# BE-012 / BE-015 阶段三实现计划

> **For Hermes:** 使用 subagent-driven-development skill 逐任务实现。

**目标:** 
- **BE-012**: 实现招标信息定时抓取任务（APScheduler），含失败告警
- **BE-015**: 增强技术案例智能匹配引擎，支持 `doc_type` 到 `case_type/scene_tags` 的精确映射

**架构:** BE-012 引入 APScheduler 定时任务框架，在 FastAPI lifespan 中管理生命周期；BE-015 在保留现有 `search_technical_cases` 基础上，增加 doc_type 映射和语义匹配层。

**技术栈:** FastAPI + APScheduler + SQLAlchemy + Alembic

---

## 当前状态

### BE-012 基础
- `Tender` 模型已存在，有 `title`, `source_url`, `publish_date`, `deadline` 等字段
- `main.py` 没有定时任务框架，`lifespan` 只做 `create_all` 和 `seed`
- 没有抓取日志/失败告警机制

### BE-015 基础
- `TechnicalCase` 模型已存在，有 `case_type`, `scene_tags`, `keywords`, `primary_review_item`, `secondary_review_item`, `score`
- `search_technical_cases` 实现为简单 SQL `contains` 匹配，仅按 `score` 排序
- `technical_document_service.py` 已在 `generate_technical_document` 中调用 `search_technical_cases`，但传入的 `keyword=doc.doc_name` 过于简单
- `proposal_plan_service.py` 也调用了 `search_technical_cases`

### 文档类型到技术案例场景的映射关系

| doc_type | 文档名 | 对应 case_type / scene_tags |
|---------|--------|------------------------------|
| `tech_overview` | 技术部分 | `项目案例`, `技术方案` |
| `tech_deviation` | 技术条款偏离表 | 不需案例 |
| `cmmi_cert` | CMMI认证证书 | `资质认证`, `CMMI` |
| `software_copyright` | 计算机软件著作权证书 | `知识产权`, `软件著作权` |
| `project_strength` | 项目实力-项目数量/金额 | `项目案例`, `同类项目`, `项目业绩` |
| `compliance_check` | 合规自查确认单 | 不需案例 |
| `service_commitment` | 服务承诺书 | `服务承诺`, `SLA` |
| `additional_content` | 其他阐述内容 | `项目案例`, `团队能力` |
| `tech_cover` | 技术部分封面 | 不需案例 |

---

## Task 1: BE-012 添加 APScheduler 依赖和配置

**目标:** 安装 APScheduler 并配置定时任务框架

**文件:**
- 修改: `backend-v2/pyproject.toml` 或 `backend-v2/requirements.txt` 添加 `apscheduler>=3.10.0`
- 创建: `backend-v2/app/core/scheduler_config.py`

**步骤 1: 添加依赖**

检查 `pyproject.toml` 是否存在，如存在则添加：
```
[project]
dependencies = [
    ...
    "apscheduler>=3.10.0",
]
```

**步骤 2: 创建配置**

```python
# backend-v2/app/core/scheduler_config.py
"""定时任务调度器配置
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED

scheduler: AsyncIOScheduler | None = None


def get_scheduler() -> AsyncIOScheduler:
    global scheduler
    if scheduler is None:
        scheduler = AsyncIOScheduler()
    return scheduler


def _on_job_event(event):
    if event.exception:
        # 记录到日志
        import logging
        logging.getLogger("apscheduler").error(
            f"定时任务执行失败: job_id={event.job_id}, exception={event.exception}"
        )


def init_scheduler():
    sched = get_scheduler()
    sched.add_listener(_on_job_event, EVENT_JOB_ERROR | EVENT_JOB_EXECUTED)
    return sched
```

**步骤 3: Commit**

```bash
git add backend-v2/app/core/scheduler_config.py backend-v2/pyproject.toml
git commit -m "chore(deps): add APScheduler for timed tender fetching tasks"
```

---

## Task 2: BE-012 创建抓取日志模型

**目标:** 创建抓取任务执行日志表，用于追踪每次抓取的状态

**文件:**
- 创建: `backend-v2/app/models/tender_fetch_log.py`

**步骤 1: 定义模型**

