# BE-013 / BE-014 打分引擎与素材库自动匹配 实现计划

> **For Hermes:** 使用 subagent-driven-development skill 逐任务实现。

**目标:** 实现基于 LLM 语义分析的打分计算引擎（支持二次重算），以及素材库自动匹配闭环。

**架构:** 打分引擎在保留启发式 fallback 的基础上，增加 LLM 语义评估维度；素材匹配扩展 Material 模型并增强 asset_routing_service 的分类匹配能力。

**技术栈:** FastAPI + SQLAlchemy + Alembic + OpenAI/Anthropic LLM Client

---

## 前置信息

### 现有文件清单

| 文件 | 说明 | 修改方式 |
|------|------|----------|
| `backend-v2/app/services/scoring_service.py` | 现有启发式打分 | 重构增强 |
| `backend-v2/app/services/llm_client.py` | LLM 客户端 | 新增打分方法 |
| `backend-v2/app/services/asset_routing_service.py` | 素材路由 | 增强匹配 |
| `backend-v2/app/models/settings.py` | Material 模型 | 扩展字段 |
| `backend-v2/app/schemas/business_document.py` | 商务文档 schema | 扩展 score response |
| `backend-v2/app/schemas/technical_document.py` | 技术文档 schema | 扩展 score response |
| `backend-v2/app/schemas/proposal_plan.py` | 方案建议书 schema | 扩展 score response |
| `backend-v2/app/api/v1/endpoints/business_document.py` | 商务 API | 已有 /score |
| `backend-v2/app/api/v1/endpoints/technical_document.py` | 技术 API | 已有 /score |
| `backend-v2/app/api/v1/endpoints/proposal_plan.py` | 方案 API | **新增 /score** |
| `backend-v2/app/api/v1/endpoints/settings.py` | 设置 API | **新增 Material CRUD** |
| `backend-v2/app/api/v1/router.py` | 路由注册 | 注册 Material 路由 |

### 现有打分逻辑（scoring_service.py）

- `_parse_max_score`: 从 `score_point` 字符串提取分值
- `_count_placeholders`: 统计占位符数量
- `_rule_match_score`: 基于规则关键词匹配（精确包含判断）
- `calculate_score`: 加权总分 = max_score × (completeness×0.6 + rule_match×0.4)

### 现有 LLM Client 结构（llm_client.py）

- `_BaseLLMClient`: 基础聊天封装
- `LLMGenerationClient`: 文档生成（`generate_document_content`）
- `LLMReviewClient`: 合同审查
- `LLMDecisionClient`: 投标决策（`evaluate_project`）
- `LLMProposalClient`: 方案生成
- `LLMPreEvaluationClient`: 预评估

---

## BE-013: 打分计算引擎

### Task 1: 扩展 DocumentScoreResponse Schema

**目标:** 为三个文档类型的 score response 增加 LLM 语义评分维度和素材覆盖度。

**文件:**
- Modify: `backend-v2/app/schemas/business_document.py`
- Modify: `backend-v2/app/schemas/technical_document.py`
- Modify: `backend-v2/app/schemas/proposal_plan.py`

**Step 1: 重写 DocumentScoreResponse**

```python
class ScoreBreakdown(BaseModel):
    completeness: float = Field(description="内容完整度 0-1")
    rule_match: float = Field(description="规则匹配度 0-1")
    semantic_quality: float = Field(description="语义质量 0-1 (LLM评估)")
    asset_coverage: float = Field(description="素材覆盖度 0-1")
    placeholder_count: int = Field(description="占位符数量")
    missing_keywords: list[str] = Field(default_factory=list, description="缺失关键词")
    llm_reasoning: str = Field(default="", description="LLM评分理由")


class DocumentScoreResponse(BaseModel):
    score: float = Field(description="当前得分")
    max_score: float = Field(description="满分")
    is_scored: bool = Field(description="是否已计分")
    breakdown: ScoreBreakdown = Field(description="评分明细")
    previous_score: float | None = Field(default=None, description="上次得分（用于对比）")
    score_delta: float | None = Field(default=None, description="得分变化")
    message: str | None = Field(default=None, description="提示信息")
```

**Step 2: 验证导入**

