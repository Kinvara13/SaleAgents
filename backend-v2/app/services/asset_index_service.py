import re
from io import BytesIO
from uuid import uuid4

from docx import Document
from fastapi import HTTPException, status
from pypdf import PdfReader
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.knowledge_asset import KnowledgeAssetRecord
from app.models.knowledge_asset_chunk import KnowledgeAssetChunkRecord
from app.models.knowledge_asset_source import KnowledgeAssetSourceRecord
from app.models.knowledge_asset_workflow import KnowledgeAssetWorkflowRecord
from app.schemas.generation import IndexedGenerationAssetResponse
from app.schemas.workspace import KnowledgeAsset

SECTION_TITLES = [
    "项目理解与建设目标",
    "公司概况与资质",
    "总体技术方案",
    "实施计划与里程碑",
    "售后服务方案",
    "商务偏离说明",
]

ASSET_PROFILE_MAP: dict[str, dict[str, object]] = {
    "园区安防平台解决方案 V5.2": {
        "summary": "覆盖视频安防平台架构、设备接入、平台联动、存储留存和实施边界，适合技术方案章节引用。",
        "keywords": ["园区安防", "视频接入", "平台架构", "联动", "存储", "实施"],
        "scene_tags": ["园区", "安防", "视频"],
        "section_tags": ["项目理解与建设目标", "总体技术方案", "实施计划与里程碑"],
        "chunks": [
            {
                "title": "平台架构与能力边界",
                "content": "支持多级平台部署、设备统一纳管、视频接入汇聚、事件联动处置与30天以上录像留存策略。",
                "keywords": ["平台架构", "统一纳管", "视频接入", "录像留存"],
                "section_tags": ["总体技术方案"],
                "weight": 1.2,
            },
            {
                "title": "实施交付约束",
                "content": "实施阶段包括现场勘查、网络联通、平台部署、联调测试、培训交接和正式验收，可匹配45至90天交付周期。",
                "keywords": ["现场勘查", "联调测试", "培训交接", "验收", "交付周期"],
                "section_tags": ["实施计划与里程碑"],
                "weight": 1.1,
            },
        ],
    },
    "智慧园区行业案例集": {
        "summary": "沉淀智慧园区、城市治理和视频安防项目案例，可为项目理解、资质能力和实施可行性提供佐证。",
        "keywords": ["智慧园区", "行业案例", "视频安防", "验收", "交付经验"],
        "scene_tags": ["园区", "政企", "安防"],
        "section_tags": ["项目理解与建设目标", "公司概况与资质", "实施计划与里程碑"],
        "chunks": [
            {
                "title": "同类项目履约案例",
                "content": "已交付多个智慧园区视频安防项目，覆盖设备改造、平台升级、现场部署与验收支撑，可用于论证实施可行性。",
                "keywords": ["履约案例", "平台升级", "现场部署", "验收支撑"],
                "section_tags": ["公司概况与资质", "实施计划与里程碑"],
                "weight": 1.15,
            }
        ],
    },
    "电子与智能化一级资质": {
        "summary": "用于应答资格条件、企业能力和合规资质要求，适合资质章节与商务响应章节引用。",
        "keywords": ["电子与智能化", "一级资质", "资格条件", "企业能力", "合规"],
        "scene_tags": ["资质", "合规"],
        "section_tags": ["公司概况与资质", "商务偏离说明"],
        "chunks": [
            {
                "title": "资质能力说明",
                "content": "具备电子与智能化相关资质证书和项目交付能力，可对照招标文件的资质门槛逐项响应。",
                "keywords": ["资质证书", "资质门槛", "逐项响应"],
                "section_tags": ["公司概况与资质", "商务偏离说明"],
                "weight": 1.25,
            }
        ],
    },
    "售后 SLA 标准条款": {
        "summary": "提供售后服务等级、响应时效、巡检与质保条款模板，适合服务承诺和商务条款章节复用。",
        "keywords": ["SLA", "售后服务", "响应时效", "巡检", "质保"],
        "scene_tags": ["服务", "运维"],
        "section_tags": ["售后服务方案", "商务偏离说明"],
        "chunks": [
            {
                "title": "服务响应模板",
                "content": "支持7x24小时受理、分级响应、故障升级、现场支持和质保期内维护安排，可按项目要求做裁剪。",
                "keywords": ["7x24", "分级响应", "现场支持", "质保期"],
                "section_tags": ["售后服务方案"],
                "weight": 1.2,
            }
        ],
    },
}