```python
# backend-v2/app/models/tender_fetch_log.py
from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class TenderFetchLog(Base):
    """招标信息抓取日志表"""
    __tablename__ = "tender_fetch_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # 抓取任务名称
    task_name: Mapped[str] = mapped_column(String(128), nullable=False, default="default_fetch")
    # 抓取来源（如 gov.cn, zbytb.com 等）
    source: Mapped[str] = mapped_column(String(256), nullable=False, default="")
    # 抓取状态: success / partial / failed
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="success")
    # 新增记录数
    new_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # 更新记录数
    updated_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # 错误信息
    error_message: Mapped[str] = mapped_column(Text, nullable=False, default="")
    # 开始时间
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    # 结束时间
    ended_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    def duration_seconds(self) -> float | None:
        if self.ended_at and self.started_at:
            return (self.ended_at - self.started_at).total_seconds()
        return None
```

**步骤 2: 导出模型**

确保 `backend-v2/app/models/__init__.py` 导入此模型（如果存在 `__init__.py`）。
检查 `app/models/__init__.py` 是否有导出列表，如果有则添加：
```python
from app.models.tender_fetch_log import TenderFetchLog
```

**步骤 3: Commit**

```bash
git add backend-v2/app/models/tender_fetch_log.py
git commit -m "feat(model): add TenderFetchLog model for fetch task tracking"
```

---

## Task 3: BE-012 创建抓取服务

**目标:** 实现招标信息抓取服务逻辑（基于现有 seed 机制扩展）

**文件:**
- 创建: `backend-v2/app/services/tender_fetch_service.py`

**步骤 1: 实现抓取服务**

```python
# backend-v2/app/services/tender_fetch_service.py
"""
招标信息抓取服务

当前实现为基础版本，模拟从多个来源抓取招标信息。
实际生产环境中可替换为真实的 HTTP 抓取逻辑。
"""
import logging
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


def _generate_mock_tenders(count: int = 3) -> list[dict[str, Any]]:
    """生成模拟招标数据（用于演示）"""
    import random
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

    raw_tenders = _generate_mock_tenders(count=random.randint(1, 3))

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
```

**步骤 2: Commit**

```bash
git add backend-v2/app/services/tender_fetch_service.py
git commit -m "feat(service): add tender fetch service with multi-source support and logging"
```

---

## Task 4: BE-012 集成定时任务到 FastAPI 生命周期

**目标:** 在 FastAPI lifespan 中启动/"停止 APScheduler，注册定时抓取任务

**文件:**
- 修改: `backend-v2/app/main.py`

**步骤 1: 修改 lifespan**

```python
# backend-v2/app/main.py
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.core.config import settings
from app.core.scheduler_config import init_scheduler, get_scheduler
from app.db.base import Base
from app.db.session import engine
from app.models import *  # noqa: F401, F403
from app.db.seed_tenders import seed_tenders


def _seed_tenders():
    from app.db.session import SessionLocal
    from app.models.tender import Tender
    db = SessionLocal()
    try:
        existing = db.query(Tender).first()
        if not existing:
            seed_tenders(db)
            db.commit()
    finally:
        db.close()


def _schedule_fetch_jobs():
    """注册定时抓取任务"""
    from apscheduler.triggers.interval import IntervalTrigger
    from app.services.tender_fetch_service import run_fetch_task
    from app.db.session import SessionLocal
    import logging

    logger = logging.getLogger(__name__)
    sched = get_scheduler()

    def _fetch_job():
        db = SessionLocal()
        try:
            run_fetch_task(db)
        except Exception:
            logger.exception("定时抓取任务异常")
        finally:
            db.close()

    # 每 30 分钟执行一次（可配置）
    sched.add_job(
        _fetch_job,
        trigger=IntervalTrigger(minutes=30),
        id="tender_fetch_job",
        name="招标信息定时抓取",
        replace_existing=True,
    )
    logger.info("已注册招标抓取定时任务，执行间隔: 30 分钟")


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    # Seed tender data
    _seed_tenders()

    # 启动定时任务调度器
    sched = init_scheduler()
    _schedule_fetch_jobs()
    sched.start()

    yield

    # 应用关闭时停止调度器
    sched.shutdown(wait=False)


def create_app() -> FastAPI:
    ...  # 保持不变
```

**步骤 2: Commit**

```bash
git add backend-v2/app/main.py
git commit -m "feat(scheduler): integrate APScheduler into FastAPI lifespan for tender fetching"
```

---

## Task 5: BE-012 添加抓取日志 API 和失败告警端点

**目标:** 提供抓取任务执行日志查询 API，以及失败告警提醒

**文件:**
- 创建: `backend-v2/app/schemas/tender_fetch_log.py`
- 创建: `backend-v2/app/api/v1/endpoints/tender_fetch_logs.py`
- 修改: `backend-v2/app/api/v1/router.py`

**步骤 1: Schema**