Run: `cd backend-v2 && python -c "from app.schemas.business_document import DocumentScoreResponse; print('OK')"`
Expected: OK

**Step 3: Commit**

```bash
git add backend-v2/app/schemas/
git commit -m "feat(scoring): extend DocumentScoreResponse with semantic quality and asset coverage breakdowns"
```

---

### Task 2: 在 LLM Client 新增打分方法

**目标:** 创建 `LLMScoringClient`，让 LLM 根据评分规则语义评估文档内容。

**文件:**
- Modify: `backend-v2/app/services/llm_client.py`

**Step 1: 在 `LLMProposalClient` 之后新增 `LLMScoringClient` 类**

位置：在 `llm_client.py` 中 `LLMProposalClient` 类结束后的空行处。

```python
class LLMScoringClient(_BaseLLMClient):
    """LLM client for semantic document scoring."""

    def score_document(
        self,
        *,
        doc_name: str,
        score_point: str,
        rule_description: str,
        content: str,
        routed_assets: list[str],
    ) -> dict[str, Any]:
        """
        Ask LLM to evaluate document content against scoring rules.
        Returns dict with keys: semantic_quality (0-1), asset_coverage (0-1), reasoning (str), suggestions (list[str]).
        """
        if not self.is_llm_ready:
            return {
                "semantic_quality": 0.0,
                "asset_coverage": 0.0,
                "reasoning": "LLM 未配置，跳过语义评分",
                "suggestions": [],
            }

        system_prompt = (
            "你是资深招投标评标专家。请根据评分规则和素材覆盖情况，"
            "对投标文件内容进行客观评估。评分必须严格基于规则描述，"
            "不得编造或臆测。输出必须是 JSON 对象。"
        )

        user_prompt = (
            f"文档名称:{doc_name}\n"
            f"评分点:{score_point}\n"
            f"评分规则:{rule_description}\n\n"
            f"已匹配素材清单:{json.dumps(routed_assets, ensure_ascii=False)}\n\n"
            f"文档内容（前8000字符）:{content[:8000]}\n\n"
            "请评估以下内容并返回 JSON:\n"
            "{\n"
            '  "semantic_quality": 0.0~1.0,  // 内容是否满足评分规则要求\n'
            '  "asset_coverage": 0.0~1.0,    // 素材是否在内容中被充分引用\n'
            '  "reasoning": "评分理由...",    // 100字以内的评分理由\n'
            '  "suggestions": ["建议1", "建议2"] // 改进建议列表\n'
            "}"
        )

        try:
            content = self._chat_completion(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.2,
                max_tokens=2048,
            )
            content = (content or "").strip()
            if not content:
                return {
                    "semantic_quality": 0.0,
                    "asset_coverage": 0.0,
                    "reasoning": "LLM 返回空内容",
                    "suggestions": [],
                }
            payload = self._parse_json_payload(content)
            return {
                "semantic_quality": float(payload.get("semantic_quality", 0)),
                "asset_coverage": float(payload.get("asset_coverage", 0)),
                "reasoning": str(payload.get("reasoning", "")),
                "suggestions": payload.get("suggestions", []) or [],
            }
        except Exception as exc:
            logger.warning("LLM scoring failed: %s", exc)
            return {
                "semantic_quality": 0.0,
                "asset_coverage": 0.0,
                "reasoning": f"LLM 评分失败: {exc}",
                "suggestions": [],
            }
```

**Step 2: 在文件末尾导出实例**

在 `llm_generation_client = LLMGenerationClient()` 附近（如果有其他实例化代码），新增：

```python
llm_scoring_client = LLMScoringClient()
```

**Step 3: 验证**

Run: `cd backend-v2 && python -c "from app.services.llm_client import LLMScoringClient; print('OK')"`
Expected: OK

**Step 4: Commit**

```bash
git add backend-v2/app/services/llm_client.py
git commit -m "feat(scoring): add LLMScoringClient for semantic document evaluation"
```

---

### Task 3: 重构 scoring_service.py — 核心引擎升级

**目标:** 保留启发式 fallback，增加 LLM 语义评分、素材覆盖度、打分历史。

**文件:**
- Modify: `backend-v2/app/services/scoring_service.py`
- Create: `backend-v2/app/models/document_score_history.py`