def _join_values(values: list[str]) -> str:
    return "||".join([item.strip() for item in values if item.strip()])


def _split_values(value: str) -> list[str]:
    return [item.strip() for item in value.split("||") if item.strip()]


def _extract_terms(text: str) -> list[str]:
    items = re.findall(r"[A-Za-z0-9\-]{2,}|[\u4e00-\u9fff]{2,8}", text)
    seen: set[str] = set()
    terms: list[str] = []
    for item in items:
        token = item.strip().lower()
        if token and token not in seen:
            seen.add(token)
            terms.append(item.strip())
    return terms[:20]


def _detect_section_tags(text: str, asset_type: str) -> list[str]:
    tags: list[str] = []
    if any(term in text for term in ("资质", "证书", "案例", "企业简介")) or "资质" in asset_type:
        tags.append("公司概况与资质")
    if any(term in text for term in ("平台", "架构", "技术", "视频", "接口", "能力")):
        tags.append("总体技术方案")
    if any(term in text for term in ("实施", "交付", "里程碑", "部署", "验收", "排期")):
        tags.append("实施计划与里程碑")
    if any(term in text for term in ("售后", "响应", "SLA", "质保", "巡检", "驻场")) or "服务" in asset_type:
        tags.append("售后服务方案")
    if any(term in text for term in ("商务", "付款", "偏离", "合同", "条款")):
        tags.append("商务偏离说明")
    if any(term in text for term in ("项目背景", "场景", "目标", "案例", "园区")):
        tags.append("项目理解与建设目标")
    return list(dict.fromkeys(tags)) or ["总体技术方案"]


def _detect_scene_tags(text: str, asset_type: str) -> list[str]:
    tags: list[str] = []
    for term in ("园区", "安防", "视频", "政企", "能源", "制造", "服务", "运维", "资质", "合规"):
        if term in text or term in asset_type:
            tags.append(term)
    return list(dict.fromkeys(tags)) or [asset_type]


def _derive_profile(asset: KnowledgeAsset) -> dict[str, object]:
    if asset.title in ASSET_PROFILE_MAP:
        return ASSET_PROFILE_MAP[asset.title]

    title_keywords = _extract_terms(asset.title)
    summary = f"{asset.title}可用于{asset.type}类章节的证据引用与支撑说明。"
    return {
        "summary": summary,
        "keywords": title_keywords or [asset.type, asset.title],
        "scene_tags": [asset.type],
        "section_tags": ["公司概况与资质", "总体技术方案"],
        "chunks": [
            {
                "title": asset.title,
                "content": summary,
                "keywords": title_keywords or [asset.type],
                "section_tags": ["公司概况与资质", "总体技术方案"],
                "weight": 1.0,
            }
        ],
    }


