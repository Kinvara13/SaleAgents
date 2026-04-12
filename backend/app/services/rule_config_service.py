import json
from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.rule_config import RuleConfig
from app.models.rule_statistics import RuleStatistics
from app.schemas.review import (
    RuleConfigCreate,
    RuleConfigResponse,
    RuleConfigUpdate,
    RuleStatisticsResponse,
)


@dataclass(frozen=True)
class RuleDefinition:
    name: str
    title: str
    issue_type: str
    level: str
    detail: str
    suggestion: str
    patterns: tuple[str, ...]
    document: str
    match_mode: str = "any"


DEFAULT_RULES = [
    RuleDefinition(
        name="payment_tail_ratio_guardrail",
        title="付款条款与公司回款红线冲突",
        issue_type="付款风险",
        level="P0",
        detail="尾款或终验回款比例偏高，可能显著增加现金流和验收争议风险。",
        suggestion="优先谈判下调终验尾款比例；若无法调整，需提请经营负责人审批豁免。",
        patterns=("终验", "30%"),
        document="付款条款",
        match_mode="all",
    ),
    RuleDefinition(
        name="unlimited_liability_guardrail",
        title="责任承担存在无限责任表述",
        issue_type="责任风险",
        level="P0",
        detail="条款出现无限责任或兜底赔偿表述，超出常规可接受合同边界。",
        suggestion="增加责任上限并限定赔偿范围，避免使用全部损失或无限责任表述。",
        patterns=("无限责任",),
        document="违约责任条款",
    ),
    RuleDefinition(
        name="one_side_liability_guardrail",
        title="责任分配明显偏向甲方",
        issue_type="责任风险",
        level="P1",
        detail="条款将主要违约、延误或损失责任单边压给乙方，存在不对等风险。",
        suggestion="补充双方责任边界与免责条件，避免乙方承担全部责任类单边措辞。",
        patterns=("乙方承担全部责任", "供应商承担全部责任", "全部责任由乙方承担"),
        document="责任分配条款",
    ),
    RuleDefinition(
        name="auto_renewal_guardrail",
        title="合同存在自动续约条款",
        issue_type="续约风险",
        level="P1",
        detail="合同自动续约可能带来价格、服务范围和责任持续生效的管理风险。",
        suggestion="将自动续约改成双方书面确认后续签，补充续约价格和退出条件。",
        patterns=("自动续约", "自动延续"),
        document="期限与续约条款",
    ),
    RuleDefinition(
        name="acceptance_one_side_guardrail",
        title="验收标准存在单方解释风险",
        issue_type="验收风险",
        level="P1",
        detail="验收标准或结论由甲方单方认定，容易引发交付争议和尾款拖延。",
        suggestion="补充客观验收标准、验收时限与默认视为通过机制。",
        patterns=("甲方有权单方认定", "验收标准以甲方解释为准"),
        document="验收条款",
    ),
    RuleDefinition(
        name="ip_assignment_guardrail",
        title="知识产权归属表述需法务确认",
        issue_type="知识产权风险",
        level="P2",
        detail="成果或交付物知识产权直接归甲方所有，可能与公司标准模板冲突。",
        suggestion="区分背景知识产权与交付成果使用权，避免全部权利无条件转移。",
        patterns=("知识产权归甲方所有", "成果归甲方所有"),
        document="知识产权条款",
    ),
]


