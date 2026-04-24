"""
招标信息抓取服务

当前实现为基础版本，模拟从多个来源抓取招标信息。
实际生产环境中可替换为真实的 HTTP 抓取逻辑。
"""
import logging
import random
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.models.tender import Tender
from app.models.tender_fetch_log import TenderFetchLog

logger = logging.getLogger(__name__)

# 招标来源配置（可扩展）
TENDER_SOURCES = [
    {"name": "政府采购网", "url": "https://www.ccgp.gov.cn/", "enabled": True},
    {"name": "中国招标信息网", "url": "https://www.zbytb.com/", "enabled": True},
    {"name": "中国国际招标网", "url": "https://www.chinabidding.com/", "enabled": False},
]


def _fallback_seed_tenders(count: int = 3) -> list[dict[str, Any]]:
    """在未接入真实招标抓取源时，生成后备示例数据以保持系统可用性。"""
    industries = ["信息技术", "建筑工程", "物流服务", "咨询服务", "软件开发"]
    regions = ["北京", "上海", "广州", "深圳", "杭州"]

    tenders = []
    for i in range(count):
        industry = random.choice(industries)
        region = random.choice(regions)
        amount = random.choice(["50", "100", "200", "500", "1000"])
        tenders.append({
            "title": f"{region}市{industry}服务项目招标公告-{datetime.now().strftime('%Y%m%d')}-{i+1}",
            "source_url": f"https://example.com/tender/{uuid.uuid4().hex[:8]}",
            "publish_date": datetime.now().strftime("%Y-%m-%d"),
            "deadline": "请查看招标文件",
            "amount": f"{amount}万元",
            "margin": "按招标文件要求",
            "project_type": industry,
            "description": f"该项目为{region}地区{industry}领域的服务采购项目，欢迎合规供应商参与投标。",
        })
    return tenders


def fetch_tenders_from_source(
    db: Session,
    source_name: str,
    source_url: str,
) -> dict[str, Any]:
    """
    从指定来源抓取招标信息

    当前为模拟实现，生成测试数据。生产环境中应替换为真实的 HTTP 请求。
    """
    logger.info(f"开始从 [{source_name}] 抓取招标信息: {source_url}")

    # TODO: 生产环境中替换为真实的 HTTP 抓取逻辑
    # 示例:
    # response = requests.get(source_url, timeout=30)
    # data = parse_tender_list(response.text)

    raw_tenders = _fallback_seed_tenders(count=random.randint(1, 3))

    new_count = 0
    updated_count = 0
    error_message = ""

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
        logger.info(
            f"[{source_name}] 抓取完成: 新增 {new_count} 条, 更新 {updated_count} 条"
        )
    except Exception as e:
        db.rollback()
        error_message = str(e)
        logger.exception(f"[{source_name}] 抓取失败: {e}")
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

    log.status = "partial" if errors and (total_new > 0 or total_updated > 0) else ("failed" if errors else "success")
    log.new_count = total_new
    log.updated_count = total_updated
    log.error_message = "; ".join(errors) if errors else ""
    log.ended_at = datetime.now(timezone.utc)
    db.commit()

    logger.info(
        f"定时抓取任务完成: 新增 {total_new}, 更新 {total_updated}, 失败: {len(errors)}"
    )

    return {
        "new_count": total_new,
        "updated_count": total_updated,
        "errors": errors,
        "log_id": log.id,
    }