```python
# backend-v2/app/schemas/tender_fetch_log.py
from datetime import datetime
from pydantic import BaseModel


class TenderFetchLogItem(BaseModel):
    id: int
    task_name: str
    source: str
    status: str
    new_count: int
    updated_count: int
    error_message: str
    started_at: datetime
    ended_at: datetime | None

    class Config:
        from_attributes = True


class TenderFetchLogList(BaseModel):
    total: int
    items: list[TenderFetchLogItem]
```

**步骤 2: API 路由**

```python
# backend-v2/app/api/v1/endpoints/tender_fetch_logs.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.tender_fetch_log import TenderFetchLog
from app.schemas.tender_fetch_log import TenderFetchLogList, TenderFetchLogItem

router = APIRouter()


@router.get("/", response_model=TenderFetchLogList)
def list_fetch_logs(
    status: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> TenderFetchLogList:
    """获取招标抓取任务执行日志

- status: 过滤状态（success / partial / failed / running）
- 默认按执行时间倒序
"""
    query = db.query(TenderFetchLog)
    if status:
        query = query.filter(TenderFetchLog.status == status)

    total = query.count()
    items = (
        query.order_by(TenderFetchLog.started_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return TenderFetchLogList(
        total=total,
        items=[TenderFetchLogItem.model_validate(i) for i in items],
    )


@router.get("/latest-failed", response_model=TenderFetchLogItem | None)
def get_latest_failed_log(
    db: Session = Depends(get_db),
) -> TenderFetchLogItem | None:
    """获取最近一次失败的抓取任务日志（用于告警展示）"""
    log = (
        db.query(TenderFetchLog)
        .filter(TenderFetchLog.status.in_(["failed", "partial"]))
        .order_by(TenderFetchLog.started_at.desc())
        .first()
    )
    if log:
        return TenderFetchLogItem.model_validate(log)
    return None
```

**步骤 3: 注册路由**

在 `backend-v2/app/api/v1/router.py` 中添加：
```python
from app.api.v1.endpoints import ... , tender_fetch_logs

api_router.include_router(
    tender_fetch_logs.router,
    prefix="/tender-fetch-logs",
    tags=["tender-fetch-logs"],
)
```

**步骤 4: Commit**

```bash
git add backend-v2/app/schemas/tender_fetch_log.py backend-v2/app/api/v1/endpoints/tender_fetch_logs.py backend-v2/app/api/v1/router.py
git commit -m "feat(api): add tender fetch log endpoints with status filtering and latest-failed alert"
```

---

## Task 6: BE-012 Alembic 迁移

**目标:** 为 `tender_fetch_logs` 表创建 Alembic 迁移

**步骤 1: 生成迁移**

```bash
cd backend-v2
alembic revision --autogenerate -m "add tender_fetch_logs table"
```

**步骤 2: 验证**

确认迁移脚本包含：
```python
op.create_table('tender_fetch_logs', ...)
```

**步骤 3: 执行**

```bash
alembic upgrade head
```

**步骤 4: Commit**

```bash
git add alembic/versions/xxx_add_tender_fetch_logs_table.py
git commit -m "chore(db): add alembic migration for tender_fetch_logs"
```

---

## Task 7: BE-015 增强 technical_case_service 智能匹配

**目标:** 重构 `search_technical_cases`，支持基于 `doc_type` 的精确匹配

**文件:**
- 修改: `backend-v2/app/services/technical_case_service.py`

**步骤 1: 定义 doc_type 到 case 场景的映射**

```python
# 在 technical_case_service.py 顶部添加

# 技术文档类型 → 案例匹配策略映射
DOC_TYPE_CASE_MAPPING: dict[str, dict] = {
    "tech_overview": {
        "case_types": ["项目案例", "技术方案"],
        "scene_tags": ["技术方案", "系统架构", "整体解决方案"],
        "keywords": ["技术", "方案", "架构", "系统"],
    },
    "cmmi_cert": {
        "case_types": ["资质认证"],
        "scene_tags": ["CMMI", "软件能力成熟度", "资质"],
        "keywords": ["CMMI", "认证", "软件能力", "成熟度"],
    },
    "software_copyright": {
        "case_types": ["知识产权"],
        "scene_tags": ["软件著作权", "知识产权", "自主研发"],
        "keywords": ["软件著作权", "知识产权", "软著", "著作权"],
    },
    "project_strength": {
        "case_types": ["项目案例"],
        "scene_tags": ["项目业绩", "同类项目", "合同", "案例"],
        "keywords": ["项目", "案例", "合同", "业绩", "客户"],
    },
    "service_commitment": {
        "case_types": ["服务承诺", "项目案例"],
        "scene_tags": ["SLA", "服务", "维保", "响应时间"],
        "keywords": ["服务", "承诺", "SLA", "维保", "响应"],
    },
    "additional_content": {
        "case_types": ["项目案例", "技术方案"],
        "scene_tags": ["技术亮点", "创新", "团队", "核心能力"],
        "keywords": ["技术", "亮点", "创新", "团队", "能力"],
    },
}

# 不需要案例的文档类型
NO_CASE_DOC_TYPES = {"tech_deviation", "compliance_check", "tech_cover"}
```