**Step 1: 新建打分历史模型**

Create: `backend-v2/app/models/document_score_history.py`

```python
from datetime import datetime, timezone
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class DocumentScoreHistory(Base):
    __tablename__ = "document_score_histories"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    project_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    doc_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    doc_kind: Mapped[str] = mapped_column(String(32), nullable=False)  # business / technical / proposal
    score: Mapped[float] = mapped_column(Float, nullable=False)
    max_score: Mapped[float] = mapped_column(Float, nullable=False)
    breakdown: Mapped[str] = mapped_column(Text, nullable=False, default="{}")  # JSON
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
```

**Step 2: 在 `backend-v2/app/models/__init__.py` 中导入新模型**

如果 `__init__.py` 导入了所有模型，追加：
```python
from app.models.document_score_history import DocumentScoreHistory
```

**Step 3: 重写 scoring_service.py**

完整替换 `scoring_service.py` 内容：

```python
"""Scoring service: auto-calculate document scores with LLM semantic evaluation."""

import json
import re
import uuid
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.business_document import BusinessDocument
from app.models.technical_document import TechnicalDocument
from app.models.proposal_plan import ProposalPlan
from app.models.document_score_history import DocumentScoreHistory
from app.services.llm_client import llm_scoring_client


_PLACEHOLDER_PATTERNS = [
    re.compile(r"_{3,}"),
    re.compile(r"\[【[^】]*】"),
    re.compile(r"请填写"),
    re.compile(r"请描述"),
    re.compile(r"请详细描述"),
    re.compile(r"请列出"),
    re.compile(r"\{\{[^}]*\}\}"),
    re.compile(r"<[^>]+>"),
]


def _parse_max_score(score_point: str | None) -> float:
    if not score_point:
        return 0.0
    m = re.search(r"(\d+(?:\.\d+)?)\s*分", score_point)
    if m:
        return float(m.group(1))
    m = re.search(r"(\d+(?:\.\d+)?)", score_point)
    if m:
        return float(m.group(1))
    return 0.0


def _count_placeholders(content: str) -> int:
    total = 0
    for pat in _PLACEHOLDER_PATTERNS:
        total += len(pat.findall(content))
    return total


def _rule_match_score(rule_description: str | None, content: str) -> tuple[float, list[str]]:
    if not rule_description:
        return 1.0, []

    keywords: list[str] = []
    for line in rule_description.splitlines():
        line = line.strip()
        if not line:
            continue
        cleaned = re.sub(r"^[①-⑿\d]+[\.\)）\s]+", "", line)
        cleaned = re.split(r"[，,。；;]", cleaned)[0]
        if 4 <= len(cleaned) <= 30:
            keywords.append(cleaned)

    if not keywords:
        return 1.0, []

    matched = []
    missing = []
    for kw in keywords:
        if kw in content or any(part in content for part in kw.split() if len(part) >= 4):
            matched.append(kw)
        else:
            missing.append(kw)

    score = len(matched) / len(keywords) if keywords else 1.0
    return score, missing


def _get_document(db: Session, project_id: str, doc_id: str, doc_kind: str):
    if doc_kind == "business":
        return db.query(BusinessDocument).filter(
            BusinessDocument.id == doc_id,
            BusinessDocument.project_id == project_id,
        ).first()
    elif doc_kind == "technical":
        return db.query(TechnicalDocument).filter(
            TechnicalDocument.id == doc_id,
            TechnicalDocument.project_id == project_id,
        ).first()
    elif doc_kind == "proposal":
        return db.query(ProposalPlan).filter(
            ProposalPlan.id == doc_id,
            ProposalPlan.project_id == project_id,
        ).first()
    return None


def _get_previous_score(db: Session, project_id: str, doc_id: str, doc_kind: str) -> float | None:
    last = (
        db.query(DocumentScoreHistory)
        .filter(
            DocumentScoreHistory.project_id == project_id,
            DocumentScoreHistory.doc_id == doc_id,
            DocumentScoreHistory.doc_kind == doc_kind,
        )
        .order_by(DocumentScoreHistory.created_at.desc())
        .first()
    )
    return last.score if last else None


def _save_score_history(
    db: Session,
    project_id: str,
    doc_id: str,
    doc_kind: str,
    score: float,
    max_score: float,
    breakdown: dict[str, Any],
) -> None:
    history = DocumentScoreHistory(
        id=str(uuid.uuid4()),
        project_id=project_id,
        doc_id=doc_id,
        doc_kind=doc_kind,
        score=score,
        max_score=max_score,
        breakdown=json.dumps(breakdown, ensure_ascii=False),
    )
    db.add(history)
    db.commit()


def calculate_score(
    db: Session,
    project_id: str,
    doc_id: str,
    doc_kind: str,
    *,
    use_llm: bool = True,
    routed_assets: list[str] | None = None,
) -> dict[str, Any]:
    doc = _get_document(db, project_id, doc_id, doc_kind)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在")

    content = doc.editable_content or doc.original_content or ""
    max_score = _parse_max_score(doc.score_point)

    if max_score <= 0:
        return {
            "score": 0,
            "max_score": 0,
            "is_scored": False,
            "breakdown": {
                "completeness": 0,
                "rule_match": 0,
                "semantic_quality": 0,
                "asset_coverage": 0,
                "placeholder_count": _count_placeholders(content),
                "missing_keywords": [],
                "llm_reasoning": "",
            },
            "previous_score": None,
            "score_delta": None,
            "message": "该文档未设置评分分值，无法计算得分",
        }

    # 1. Completeness heuristic
    placeholder_count = _count_placeholders(content)
    content_length = len(content.strip())
    base_length = max(len(doc.original_content or ""), 100)

    if placeholder_count == 0 and content_length > base_length * 0.5:
        completeness = 1.0
    else:
        completeness = max(0.0, 1.0 - (placeholder_count / 10.0))

    # 2. Rule match heuristic
    rule_match, missing_keywords = _rule_match_score(doc.rule_description, content)

    # 3. LLM semantic scoring
    semantic_quality = 0.0
    asset_coverage = 0.0
    llm_reasoning = "LLM 未配置"
    if use_llm and llm_scoring_client.is_llm_ready:
        llm_result = llm_scoring_client.score_document(
            doc_name=doc.doc_name,
            score_point=doc.score_point,
            rule_description=doc.rule_description,
            content=content,
            routed_assets=routed_assets or [],
        )
        semantic_quality = llm_result["semantic_quality"]
        asset_coverage = llm_result["asset_coverage"]
        llm_reasoning = llm_result["reasoning"]

    # 4. Weighted total: completeness 30% + rule_match 20% + semantic_quality 35% + asset_coverage 15%
    score = max_score * (
        completeness * 0.30 +
        rule_match * 0.20 +
        semantic_quality * 0.35 +
        asset_coverage * 0.15
    )
    score = round(score, 2)

    previous_score = _get_previous_score(db, project_id, doc_id, doc_kind)
    score_delta = round(score - previous_score, 2) if previous_score is not None else None

    breakdown = {
        "completeness": round(completeness, 2),
        "rule_match": round(rule_match, 2),
        "semantic_quality": round(semantic_quality, 2),
        "asset_coverage": round(asset_coverage, 2),
        "placeholder_count": placeholder_count,
        "missing_keywords": missing_keywords,
        "llm_reasoning": llm_reasoning,
    }

    # Save history
    _save_score_history(db, project_id, doc_id, doc_kind, score, max_score, breakdown)

    return {
        "score": score,
        "max_score": max_score,
        "is_scored": True,
        "breakdown": breakdown,
        "previous_score": previous_score,
        "score_delta": score_delta,
        "message": None,
    }
```