class AssetIndexService:
    def initialize_seed_assets(self, db: Session) -> None:
        from app.services.workspace_service import get_generation_assets

        assets = get_generation_assets(db)
        for asset in assets:
            existing = db.scalars(
                select(KnowledgeAssetRecord).where(KnowledgeAssetRecord.title == asset.title).limit(1)
            ).first()
            if existing is not None:
                existing_source = db.scalars(
                    select(KnowledgeAssetSourceRecord)
                    .where(KnowledgeAssetSourceRecord.asset_id == existing.id)
                    .limit(1)
                ).first()
                if existing_source is None:
                    profile = _derive_profile(asset)
                    db.add(
                        KnowledgeAssetSourceRecord(
                            id=f"asset-src-{uuid4().hex[:10]}",
                            asset_id=existing.id,
                            source_kind="seed",
                            file_name=asset.title,
                            source_text="\n".join([item["content"] for item in profile["chunks"]]),
                        )
                    )
                existing_workflow = db.scalars(
                    select(KnowledgeAssetWorkflowRecord)
                    .where(KnowledgeAssetWorkflowRecord.asset_id == existing.id)
                    .limit(1)
                ).first()
                if existing_workflow is None:
                    db.add(
                        KnowledgeAssetWorkflowRecord(
                            id=f"asset-flow-{uuid4().hex[:10]}",
                            asset_id=existing.id,
                            owner="system",
                            visibility="internal",
                            review_status="approved",
                            reviewer="system",
                            review_note="系统种子素材默认可用",
                        )
                    )
                continue

            profile = _derive_profile(asset)
            asset_row = KnowledgeAssetRecord(
                id=f"asset-{uuid4().hex[:10]}",
                title=asset.title,
                asset_type=asset.type,
                score=asset.score,
                status=asset.status,
                summary=str(profile["summary"]),
                keywords=_join_values(list(profile["keywords"])),
                scene_tags=_join_values(list(profile["scene_tags"])),
                section_tags=_join_values(list(profile["section_tags"])),
            )
            db.add(asset_row)
            db.flush()
            db.add(
                KnowledgeAssetSourceRecord(
                    id=f"asset-src-{uuid4().hex[:10]}",
                    asset_id=asset_row.id,
                    source_kind="seed",
                    file_name=asset.title,
                    source_text="\n".join([item["content"] for item in profile["chunks"]]),
                )
            )
            db.add(
                KnowledgeAssetWorkflowRecord(
                    id=f"asset-flow-{uuid4().hex[:10]}",
                    asset_id=asset_row.id,
                    owner="system",
                    visibility="internal",
                    review_status="approved",
                    reviewer="system",
                    review_note="系统种子素材默认可用",
                )
            )
            self._replace_chunks(db, asset_row.id, profile["chunks"])
        db.commit()

    def list_assets(self, db: Session) -> list[KnowledgeAssetRecord]:
        return db.scalars(select(KnowledgeAssetRecord).order_by(KnowledgeAssetRecord.title.asc())).all()

    def list_chunks(self, db: Session, asset_ids: list[str] | None = None) -> list[KnowledgeAssetChunkRecord]:
        stmt = select(KnowledgeAssetChunkRecord).order_by(
            KnowledgeAssetChunkRecord.asset_id.asc(), KnowledgeAssetChunkRecord.sort_order.asc()
        )
        if asset_ids:
            stmt = stmt.where(KnowledgeAssetChunkRecord.asset_id.in_(asset_ids))
        return db.scalars(stmt).all()

    def list_asset_responses(self, db: Session) -> list[IndexedGenerationAssetResponse]:
        assets = self.list_assets(db)
        sources = db.scalars(select(KnowledgeAssetSourceRecord)).all()
        workflows = db.scalars(select(KnowledgeAssetWorkflowRecord)).all()
        source_map = {row.asset_id: row for row in sources}
        workflow_map = {row.asset_id: row for row in workflows}
        return [
            IndexedGenerationAssetResponse(
                id=row.id,
                title=row.title,
                asset_type=row.asset_type,
                score=row.score,
                status=row.status,
                summary=row.summary,
                keywords=_split_values(row.keywords),
                scene_tags=_split_values(row.scene_tags),
                section_tags=_split_values(row.section_tags),
                source_kind=source_map.get(row.id).source_kind if source_map.get(row.id) else "manual",
                file_name=source_map.get(row.id).file_name if source_map.get(row.id) else "",
                owner=workflow_map.get(row.id).owner if workflow_map.get(row.id) else "system",
                visibility=workflow_map.get(row.id).visibility if workflow_map.get(row.id) else "internal",
                review_status=workflow_map.get(row.id).review_status if workflow_map.get(row.id) else "approved",
                reviewer=workflow_map.get(row.id).reviewer if workflow_map.get(row.id) else "",
                review_note=workflow_map.get(row.id).review_note if workflow_map.get(row.id) else "",
            )
            for row in assets
        ]

    def create_manual_asset(
        self,
        db: Session,
        *,
        title: str,
        asset_type: str,
        status_text: str,
        content: str,
        owner: str,
        visibility: str,
    ) -> IndexedGenerationAssetResponse:
        asset_row = KnowledgeAssetRecord(
            id=f"asset-{uuid4().hex[:10]}",
            title=title.strip(),
            asset_type=asset_type.strip() or "通用素材",
            score="0.82",
            status=status_text.strip() or "可引用",
            summary="",
            keywords="",
            scene_tags="",
            section_tags="",
        )
        db.add(asset_row)
        db.flush()
        db.add(
            KnowledgeAssetSourceRecord(
                id=f"asset-src-{uuid4().hex[:10]}",
                asset_id=asset_row.id,
                source_kind="manual",
                file_name=title.strip(),
                source_text=content.strip(),
            )
        )
        db.add(
            KnowledgeAssetWorkflowRecord(
                id=f"asset-flow-{uuid4().hex[:10]}",
                asset_id=asset_row.id,
                owner=owner.strip() or "system",
                visibility=visibility.strip() or "internal",
                review_status="pending_review",
                reviewer="",
                review_note="新增素材待审核",
            )
        )
        self._reindex_asset(db, asset_row, content.strip())
        db.commit()
        return next(item for item in self.list_asset_responses(db) if item.id == asset_row.id)

    def create_uploaded_asset(
        self,
        db: Session,
        *,
        filename: str,
        file_bytes: bytes,
        asset_type: str,
        title: str | None = None,
        owner: str = "system",
        visibility: str = "internal",
    ) -> IndexedGenerationAssetResponse:
        content = self._extract_text_from_file(filename, file_bytes)
        asset_title = (title or filename.rsplit(".", 1)[0]).strip()
        if not content:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Unable to extract text from uploaded asset.",
            )
        asset_row = KnowledgeAssetRecord(
            id=f"asset-{uuid4().hex[:10]}",
            title=asset_title,
            asset_type=asset_type.strip() or "通用素材",
            score="0.84",
            status="可引用",
            summary="",
            keywords="",
            scene_tags="",
            section_tags="",
        )
        db.add(asset_row)
        db.flush()
        db.add(
            KnowledgeAssetSourceRecord(
                id=f"asset-src-{uuid4().hex[:10]}",
                asset_id=asset_row.id,
                source_kind="upload",
                file_name=filename,
                source_text=content,
            )
        )
        db.add(
            KnowledgeAssetWorkflowRecord(
                id=f"asset-flow-{uuid4().hex[:10]}",
                asset_id=asset_row.id,
                owner=owner.strip() or "system",
                visibility=visibility.strip() or "internal",
                review_status="pending_review",
                reviewer="",
                review_note="上传素材待审核",
            )
        )
        self._reindex_asset(db, asset_row, content)
        db.commit()
        return next(item for item in self.list_asset_responses(db) if item.id == asset_row.id)

    def refresh_asset_indexes(self, db: Session, asset_id: str | None = None) -> int:
        assets = self.list_assets(db)
        if asset_id:
            assets = [item for item in assets if item.id == asset_id]
        source_rows = db.scalars(select(KnowledgeAssetSourceRecord)).all()
        source_map = {row.asset_id: row for row in source_rows}
        refreshed = 0
        for asset_row in assets:
            source_text = source_map.get(asset_row.id).source_text if source_map.get(asset_row.id) else asset_row.summary
            self._reindex_asset(db, asset_row, source_text)
            refreshed += 1
        db.commit()
        return refreshed

    def split_values(self, value: str) -> list[str]:
        return _split_values(value)

    def list_routable_assets(self, db: Session) -> list[KnowledgeAssetRecord]:
        workflows = db.scalars(select(KnowledgeAssetWorkflowRecord)).all()
        approved_ids = {row.asset_id for row in workflows if row.review_status == "approved"}
        return [row for row in self.list_assets(db) if row.id in approved_ids]

    def list_asset_chunks(self, db: Session, asset_id: str) -> list[KnowledgeAssetChunkRecord]:
        self.get_asset_or_404(db, asset_id)
        return db.scalars(
            select(KnowledgeAssetChunkRecord)
            .where(KnowledgeAssetChunkRecord.asset_id == asset_id)
            .order_by(KnowledgeAssetChunkRecord.sort_order.asc())
        ).all()

    def update_asset(
        self,
        db: Session,
        *,
        asset_id: str,
        title: str,
        asset_type: str,
        status_text: str,
        content: str,
        owner: str,
        visibility: str,
    ) -> IndexedGenerationAssetResponse:
        asset_row = self.get_asset_or_404(db, asset_id)
        source_row = self._get_source_or_404(db, asset_id)
        workflow = self._get_workflow_or_404(db, asset_id)
        asset_row.title = title.strip()
        asset_row.asset_type = asset_type.strip() or "通用素材"
        asset_row.status = status_text.strip() or "可引用"
        source_row.file_name = title.strip()
        source_row.source_text = content.strip()
        workflow.owner = owner.strip() or workflow.owner
        workflow.visibility = visibility.strip() or workflow.visibility
        workflow.review_status = "pending_review"
        workflow.review_note = "素材编辑后待重新审核"
        workflow.reviewer = ""
        self._reindex_asset(db, asset_row, content.strip())
        db.commit()
        return next(item for item in self.list_asset_responses(db) if item.id == asset_id)

    def delete_asset(self, db: Session, asset_id: str) -> None:
        self.get_asset_or_404(db, asset_id)
        db.execute(delete(KnowledgeAssetChunkRecord).where(KnowledgeAssetChunkRecord.asset_id == asset_id))
        db.execute(delete(KnowledgeAssetSourceRecord).where(KnowledgeAssetSourceRecord.asset_id == asset_id))
        db.execute(delete(KnowledgeAssetWorkflowRecord).where(KnowledgeAssetWorkflowRecord.asset_id == asset_id))
        db.execute(delete(KnowledgeAssetRecord).where(KnowledgeAssetRecord.id == asset_id))
        db.commit()

    def review_asset(
        self,
        db: Session,
        *,
        asset_id: str,
        action: str,
        reviewer: str,
        review_note: str,
    ) -> IndexedGenerationAssetResponse:
        self.get_asset_or_404(db, asset_id)
        workflow = self._get_workflow_or_404(db, asset_id)
        workflow.review_status = "approved" if action == "approve" else "rejected"
        workflow.reviewer = reviewer.strip()
        workflow.review_note = review_note.strip()
        db.commit()
        return next(item for item in self.list_asset_responses(db) if item.id == asset_id)

    def create_chunk(
        self,
        db: Session,
        *,
        asset_id: str,
        title: str,
        content: str,
        keywords: list[str],
        section_tags: list[str],
        weight: float,
    ) -> KnowledgeAssetChunkRecord:
        self.get_asset_or_404(db, asset_id)
        existing = self.list_asset_chunks(db, asset_id)
        row = KnowledgeAssetChunkRecord(
            id=f"asset-chunk-{uuid4().hex[:10]}",
            asset_id=asset_id,
            title=title.strip(),
            content=content.strip(),
            keywords=_join_values(keywords),
            section_tags=_join_values(section_tags),
            sort_order=(existing[-1].sort_order + 1) if existing else 1,
            weight=weight,
        )
        db.add(row)
        workflow = self._get_workflow_or_404(db, asset_id)
        workflow.review_status = "pending_review"
        workflow.review_note = "片段新增后待重新审核"
        workflow.reviewer = ""
        db.commit()
        db.refresh(row)
        return row

    def update_chunk(
        self,
        db: Session,
        *,
        asset_id: str,
        chunk_id: str,
        title: str,
        content: str,
        keywords: list[str],
        section_tags: list[str],
        weight: float,
    ) -> KnowledgeAssetChunkRecord:
        self.get_asset_or_404(db, asset_id)
        chunk = self._get_chunk_or_404(db, asset_id, chunk_id)
        chunk.title = title.strip()
        chunk.content = content.strip()
        chunk.keywords = _join_values(keywords)
        chunk.section_tags = _join_values(section_tags)
        chunk.weight = weight
        workflow = self._get_workflow_or_404(db, asset_id)
        workflow.review_status = "pending_review"
        workflow.review_note = "片段编辑后待重新审核"
        workflow.reviewer = ""
        db.commit()
        db.refresh(chunk)
        return chunk

    def delete_chunk(self, db: Session, *, asset_id: str, chunk_id: str) -> None:
        self.get_asset_or_404(db, asset_id)
        self._get_chunk_or_404(db, asset_id, chunk_id)
        db.execute(delete(KnowledgeAssetChunkRecord).where(KnowledgeAssetChunkRecord.id == chunk_id))
        workflow = self._get_workflow_or_404(db, asset_id)
        workflow.review_status = "pending_review"
        workflow.review_note = "片段删除后待重新审核"
        workflow.reviewer = ""
        db.commit()

    def _reindex_asset(self, db: Session, asset_row: KnowledgeAssetRecord, source_text: str) -> None:
        profile = self._profile_from_source(asset_row.title, asset_row.asset_type, source_text)
        asset_row.summary = str(profile["summary"])
        asset_row.keywords = _join_values(list(profile["keywords"]))
        asset_row.scene_tags = _join_values(list(profile["scene_tags"]))
        asset_row.section_tags = _join_values(list(profile["section_tags"]))
        self._replace_chunks(db, asset_row.id, list(profile["chunks"]))

    def _replace_chunks(self, db: Session, asset_id: str, chunks: list[dict[str, object]]) -> None:
        db.execute(delete(KnowledgeAssetChunkRecord).where(KnowledgeAssetChunkRecord.asset_id == asset_id))
        db.flush()
        for index, chunk in enumerate(chunks, start=1):
            db.add(
                KnowledgeAssetChunkRecord(
                    id=f"asset-chunk-{uuid4().hex[:10]}",
                    asset_id=asset_id,
                    title=str(chunk["title"]),
                    content=str(chunk["content"]),
                    keywords=_join_values(list(chunk["keywords"])),
                    section_tags=_join_values(list(chunk["section_tags"])),
                    sort_order=index,
                    weight=float(chunk["weight"]),
                )
            )

    def _profile_from_source(self, title: str, asset_type: str, source_text: str) -> dict[str, object]:
        if title in ASSET_PROFILE_MAP:
            return ASSET_PROFILE_MAP[title]

        paragraphs = [item.strip() for item in re.split(r"[\n\r]+", source_text) if item.strip()]
        if not paragraphs:
            paragraphs = [source_text.strip()]
        summary = paragraphs[0][:180] if paragraphs else f"{title}可用于{asset_type}相关章节。"
        keywords = _extract_terms(f"{title}\n{source_text}")[:10]
        scene_tags = _detect_scene_tags(source_text, asset_type)
        section_tags = _detect_section_tags(source_text, asset_type)
        chunks: list[dict[str, object]] = []
        for index, paragraph in enumerate(paragraphs[:5], start=1):
            if len(paragraph) < 8:
                continue
            chunk_tags = _detect_section_tags(paragraph, asset_type)
            chunks.append(
                {
                    "title": f"片段 {index}",
                    "content": paragraph[:500],
                    "keywords": _extract_terms(paragraph)[:8] or keywords[:4],
                    "section_tags": chunk_tags,
                    "weight": 1.0 + (0.1 if any(tag in chunk_tags for tag in section_tags[:2]) else 0.0),
                }
            )
        if not chunks:
            chunks.append(
                {
                    "title": title,
                    "content": summary,
                    "keywords": keywords[:6] or [asset_type],
                    "section_tags": section_tags,
                    "weight": 1.0,
                }
            )
        return {
            "summary": summary,
            "keywords": keywords or [asset_type, title],
            "scene_tags": scene_tags,
            "section_tags": section_tags,
            "chunks": chunks,
        }

    def _extract_text_from_file(self, filename: str, file_bytes: bytes) -> str:
        suffix = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
        if suffix in {"txt", "md"}:
            return file_bytes.decode("utf-8", errors="ignore").strip()
        if suffix == "docx":
            document = Document(BytesIO(file_bytes))
            return "\n".join([para.text.strip() for para in document.paragraphs if para.text.strip()]).strip()
        if suffix == "pdf":
            reader = PdfReader(BytesIO(file_bytes))
            page_texts = []
            for page in reader.pages:
                extracted = (page.extract_text() or "").strip()
                if extracted:
                    page_texts.append(extracted)
            return "\n".join(page_texts).strip()
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported asset type. Please upload txt, pdf, or docx.",
        )

    def get_asset_or_404(self, db: Session, asset_id: str) -> KnowledgeAssetRecord:
        row = db.get(KnowledgeAssetRecord, asset_id)
        if row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Asset '{asset_id}' not found.")
        return row

    def _get_source_or_404(self, db: Session, asset_id: str) -> KnowledgeAssetSourceRecord:
        row = db.scalars(
            select(KnowledgeAssetSourceRecord).where(KnowledgeAssetSourceRecord.asset_id == asset_id).limit(1)
        ).first()
        if row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Asset source '{asset_id}' not found.")
        return row

    def _get_workflow_or_404(self, db: Session, asset_id: str) -> KnowledgeAssetWorkflowRecord:
        row = db.scalars(
            select(KnowledgeAssetWorkflowRecord).where(KnowledgeAssetWorkflowRecord.asset_id == asset_id).limit(1)
        ).first()
        if row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Asset workflow '{asset_id}' not found.")
        return row

    def _get_chunk_or_404(self, db: Session, asset_id: str, chunk_id: str) -> KnowledgeAssetChunkRecord:
        row = db.get(KnowledgeAssetChunkRecord, chunk_id)
        if row is None or row.asset_id != asset_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Chunk '{chunk_id}' not found.")
        return row


asset_index_service = AssetIndexService()