**步骤 2: 重构 search_technical_cases**

```python
def search_technical_cases(
    db: Session,
    project_id: str,
    doc_type: str = "",
    primary_item: str = "",
    secondary_item: str = "",
    keyword: str = "",
    limit: int = 5,
) -> list[TechnicalCase]:
    """
根据文档类型和关键词智能检索技术案例

匹配优先级：
1. doc_type 映射 → case_type + scene_tags
2. primary_review_item / secondary_review_item 精确匹配
3. keyword 关键词模糊匹配
"""
    # 某些文档类型不需要技术案例
    if doc_type in NO_CASE_DOC_TYPES:
        return []

    query = db.query(TechnicalCase).filter(
        TechnicalCase.project_id == project_id,
        TechnicalCase.status == "可用",
    )

    # 策略 1: doc_type 映射匹配
    mapping = DOC_TYPE_CASE_MAPPING.get(doc_type)
    if mapping:
        # 构建 OR 条件：case_type 在列表中 或 scene_tags 包含某个标签
        from sqlalchemy import or_
        type_conditions = [
            TechnicalCase.case_type == ct
            for ct in mapping["case_types"]
        ]
        tag_conditions = [
            TechnicalCase.scene_tags.contains(tag)
            for tag in mapping["scene_tags"]
        ]
        keyword_conditions = [
            TechnicalCase.keywords.contains(kw)
            for kw in mapping["keywords"]
        ]
        query = query.filter(
            or_(
                *type_conditions,
                *tag_conditions,
                *keyword_conditions,
                TechnicalCase.title.contains(keyword) if keyword else False,
            )
        )
    else:
        # 回退到传统匹配
        if primary_item:
            query = query.filter(TechnicalCase.primary_review_item == primary_item)
        if secondary_item:
            query = query.filter(TechnicalCase.secondary_review_item == secondary_item)
        if keyword:
            query = query.filter(
                (TechnicalCase.title.contains(keyword))
                | (TechnicalCase.keywords.contains(keyword))
                | (TechnicalCase.summary.contains(keyword))
            )

    return query.order_by(TechnicalCase.score.desc()).limit(limit).all()
```

**步骤 3: Commit**

```bash
git add backend-v2/app/services/technical_case_service.py
git commit -m "feat(cases): enhance technical case search with doc_type-based smart matching"
```

---

## Task 8: BE-015 更新技术文档生成服务

**目标:** 在 `generate_technical_document` 中使用新的 `doc_type` 参数调用 `search_technical_cases`

**文件:**
- 修改: `backend-v2/app/services/technical_document_service.py`

**步骤 1: 修改案例检索调用**

在 `generate_technical_document` 函数中，将：
```python
# 旧代码
cases = search_technical_cases(db, project_id, keyword=doc.doc_name)
```

替换为：
```python
# 新代码: 基于 doc_type 智能匹配案例
cases = search_technical_cases(
    db,
    project_id=project_id,
    doc_type=doc.doc_type,
    keyword=doc.doc_name,
    limit=5,
)
```

**步骤 2: Commit**

```bash
git add backend-v2/app/services/technical_document_service.py
git commit -m "feat(tech-doc): use doc_type-aware case matching in technical document generation"
```

---

## Task 9: BE-015 更新方案建议书生成服务（同步）

**目标:** 方案建议书同样使用新的 `doc_type` 匹配

**文件:**
- 修改: `backend-v2/app/services/proposal_plan_service.py`

**步骤 1: 修改案例检索调用**

在 `generate_proposal_plan` 函数中，将：
```python
cases = search_technical_cases(db, project_id, keyword=doc.doc_name)
```

替换为：
```python
cases = search_technical_cases(
    db,
    project_id=project_id,
    doc_type=doc.doc_type,
    keyword=doc.doc_name,
    limit=5,
)
```

**步骤 2: Commit**

```bash
git add backend-v2/app/services/proposal_plan_service.py
git commit -m "feat(proposal): use doc_type-aware case matching in proposal plan generation"
```

---

