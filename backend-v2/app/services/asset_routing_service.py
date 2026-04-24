import re
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.knowledge_asset import KnowledgeAssetRecord
from app.services.asset_index_service import asset_index_service


@dataclass(frozen=True)
class RoutedAsset:
    asset_id: str
    asset_title: str
    asset_type: str
    chunk_title: str
    snippet: str
    reason: str
    score: float


def _extract_terms(text: str) -> set[str]:
    terms = re.findall(r"[A-Za-z0-9\-]{2,}|[\u4e00-\u9fff]{2,8}", text)
    stopwords = {"项目", "方案", "要求", "支持", "提供", "需要", "当前", "说明", "建设", "项目名称"}
    return {term.strip().lower() for term in terms if term.strip() and term not in stopwords}


class AssetRoutingService:
    def route_assets_for_section(
        self,
        db: Session,
        *,
        section_title: str,
        project_summary: str,
        tender_requirements: str,
        delivery_deadline: str,
        service_commitment: str,
        selected_asset_titles: list[str],
        fixed_asset_titles: list[str],
        excluded_asset_titles: list[str],
        extracted_fields: dict[str, str],
        limit: int = 3,
    ) -> list[RoutedAsset]:
        assets = asset_index_service.list_routable_assets(db)
        asset_map = {asset.id: asset for asset in assets}
        asset_ids = [asset.id for asset in assets]
        chunks = asset_index_service.list_chunks(db, asset_ids)

        query_terms = _extract_terms(
            " ".join(
                [
                    section_title,
                    project_summary,
                    tender_requirements,
                    delivery_deadline,
                    service_commitment,
                    " ".join(extracted_fields.values()),
                ]
            )
        )

        matches: list[RoutedAsset] = []
        for chunk in chunks:
            asset = asset_map.get(chunk.asset_id)
            if asset is None:
                continue
            if asset.title in excluded_asset_titles:
                continue

            chunk_terms = _extract_terms(
                " ".join(
                    [
                        asset.title,
                        asset.summary,
                        asset.keywords,
                        asset.section_tags,
                        chunk.title,
                        chunk.content,
                        chunk.keywords,
                        chunk.section_tags,
                    ]
                )
            )
            score = 0.0
            reasons: list[str] = []

            asset_section_tags = set(asset_index_service.split_values(asset.section_tags))
            chunk_section_tags = set(asset_index_service.split_values(chunk.section_tags))
            if section_title in asset_section_tags or section_title in chunk_section_tags:
                score += 3.5
                reasons.append(f"适配章节“{section_title}”")

            if asset.title in selected_asset_titles:
                score += 3.0
                reasons.append("命中用户已选素材")

            if asset.title in fixed_asset_titles:
                score += 4.0
                reasons.append("项目固定引用素材")

            overlaps = sorted(query_terms & chunk_terms)
            if overlaps:
                overlap_score = min(4.0, len(overlaps) * 0.8)
                score += overlap_score
                reasons.append(f"关键词匹配：{'、'.join(overlaps[:4])}")

            if section_title == "售后服务方案" and ("服务" in asset.asset_type or "SLA" in chunk.content):
                score += 1.5
                reasons.append("服务承诺场景匹配")

            if section_title == "公司概况与资质" and ("资质" in asset.asset_type or "资质" in asset.title):
                score += 1.5
                reasons.append("资质能力场景匹配")

            if section_title == "实施计划与里程碑" and ("交付" in chunk.content or "实施" in chunk.content):
                score += 1.2
                reasons.append("交付实施场景匹配")

            score *= chunk.weight
            if score <= 0:
                continue

            matches.append(
                RoutedAsset(
                    asset_id=asset.id,
                    asset_title=asset.title,
                    asset_type=asset.asset_type,
                    chunk_title=chunk.title,
                    snippet=chunk.content[:220],
                    reason="；".join(reasons)[:280],
                    score=round(score, 2),
                )
            )

        matches.sort(key=lambda item: item.score, reverse=True)
        if matches:
            return matches[:limit]

        fallback_assets = [
            asset
            for asset in assets
            if asset.title not in excluded_asset_titles
            and (not selected_asset_titles or asset.title in selected_asset_titles)
        ]
        return [
            RoutedAsset(
                asset_id=asset.id,
                asset_title=asset.title,
                asset_type=asset.asset_type,
                chunk_title="默认摘要",
                snippet=asset.summary[:220],
                reason="未命中明确关键词，回退到默认可引用素材",
                score=1.0,
            )
            for asset in fallback_assets[:limit]
        ]


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


asset_routing_service = AssetRoutingService()
