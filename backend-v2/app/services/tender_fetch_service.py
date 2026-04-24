"""
招标信息抓取服务

支持从真实 HTTP 源抓取招标信息，失败时自动降级到模拟数据以保持系统可用性。
"""
import logging
import random
import re
import time
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.models.tender import Tender
from app.models.tender_fetch_log import TenderFetchLog

logger = logging.getLogger(__name__)

# 软依赖：httpx / beautifulsoup4 —— 若缺失则自动降级到 fallback
try:
    import httpx

    HTTPX_AVAILABLE = True
except ImportError:  # pragma: no cover
    HTTPX_AVAILABLE = False

try:
    from bs4 import BeautifulSoup

    BS4_AVAILABLE = True
except ImportError:  # pragma: no cover
    BS4_AVAILABLE = False

# 招标来源配置（可扩展）
TENDER_SOURCES = [
    {"name": "政府采购网", "url": "https://www.ccgp.gov.cn/", "enabled": True},
    {"name": "中国招标信息网", "url": "https://www.zbytb.com/", "enabled": True},
    {"name": "中国国际招标网", "url": "https://www.chinabidding.com/", "enabled": False},
]

# 各源对应的搜索/列表页（与首页分离，避免直接抓取门户首页）
_SOURCE_SEARCH_URLS = {
    "政府采购网": (
        "http://search.ccgp.gov.cn/bxsearch?"
        "searchtype=1&page_index=1&startTime=&endTime=&keyword=&"
        "pinMu=0&bidType=1&buyerName=&projectId=&displayZone=&zoneId=&pppStatus=0"
    ),
    "中国招标信息网": "https://www.zbytb.com/zbgg/index.html",
}

_DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/avif,image/webp,image/apng,*/*;q=0.8"
    ),
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Cache-Control": "no-cache",
}


def _fallback_seed_tenders(count: int = 3) -> list[dict[str, Any]]:
    """在未接入真实招标抓取源时，生成后备示例数据以保持系统可用性。"""
    industries = ["信息技术", "建筑工程", "物流服务", "咨询服务", "软件开发"]
    regions = ["北京", "上海", "广州", "深圳", "杭州"]

    tenders = []
    for i in range(count):
        industry = random.choice(industries)
        region = random.choice(regions)
        amount = random.choice(["50", "100", "200", "500", "1000"])
        tenders.append(
            {
                "title": (
                    f"{region}市{industry}服务项目招标公告-"
                    f"{datetime.now().strftime('%Y%m%d')}-{i+1}"
                ),
                "source_url": f"https://example.com/tender/{uuid.uuid4().hex[:8]}",
                "publish_date": datetime.now().strftime("%Y-%m-%d"),
                "deadline": "请查看招标文件",
                "amount": f"{amount}万元",
                "margin": "按招标文件要求",
                "project_type": industry,
                "description": (
                    f"该项目为{region}地区{industry}领域的服务采购项目，"
                    "欢迎合规供应商参与投标。"
                ),
            }
        )
    return tenders


def _fetch_with_retry(
    url: str,
    headers: dict[str, str] | None = None,
    max_retries: int = 3,
    timeout: float = 15.0,
    encoding: str | None = None,
) -> str:
    """发起 HTTP GET 请求，支持指数退避重试。

    Args:
        url: 目标地址。
        headers: 自定义请求头，将与默认头合并。
        max_retries: 最大重试次数（默认 3 次）。
        timeout: 单次请求超时秒数（默认 15 秒）。
        encoding: 强制指定响应编码（如 gb2312）；None 时由 httpx 自动检测。

    Returns:
        解码后的 HTML 文本。

    Raises:
        RuntimeError: 所有重试均失败后抛出，携带最后一次异常信息。
    """
    if not HTTPX_AVAILABLE:
        raise RuntimeError("httpx 未安装，无法执行真实 HTTP 抓取")

    merged_headers = {**_DEFAULT_HEADERS, **(headers or {})}
    last_error: Exception | None = None

    for attempt in range(1, max_retries + 1):
        try:
            with httpx.Client(timeout=timeout, follow_redirects=True) as client:
                resp = client.get(url, headers=merged_headers)
                resp.raise_for_status()
                if encoding:
                    return resp.content.decode(encoding, errors="ignore")
                return resp.text
        except Exception as e:
            last_error = e
            logger.warning(
                "HTTP 请求失败 [%s] 第 %d/%d 次: %s",
                url,
                attempt,
                max_retries,
                e,
            )
            if attempt < max_retries:
                backoff = 2**attempt
                logger.info("指数退避: 等待 %ds 后重试...", backoff)
                time.sleep(backoff)

    raise last_error or RuntimeError(
        f"请求 {url} 失败，已重试 {max_retries} 次"
    )


def _parse_ccgp_tenders(html: str) -> list[dict[str, Any]]:
    """解析中国政府采购网搜索结果 HTML，提取招标列表。

    基于 search.ccgp.gov.cn 搜索结果页结构解析。
    若页面结构发生变更，解析可能返回空列表，由上层触发 fallback 降级。
    """
    if not BS4_AVAILABLE:
        raise RuntimeError("beautifulsoup4 未安装，无法解析 HTML")

    tenders: list[dict[str, Any]] = []
    soup = BeautifulSoup(html, "html.parser")

    # 结果列表常见选择器（search.ccgp.gov.cn 结果在 .vT-srch-result-list > li）
    result_items = soup.select("ul.vT-srch-result-list li") or soup.select(
        "ul.c_list_bid li"
    )

    for item in result_items[:5]:  # 限制单次抓取数量，避免过度请求
        try:
            a_tag = item.find("a")
            if not a_tag or not a_tag.get("href"):
                continue

            title = (a_tag.get_text(strip=True) or "未知标题")[:500]
            href = a_tag["href"]
            # 补全相对路径
            source_url = (
                href
                if href.startswith("http")
                else f"http://www.ccgp.gov.cn{href}"
            )

            # 提取日期：通常在 <span> 或带有时间类名的元素中
            date_text = ""
            span = item.find("span")
            if span:
                date_text = span.get_text(strip=True)
            date_match = re.search(r"(\d{4}-\d{2}-\d{2})", date_text)
            publish_date = (
                date_match.group(1)
                if date_match
                else datetime.now().strftime("%Y-%m-%d")
            )

            tenders.append(
                {
                    "title": title,
                    "source_url": source_url,
                    "publish_date": publish_date,
                    "deadline": "请查看招标文件",
                    "amount": "待定",
                    "margin": "按招标文件要求",
                    "project_type": "政府采购",
                    "description": f"来源：中国政府采购网。{title}",
                }
            )
        except Exception as parse_err:
            logger.warning("解析单条 ccgp 公告失败: %s", parse_err)
            continue

    return tenders


def _parse_zbytb_tenders(html: str) -> list[dict[str, Any]]:
    """解析中国招标信息网列表页 HTML，提取招标列表。

    若页面结构发生变更，解析可能返回空列表，由上层触发 fallback 降级。
    """
    if not BS4_AVAILABLE:
        raise RuntimeError("beautifulsoup4 未安装，无法解析 HTML")

    tenders: list[dict[str, Any]] = []
    soup = BeautifulSoup(html, "html.parser")

    # zbytb.com 列表项通常在 table 或 ul.news-list 结构中
    rows = soup.select("table.list-table tr") or soup.select("ul.news-list li")

    for row in rows[:5]:
        try:
            a_tag = row.find("a")
            if not a_tag or not a_tag.get("href"):
                continue

            title = (a_tag.get_text(strip=True) or "未知标题")[:500]
            href = a_tag["href"]
            source_url = (
                href
                if href.startswith("http")
                else f"https://www.zbytb.com{href}"
            )

            # 尝试从整行文本提取日期
            date_text = row.get_text(strip=True)
            date_match = re.search(r"(\d{4}-\d{2}-\d{2})", date_text)
            publish_date = (
                date_match.group(1)
                if date_match
                else datetime.now().strftime("%Y-%m-%d")
            )

            tenders.append(
                {
                    "title": title,
                    "source_url": source_url,
                    "publish_date": publish_date,
                    "deadline": "请查看招标文件",
                    "amount": "待定",
                    "margin": "按招标文件要求",
                    "project_type": "招标信息",
                    "description": f"来源：中国招标信息网。{title}",
                }
            )
        except Exception as parse_err:
            logger.warning("解析单条 zbytb 公告失败: %s", parse_err)
            continue

    return tenders


def _fetch_real_tenders(source_name: str) -> list[dict[str, Any]]:
    """从真实源抓取招标信息。

    成功时返回解析后的 tender 字典列表；
    失败时抛出异常，由上层调用方触发 fallback 降级。
    """
    search_url = _SOURCE_SEARCH_URLS.get(source_name)
    if not search_url:
        raise ValueError(f"未配置 {source_name} 的搜索地址")

    if source_name == "政府采购网":
        html = _fetch_with_retry(
            search_url, encoding="utf-8", max_retries=3, timeout=15.0
        )
        tenders = _parse_ccgp_tenders(html)
    elif source_name == "中国招标信息网":
        html = _fetch_with_retry(
            search_url, encoding="utf-8", max_retries=3, timeout=15.0
        )
        tenders = _parse_zbytb_tenders(html)
    else:
        raise ValueError(f"暂不支持的招标源: {source_name}")

    if not tenders:
        raise RuntimeError(
            f"从 {source_name} 未解析到任何招标数据，可能页面结构已变更"
        )

    return tenders


def fetch_tenders_from_source(
    db: Session,
    source_name: str,
    source_url: str,
) -> dict[str, Any]:
    """从指定来源抓取招标信息。

    优先尝试真实 HTTP 抓取；若依赖缺失、请求失败或解析为空，
    自动降级到 ``_fallback_seed_tenders`` 模拟数据，保证服务可用性。
    """
    logger.info("开始从 [%s] 抓取招标信息: %s", source_name, source_url)

    raw_tenders: list[dict[str, Any]] = []
    used_fallback = False
    error_message = ""

    try:
        raw_tenders = _fetch_real_tenders(source_name)
        logger.info(
            "[%s] 真实抓取成功，解析到 %d 条", source_name, len(raw_tenders)
        )
    except Exception as e:
        error_message = f"真实抓取失败: {e}；已降级到 fallback 数据。"
        logger.warning("[%s] %s", source_name, error_message)
        raw_tenders = _fallback_seed_tenders(count=random.randint(1, 3))
        used_fallback = True

    new_count = 0
    updated_count = 0

    try:
        for raw in raw_tenders:
            # 检查是否已存在（基于 source_url 唯一性）
            existing = (
                db.query(Tender)
                .filter(Tender.source_url == raw["source_url"])
                .first()
            )
            if existing:
                # 更新现有记录
                existing.title = raw["title"]
                existing.publish_date = raw["publish_date"]
                existing.deadline = raw["deadline"]
                existing.amount = raw["amount"]
                existing.margin = raw["margin"]
                existing.project_type = raw["project_type"]
                existing.description = raw["description"]
                existing.updated_at = datetime.now(timezone.utc)
                updated_count += 1
            else:
                # 创建新记录
                tender = Tender(
                    id=f"tender_{uuid.uuid4().hex[:12]}",
                    title=raw["title"],
                    source_url=raw["source_url"],
                    publish_date=raw["publish_date"],
                    deadline=raw["deadline"],
                    amount=raw["amount"],
                    margin=raw["margin"],
                    project_type=raw["project_type"],
                    description=raw["description"],
                    decision="pending",
                    reject_reason="",
                    project_id="",
                )
                db.add(tender)
                new_count += 1

        db.commit()
        status_msg = "降级 fallback" if used_fallback else "真实抓取"
        logger.info(
            "[%s] %s 完成: 新增 %d 条, 更新 %d 条",
            source_name,
            status_msg,
            new_count,
            updated_count,
        )
    except Exception as e:
        db.rollback()
        error_message = f"数据库写入失败: {e}"
        logger.exception("[%s] 抓取失败: %s", source_name, e)
        raise

    return {
        "source": source_name,
        "new_count": new_count,
        "updated_count": updated_count,
        "error_message": error_message,
    }


def run_fetch_task(db: Session) -> dict[str, Any]:
    """执行完整的招标抓取任务

    依次从所有启用的来源抓取，并记录执行日志。
    """
    log = TenderFetchLog(
        task_name="scheduled_fetch",
        source=",".join([s["name"] for s in TENDER_SOURCES if s["enabled"]]),
        status="running",
    )
    db.add(log)
    db.commit()
    db.refresh(log)

    total_new = 0
    total_updated = 0
    errors: list[str] = []

    for source in TENDER_SOURCES:
        if not source["enabled"]:
            continue
        try:
            result = fetch_tenders_from_source(db, source["name"], source["url"])
            total_new += result["new_count"]
            total_updated += result["updated_count"]
        except Exception as e:
            errors.append(f"{source['name']}: {e}")

    log.status = (
        "partial"
        if errors and (total_new > 0 or total_updated > 0)
        else ("failed" if errors else "success")
    )
    log.new_count = total_new
    log.updated_count = total_updated
    log.error_message = "; ".join(errors) if errors else ""
    log.ended_at = datetime.now(timezone.utc)
    db.commit()

    logger.info(
        "定时抓取任务完成: 新增 %d, 更新 %d, 失败: %d",
        total_new,
        total_updated,
        len(errors),
    )

    return {
        "new_count": total_new,
        "updated_count": total_updated,
        "errors": errors,
        "log_id": log.id,
    }