## Task 10: BE-015 添加全局案例搜索支持

**目标:** 支持在项目级别搜索所有可用案例（包括跨项目的通用案例库）

**文件:**
- 修改: `backend-v2/app/services/technical_case_service.py`
- 修改: `backend-v2/app/models/technical_case.py`（如需要）

**步骤 1: 增加全局搜索参数**

```python
def search_technical_cases(
    db: Session,
    project_id: str = "",
    doc_type: str = "",
    primary_item: str = "",
    secondary_item: str = "",
    keyword: str = "",
    limit: int = 5,
    scope: str = "project",  # "project" | "global"
) -> list[TechnicalCase]:
    """
... 原有 docstring 保持不变

Args:
    scope: 搜索范围，"project"仅搜索当前项目，"global"搜索所有项目
"""
    if doc_type in NO_CASE_DOC_TYPES:
        return []

    query = db.query(TechnicalCase).filter(
        TechnicalCase.status == "可用",
    )

    if scope == "project" and project_id:
        query = query.filter(TechnicalCase.project_id == project_id)

    # ... 后续匹配逻辑保持不变
```

**步骤 2: 更新调用点**

在 `technical_document_service.py` 和 `proposal_plan_service.py` 中，可以根据配置选择 scope：
```python
cases = search_technical_cases(
    db,
    project_id=project_id,
    doc_type=doc.doc_type,
    keyword=doc.doc_name,
    limit=5,
    scope="global",  # 或从配置中读取
)
```

**步骤 3: Commit**

```bash
git add backend-v2/app/services/technical_case_service.py backend-v2/app/services/technical_document_service.py backend-v2/app/services/proposal_plan_service.py
git commit -m "feat(cases): add global scope support for cross-project case matching"
```

---

## Task 11: Smoke 测试验收

**目标:** 验证所有修改文件的语法正确性

**步骤 1: 全量语法检查**

```bash
cd backend-v2
python -m py_compile \
  app/main.py \
  app/core/scheduler_config.py \
  app/models/tender_fetch_log.py \
  app/services/tender_fetch_service.py \
  app/schemas/tender_fetch_log.py \
  app/api/v1/endpoints/tender_fetch_logs.py \
  app/api/v1/router.py \
  app/services/technical_case_service.py \
  app/services/technical_document_service.py \
  app/services/proposal_plan_service.py
```

**步骤 2: 验证路由注册**

检查 `router.py` 确保：
- `materials` 路由已注册
- `tender_fetch_logs` 路由已注册
- 没有重复前缀冲突

**步骤 3: 推送**

```bash
git push origin main
```

---

## 文件清单汇总

### 新增文件
| 文件路径 | 说明 |
|---------|------|
| `app/core/scheduler_config.py` | APScheduler 配置 |
| `app/models/tender_fetch_log.py` | 抓取日志模型 |
| `app/services/tender_fetch_service.py` | 抓取业务逻辑 |
| `app/schemas/tender_fetch_log.py` | 抓取日志 Schema |
| `app/api/v1/endpoints/tender_fetch_logs.py` | 抓取日志 API |

### 修改文件
| 文件路径 | 说明 |
|---------|------|
| `app/main.py` | 启动定时任务调度器 |
| `app/api/v1/router.py` | 注册 tender_fetch_logs 路由 |
| `app/services/technical_case_service.py` | 智能案例匹配引擎 |
| `app/services/technical_document_service.py` | 使用新案例匹配 |
| `app/services/proposal_plan_service.py` | 使用新案例匹配 |
| `pyproject.toml` 或 `requirements.txt` | 添加 APScheduler 依赖 |
| `alembic/versions/*.py` | 新增 tender_fetch_logs 迁移 |

---

## 验收标准

### BE-012 验收
- [ ] `GET /api/v1/tender-fetch-logs/` 返回抓取日志列表
- [ ] `GET /api/v1/tender-fetch-logs/latest-failed` 返回最近失败日志
- [ ] FastAPI 启动时 APScheduler 正常启动
- [ ] 每 30 分钟自动执行抓取任务（模拟数据）
- [ ] 抓取失败时日志正确记录
- [ ] Alembic 迁移正常执行

### BE-015 验收
- [ ] `search_technical_cases` 支持 `doc_type` 参数
- [ ] 不同 `doc_type` 返回不同类型的案例（CMMI、软著、项目案例等）
- [ ] `技术条款偏离表`、`合规自查确认单`、`技术部分封面` 不返回案例
- [ ] `generate_technical_document` 正确传递 `doc_type`
- [ ] `generate_proposal_plan` 正确传递 `doc_type`