**Step 4: 验证导入**

Run: `cd backend-v2 && python -c "from app.services.scoring_service import calculate_score; print('OK')"`
Expected: OK

**Step 5: Commit**

```bash
git add backend-v2/app/services/scoring_service.py backend-v2/app/models/document_score_history.py
git commit -m "feat(scoring): refactor scoring engine with LLM semantic quality and asset coverage"
```

---

### Task 4: 为 proposal_plan 添加 /score 路由

**目标:** 补齐方案建议书的打分 API。

**文件:**
- Modify: `backend-v2/app/api/v1/endpoints/proposal_plan.py`
- Modify: `backend-v2/app/schemas/proposal_plan.py`（添加 DocumentScoreResponse 导入）

**Step 1: 在 `proposal_plan.py` 顶部导入**

```python
from app.services.scoring_service import calculate_score
```

并在 schema import 中追加 `DocumentScoreResponse`。

**Step 2: 在文件末尾添加路由**

```python
@router.get("/{project_id}/proposal-plans/{doc_id}/score", response_model=DocumentScoreResponse)
def score_proposal_plan(
    project_id: str,
    doc_id: str,
    db: Session = Depends(get_db),
) -> DocumentScoreResponse:
    """计算方案建议书评分"""
    return DocumentScoreResponse(**calculate_score(db, project_id, doc_id, doc_kind="proposal"))
```