class RuleConfigService:
    def list_rules(
        self,
        db: Session,
        *,
        is_enabled: bool | None = None,
        category: str | None = None,
    ) -> list[RuleConfigResponse]:
        query = select(RuleConfig).order_by(RuleConfig.priority.asc(), RuleConfig.name.asc())
        if is_enabled is not None:
            query = query.where(RuleConfig.is_enabled == is_enabled)
        if category:
            query = query.where(RuleConfig.category == category)
        rows = db.scalars(query).all()
        return [RuleConfigResponse.model_validate(row) for row in rows]

    def get_rule(self, db: Session, rule_id: str) -> RuleConfigResponse:
        rule = db.get(RuleConfig, rule_id)
        if rule is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rule config '{rule_id}' not found.",
            )
        return RuleConfigResponse.model_validate(rule)

    def get_rule_by_name(self, db: Session, name: str) -> RuleConfigResponse | None:
        rule = db.scalars(select(RuleConfig).where(RuleConfig.name == name).limit(1)).first()
        if rule is None:
            return None
        return RuleConfigResponse.model_validate(rule)

    def create_rule(self, db: Session, payload: RuleConfigCreate) -> RuleConfigResponse:
        existing = db.scalars(select(RuleConfig).where(RuleConfig.name == payload.name).limit(1)).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Rule with name '{payload.name}' already exists.",
            )

        rule = RuleConfig(
            id=f"rule-{uuid4().hex[:10]}",
            name=payload.name,
            title=payload.title,
            issue_type=payload.issue_type,
            level=payload.level,
            detail=payload.detail,
            suggestion=payload.suggestion,
            patterns=payload.patterns,
            document=payload.document,
            match_mode=payload.match_mode,
            is_enabled=payload.is_enabled,
            priority=payload.priority,
            category=payload.category,
            description=payload.description,
        )
        db.add(rule)
        db.commit()
        db.refresh(rule)
        return RuleConfigResponse.model_validate(rule)

    def update_rule(self, db: Session, rule_id: str, payload: RuleConfigUpdate) -> RuleConfigResponse:
        rule = db.get(RuleConfig, rule_id)
        if rule is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rule config '{rule_id}' not found.",
            )

        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(rule, key, value)

        db.commit()
        db.refresh(rule)
        return RuleConfigResponse.model_validate(rule)

    def delete_rule(self, db: Session, rule_id: str) -> None:
        rule = db.get(RuleConfig, rule_id)
        if rule is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rule config '{rule_id}' not found.",
            )
        db.delete(rule)
        db.commit()

    def get_active_rules(self, db: Session) -> list[RuleDefinition]:
        rows = db.scalars(
            select(RuleConfig)
            .where(RuleConfig.is_enabled == True)
            .order_by(RuleConfig.priority.asc())
        ).all()

        if not rows:
            return list(DEFAULT_RULES)

        return [
            RuleDefinition(
                name=row.name,
                title=row.title,
                issue_type=row.issue_type,
                level=row.level,
                detail=row.detail,
                suggestion=row.suggestion,
                patterns=tuple(json.loads(row.patterns)) if row.patterns else (),
                document=row.document,
                match_mode=row.match_mode,
            )
            for row in rows
        ]

    def initialize_default_rules(self, db: Session) -> int:
        count = 0
        for rule in DEFAULT_RULES:
            existing = db.scalars(select(RuleConfig).where(RuleConfig.name == rule.name).limit(1)).first()
            if existing:
                continue

            config = RuleConfig(
                id=f"rule-{uuid4().hex[:10]}",
                name=rule.name,
                title=rule.title,
                issue_type=rule.issue_type,
                level=rule.level,
                detail=rule.detail,
                suggestion=rule.suggestion,
                patterns=json.dumps(rule.patterns),
                document=rule.document,
                match_mode=rule.match_mode,
                is_enabled=True,
                priority=100,
                category=rule.issue_type,
                description=rule.detail[:200],
            )
            db.add(config)
            count += 1

        if count > 0:
            db.commit()
        return count

    def get_statistics(self, db: Session, rule_name: str | None = None) -> list[RuleStatisticsResponse]:
        query = select(RuleStatistics).order_by(RuleStatistics.hit_count.desc())
        if rule_name:
            query = query.where(RuleStatistics.rule_name == rule_name)
        rows = db.scalars(query).all()
        return [RuleStatisticsResponse.model_validate(row) for row in rows]

    def record_feedback(
        self,
        db: Session,
        rule_name: str,
        feedback_type: str,
    ) -> None:
        stats = db.scalars(select(RuleStatistics).where(RuleStatistics.rule_name == rule_name).limit(1)).first()
        if stats is None:
            stats = RuleStatistics(
                rule_name=rule_name,
                hit_count=0,
                confirmed_count=0,
                dismissed_count=0,
                modified_count=0,
                accuracy_rate=0.0,
            )
            db.add(stats)

        stats.hit_count += 1
        if feedback_type == "confirmed":
            stats.confirmed_count += 1
        elif feedback_type == "dismissed":
            stats.dismissed_count += 1
        elif feedback_type == "modified":
            stats.modified_count += 1

        total = stats.confirmed_count + stats.dismissed_count + stats.modified_count
        if total > 0:
            stats.accuracy_rate = stats.confirmed_count / total

        stats.last_feedback_at = datetime.utcnow()
        db.commit()


rule_config_service = RuleConfigService()