**Step 3: 验证**

Run: `cd backend-v2 && python -c "from app.api.v1.endpoints.proposal_plan import router; print('OK')"`
Expected: OK

**Step 4: Commit**

```bash
git add backend-v2/app/api/v1/endpoints/proposal_plan.py
git commit -m "feat(api): add /score endpoint for proposal plans"
```

---

### Task 5: 生成 Alembic 迁移（document_score_history 表）

**目标:** 为新模型创建数据库迁移。

**文件:**
- Create: `backend-v2/alembic/versions/xxxx_add_document_score_history.py`

**Step 1: 生成迁移**

Run:
```bash
cd backend-v2
alembic revision --autogenerate -m "add document_score_history table"
```

**Step 2: 检查生成的迁移文件**

确保包含 `document_score_histories` 表的创建，字段正确。

**Step 3: 验证升级**

Run: `alembic upgrade head`
Expected: 成功，无报错

**Step 4: Commit**

```bash
git add backend-v2/alembic/versions/
git commit -m "chore(db): add alembic migration for document_score_history"
```

---

## BE-014: 素材库自动匹配

### Task 6: 扩展 Material 模型

**目标:** 为素材增加内容、标签、分类、元数据等字段。

**文件:**
- Modify: `backend-v2/app/models/settings.py`

**Step 1: 重写 Material 模型**

将现有的 `Material` 替换为：

```python
class Material(Base):
    __tablename__ = "materials"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    # 素材分类: cmmi / soft_copy / project_experience / personnel_capability / certificate / other
    category: Mapped[str] = mapped_column(String(64), nullable=False, default="other")
    # 细分类标签，JSON 数组
    tags: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    # 素材文本内容（用于匹配和填充）
    content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    # 原始文件路径
    file_path: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    # 素材描述
    description: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    # 关联公司/组织
    organization: Mapped[str] = mapped_column(String(256), nullable=False, default="")
    # 获取日期
    acquired_date: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    # 有效期至
    valid_until: Mapped[str] = mapped_column(String(32), nullable=False, default="")
    # 是否激活
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    # 元数据（额外字段）
    metadata_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )
```

注意：不要删除 `material_type` 字段（保持向后兼容），但将其标记为 deprecated 或保留默认值。

```python
    # 保留旧字段以兼容
    material_type: Mapped[str] = mapped_column(String(64), nullable=False, default="general")
```

**Step 2: 验证导入**

Run: `cd backend-v2 && python -c "from app.models.settings import Material; print('OK')"`
Expected: OK

**Step 3: Commit**

```bash
git add backend-v2/app/models/settings.py
git commit -m "feat(material): extend Material model with category, tags, content, metadata"
```

---

### Task 7: 创建 Material Schemas

**目标:** 为 Material 创建 Pydantic schemas。

**文件:**
- Create: `backend-v2/app/schemas/material.py`

**Step 1: 创建 schema 文件**

```python
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


class MaterialBase(BaseModel):
    name: str
    category: str = Field(default="other")
    tags: list[str] = Field(default_factory=list)
    content: str = Field(default="")
    file_path: str = Field(default="")
    description: str = Field(default="")
    organization: str = Field(default="")
    acquired_date: str = Field(default="")
    valid_until: str = Field(default="")
    is_active: bool = Field(default=True)
    metadata_json: dict = Field(default_factory=dict)


class MaterialCreate(MaterialBase):
    pass


class MaterialUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    tags: list[str] | None = None
    content: str | None = None
    file_path: str | None = None
    description: str | None = None
    organization: str | None = None
    acquired_date: str | None = None
    valid_until: str | None = None
    is_active: bool | None = None
    metadata_json: dict | None = None


class MaterialSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    category: str
    tags: str  # JSON string from DB
    description: str
    is_active: bool
    created_at: datetime


class MaterialDetail(MaterialBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    material_type: str = Field(default="general")  # backward compat
    created_at: datetime
    updated_at: datetime
```

**Step 2: 验证导入**

Run: `cd backend-v2 && python -c "from app.schemas.material import MaterialDetail; print('OK')"`
Expected: OK

**Step 3: Commit**

```bash
git add backend-v2/app/schemas/material.py
git commit -m "feat(schemas): add Material Pydantic schemas"
```

---

### Task 8: 创建 Material CRUD Service

**目标:** 实现素材的增删改查服务。

**文件:**
- Create: `backend-v2/app/services/material_service.py`

**Step 1: 创建服务文件**

```python
import json
import uuid
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.settings import Material
from app.schemas.material import MaterialCreate, MaterialUpdate


def list_materials(
    db: Session,
    *,
    category: str | None = None,
    tag: str | None = None,
    is_active: bool | None = None,
    search: str | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[Material]:
    query = db.query(Material)
    if category:
        query = query.filter(Material.category == category)
    if is_active is not None:
        query = query.filter(Material.is_active == is_active)
    if search:
        like = f"%{search}%"
        query = query.filter(
            Material.name.ilike(like) | Material.description.ilike(like) | Material.content.ilike(like)
        )
    if tag:
        # Simple JSON string containment check
        query = query.filter(Material.tags.contains(tag))
    return query.offset(skip).limit(limit).all()


def get_material(db: Session, material_id: str) -> Material:
    material = db.query(Material).filter(Material.id == material_id).first()
    if not material:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="素材不存在")
    return material


def create_material(db: Session, payload: MaterialCreate) -> Material:
    material = Material(
        id=str(uuid.uuid4()),
        name=payload.name,
        category=payload.category,
        tags=json.dumps(payload.tags, ensure_ascii=False),
        content=payload.content,
        file_path=payload.file_path,
        description=payload.description,
        organization=payload.organization,
        acquired_date=payload.acquired_date,
        valid_until=payload.valid_until,
        is_active=payload.is_active,
        metadata_json=json.dumps(payload.metadata_json, ensure_ascii=False),
    )
    db.add(material)
    db.commit()
    db.refresh(material)
    return material


def update_material(db: Session, material_id: str, payload: MaterialUpdate) -> Material:
    material = get_material(db, material_id)
    update_data: dict[str, Any] = payload.model_dump(exclude_unset=True)
    if "tags" in update_data and update_data["tags"] is not None:
        update_data["tags"] = json.dumps(update_data["tags"], ensure_ascii=False)
    if "metadata_json" in update_data and update_data["metadata_json"] is not None:
        update_data["metadata_json"] = json.dumps(update_data["metadata_json"], ensure_ascii=False)
    for key, value in update_data.items():
        setattr(material, key, value)
    db.commit()
    db.refresh(material)
    return material


def delete_material(db: Session, material_id: str) -> None:
    material = get_material(db, material_id)
    db.delete(material)
    db.commit()
```

**Step 2: 验证导入**

Run: `cd backend-v2 && python -c "from app.services.material_service import list_materials; print('OK')"`
Expected: OK

**Step 3: Commit**

```bash
git add backend-v2/app/services/material_service.py
git commit -m "feat(service): add Material CRUD service"
```

---

### Task 9: 创建 Material API 路由

**目标:** 注册素材 REST API。

**文件:**
- Create: `backend-v2/app/api/v1/endpoints/materials.py`

**Step 1: 创建路由文件**

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.material import (
    MaterialCreate,
    MaterialUpdate,
    MaterialSummary,
    MaterialDetail,
)
from app.services import material_service

router = APIRouter()


@router.get("/", response_model=list[MaterialSummary])
def list_materials(
    category: str | None = None,
    tag: str | None = None,
    search: str | None = None,
    is_active: bool | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
) -> list[MaterialSummary]:
    return material_service.list_materials(
        db, category=category, tag=tag, search=search, is_active=is_active, skip=skip, limit=limit
    )


@router.post("/", response_model=MaterialDetail)
def create_material(
    payload: MaterialCreate,
    db: Session = Depends(get_db),
) -> MaterialDetail:
    return MaterialDetail.model_validate(material_service.create_material(db, payload))


@router.get("/{material_id}", response_model=MaterialDetail)
def get_material(
    material_id: str,
    db: Session = Depends(get_db),
) -> MaterialDetail:
    return MaterialDetail.model_validate(material_service.get_material(db, material_id))


@router.patch("/{material_id}", response_model=MaterialDetail)
def update_material(
    material_id: str,
    payload: MaterialUpdate,
    db: Session = Depends(get_db),
) -> MaterialDetail:
    return MaterialDetail.model_validate(material_service.update_material(db, material_id, payload))


@router.delete("/{material_id}")
def delete_material(
    material_id: str,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    material_service.delete_material(db, material_id)
    return {"message": "素材已删除"}
```

**Step 2: 在 router.py 中注册**

Find: `backend-v2/app/api/v1/router.py`
Add:
```python
from app.api.v1.endpoints import materials

# ... 在 existing router includes 附近 ...
api_router.include_router(materials.router, prefix="/materials", tags=["materials"])
```

**Step 3: 验证**

Run: `cd backend-v2 && python -c "from app.api.v1.router import api_router; print('OK')"`
Expected: OK

**Step 4: Commit**

```bash
git add backend-v2/app/api/v1/endpoints/materials.py backend-v2/app/api/v1/router.py
git commit -m "feat(api): add Material CRUD REST endpoints"
```

---

### Task 10: 增强 Asset Routing Service — 素材自动匹配

**目标:** 在 `asset_routing_service.py` 中增加基于 `Material` 的分类匹配逻辑。

**文件:**
- Modify: `backend-v2/app/services/asset_routing_service.py`

**Step 1: 新增 Material 匹配函数**

在 `AssetRoutingService` 类中，新增 `route_materials_for_document` 方法：

```python
    def route_materials_for_document(
        self,
        db: Session,
        *,
        doc_type: str,
        doc_name: str,
        rule_description: str,
        project_summary: str,
        limit: int = 5,
    ) -> list[RoutedAsset]:
        """
        Match Materials from the material library based on doc_type and rule_description.
        Returns list of RoutedAsset for injection into document generation.
        """
        from app.models.settings import Material

        # Determine target categories from doc_type
        category_map: dict[str, list[str]] = {
            "deviation": ["certificate", "other"],
            "commitment": ["certificate", "other"],
            "authorization": ["certificate"],
            "cmmi": ["cmmi", "certificate"],
            "soft_copy": ["soft_copy", "certificate"],
            "project_experience": ["project_experience"],
            "personnel_capability": ["personnel_capability"],
            "maintenance_period": ["certificate", "other"],
            "project_manager": ["personnel_capability"],
            "staff_capability": ["personnel_capability"],
            "hardware_resource": ["certificate", "other"],
        }
        target_categories = category_map.get(doc_type, [])
        if not target_categories:
            target_categories = ["other"]

        query = db.query(Material).filter(
            Material.is_active == True,
            Material.category.in_(target_categories),
        )

        # Keyword search from rule_description
        keywords: list[str] = []
        if rule_description:
            for line in rule_description.splitlines():
                line = line.strip()
                if not line:
                    continue
                cleaned = re.sub(r"^[\u2460-\u247f\d]+[\.\)\uff09\s]+", "", line)
                cleaned = re.split(r"[\uff0c,\u3002\uff1b;]", cleaned)[0]
                if 4 <= len(cleaned) <= 30:
                    keywords.append(cleaned)

        materials = query.all()
        matches: list[RoutedAsset] = []

        for m in materials:
            score = 0.0
            reasons: list[str] = []

            # Category match
            if m.category in target_categories:
                score += 2.0
                reasons.append(f"分类匹配: {m.category}")

            # Keyword match against content/name/description
            m_text = f"{m.name} {m.description} {m.content}"
            for kw in keywords:
                if kw in m_text:
                    score += 1.0
                    reasons.append(f"关键词匹配: {kw}")

            # Project summary relevance
            if project_summary and any(term in m_text for term in _extract_terms(project_summary)):
                score += 0.5
                reasons.append("项目相关度匹配")

            if score <= 0:
                continue

            snippet = m.content[:220] if m.content else m.description[:220]
            matches.append(
                RoutedAsset(
                    asset_id=m.id,
                    asset_title=m.name,
                    asset_type=m.category,
                    chunk_title=m.name,
                    snippet=snippet,
                    reason="；".join(reasons)[:280],
                    score=round(score, 2),
                )
            )

        matches.sort(key=lambda item: item.score, reverse=True)
        return matches[:limit]
```

**Step 2: 在三个文档生成服务中接入 Material 路由**

以 `business_document_service.py` 为例，在调用 `asset_routing_service.route_assets_for_section` 之后，增加 Material 匹配：

```python
    # Material library routing
    material_assets = asset_routing_service.route_materials_for_document(
        db,
        doc_type=doc.doc_type,
        doc_name=doc.doc_name,
        rule_description=doc.rule_description,
        project_summary=project_summary,
        limit=3,
    )
    for ma in material_assets:
        routed_asset_payloads.append(f"{ma.asset_title}�{ma.asset_type}�{ma.snippet}")
```

对 `technical_document_service.py` 和 `proposal_plan_service.py` 做同样修改。

**Step 3: 验证导入**

Run: `cd backend-v2 && python -c "from app.services.asset_routing_service import asset_routing_service; print('OK')"`
Expected: OK

**Step 4: Commit**

```bash
git add backend-v2/app/services/asset_routing_service.py
git add backend-v2/app/services/business_document_service.py
# ... also technical_document_service.py and proposal_plan_service.py if modified
git commit -m "feat(asset): add Material-based auto-matching to asset routing service"
```

---

### Task 11: 生成 Alembic 迁移（Material 表扩展）

**目标:** 为 Material 模型字段扩展创建迁移。

**Step 1: 生成迁移**

Run:
```bash
cd backend-v2
alembic revision --autogenerate -m "extend materials table with category content metadata"
```

**Step 2: 检查并应用**

Run: `alembic upgrade head`
Expected: 成功

**Step 3: Commit**

```bash
git add backend-v2/alembic/versions/
git commit -m "chore(db): alembic migration for extended Material model"
```

---

### Task 12: Smoke 测试

**目标:** 验证所有新增代码可导入、API 可注册。

**Step 1: 后端导入测试**

Run:
```bash
cd backend-v2
python -c "from app.main import app"
```
Expected: 无报错，正常退出

**Step 2: 启动服务测试**

Run:
```bash
cd backend-v2
python -c "
from fastapi.testclient import TestClient
from app.main import app
client = TestClient(app)
print('Health:', client.get('/api/v1/health').status_code)
"
```
Expected: Health: 200

**Step 3: Commit（如发现问题则修复后再提交）**

---

## 执行顺序

1. **Task 1** — 扩展 Schema
2. **Task 2** — LLM 打分 Client
3. **Task 3** — 重构 scoring_service
4. **Task 4** — Proposal /score 路由
5. **Task 5** — Alembic 迁移 (score history)
6. **Task 6** — 扩展 Material 模型
7. **Task 7** — Material Schemas
8. **Task 8** — Material Service
9. **Task 9** — Material API
10. **Task 10** — Asset Routing 增强
11. **Task 11** — Alembic 迁移 (material)
12. **Task 12** — Smoke 测试

---

## 验收标准

| 检查项 | 标准 |
|--------|------|
| BE-013 启发式打分 | `/score` 接口返回的 `breakdown.semantic_quality` 不为空，`llm_reasoning` 有内容 |
| BE-013 二次重算 | 人工修改文档后再次调用 `/score`，`previous_score` 和 `score_delta` 正确 |
| BE-013 方案打分 | `/proposal-plans/{id}/score` 返回 200 且结构正确 |
| BE-014 素材 CRUD | `GET/POST/PATCH/DELETE /api/v1/materials/` 均正常 |
| BE-014 自动匹配 | 生成文档时 `routed_assets` 中包含 Material 库中的匹配素材 |
| 后端启动 | `python -c "from app.main import app"` 无报错 |
| 数据库迁移 | `alembic upgrade head` 成功 |
