import json
import logging
import math
from typing import Any

from app.schemas.tech_score import (
    TechScoreEvaluateRequest,
    TechScoreEvaluateResponse,
    ObjectiveScoreResult,
    ObjectiveScoreItem,
    SubjectiveScoreResult,
    SubjectiveScoreItem,
)
from app.services.llm_client import _BaseLLMClient

logger = logging.getLogger(__name__)


class _TechScoreLLMClient(_BaseLLMClient):
    def evaluate_subjective_items(
        self,
        subjective_items: list[dict],
        proposal_text: str,
        qualifications: list[str],
        cases: list[str],
    ) -> list[dict]:
        if not self.is_llm_ready:
            logger.warning("LLM not ready, falling back to heuristic subjective evaluation")
            return self._heuristic_subjective(subjective_items, proposal_text)

        system_prompt = (
            "你是招投标技术评分专家。"
            "根据提供的评分标准、企业资质、案例和方案内容，评估每个主观评分项应落在哪个档位。"
            "输出必须是 JSON 对象，不要带 Markdown 代码块。"
        )

        items_desc = []
        for item in subjective_items:
            tier_desc = []
            for t in item.get("tiers", []):
                tier_desc.append(
                    f"  第{t['tier']}档({t['min_score']}-{t['max_score']}分): {t['description']}"
                )
            items_desc.append(
                f"- {item['name']}(满分{item['max_score']}分)\n" + "\n".join(tier_desc)
            )

        schema = {
            "evaluations": [
                {
                    "name": "评分项名称",
                    "tier": 2,
                    "score": 12.0,
                    "confidence": 0.7,
                    "reasoning": "评估理由",
                    "references": ["引用依据1"]
                }
            ]
        }

        user_prompt = (
            f"评分标准:\n{chr(10).join(items_desc)}\n\n"
            f"企业资质: {json.dumps(qualifications, ensure_ascii=False)}\n"
            f"历史案例: {json.dumps(cases, ensure_ascii=False)}\n"
            f"方案内容:\n{proposal_text[:3000]}\n\n"
            f"请评估每个主观评分项的档位和分数。返回格式:\n"
            f"{json.dumps(schema, ensure_ascii=False)}"
        )

        try:
            content = self._chat_completion(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.3,
                max_tokens=2048,
            )
            if not content:
                return self._heuristic_subjective(subjective_items, proposal_text)

            payload = self._parse_json_payload(content.strip())
            return payload.get("evaluations", [])
        except Exception as exc:
            logger.warning("LLM subjective evaluation failed: %s", exc)
            return self._heuristic_subjective(subjective_items, proposal_text)

    def _heuristic_subjective(
        self, items: list[dict], proposal_text: str
    ) -> list[dict]:
        results = []
        text_len = len(proposal_text)
        for item in items:
            max_score = item.get("max_score", 20)
            if text_len > 2000:
                ratio = 0.75
            elif text_len > 500:
                ratio = 0.55
            else:
                ratio = 0.35
            score = round(max_score * ratio, 1)
            tier = 2 if ratio > 0.6 else 3
            results.append({
                "name": item.get("name", ""),
                "tier": tier,
                "score": score,
                "confidence": 0.4,
                "reasoning": "基于方案文本长度的启发式估算，建议人工确认",
                "references": [],
            })
        return results

    def verify_objective_items(
        self,
        criteria_items: list[dict],
        qualifications: list[str],
        cases: list[str],
        technical_params: list[str],
    ) -> list[dict]:
        if not self.is_llm_ready:
            logger.info("LLM not ready, skipping objective item AI verification")
            return []

        system_prompt = (
            "你是招投标技术评分校验专家。"
            "根据评分项要求和企业提供的材料，校验每个客观评分项的匹配情况。"
            "识别哪些要求已满足、哪些缺失，给出匹配率和缺失清单。"
            "输出必须是 JSON 对象，不要带 Markdown 代码块。"
        )

        items_desc = []
        for item in criteria_items:
            items_desc.append(
                f"- {item.get('name', '')}(满分{item.get('max_score', 100)}分, 权重{item.get('weight', 1.0)})"
            )

        schema = {
            "verifications": [
                {
                    "name": "评分项名称",
                    "matched_count": 3,
                    "total_required": 5,
                    "match_ratio": 0.6,
                    "missing": ["缺失项1", "缺失项2"],
                    "detail": "校验详情"
                }
            ]
        }

        user_prompt = (
            f"评分项:\n{chr(10).join(items_desc)}\n\n"
            f"企业资质: {json.dumps(qualifications, ensure_ascii=False)}\n"
            f"历史案例: {json.dumps(cases, ensure_ascii=False)}\n"
            f"技术参数响应: {json.dumps(technical_params, ensure_ascii=False)}\n\n"
            f"请校验每个客观评分项的匹配情况。返回格式:\n"
            f"{json.dumps(schema, ensure_ascii=False)}"
        )

        try:
            content = self._chat_completion(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.2,
                max_tokens=2048,
            )
            if not content:
                return []
            payload = self._parse_json_payload(content.strip())
            return payload.get("verifications", [])
        except Exception as exc:
            logger.warning("LLM objective verification failed: %s", exc)
            return []


_llm_client = _TechScoreLLMClient()


def _evaluate_objective_items(
    criteria_items: list[dict],
    qualifications: list[str],
    cases: list[str],
    technical_params: list[str],
    manual_score: float | None,
) -> ObjectiveScoreResult:
    if manual_score is not None:
        return ObjectiveScoreResult(
            total=manual_score,
            items=[ObjectiveScoreItem(
                name="手动输入客观分", score=manual_score,
                max_score=100, matched=True, detail="用户手动输入"
            )],
            confidence=1.0,
        )

    ai_verifications = _llm_client.verify_objective_items(
        criteria_items=criteria_items,
        qualifications=qualifications,
        cases=cases,
        technical_params=technical_params,
    )

    ai_verification_map: dict[str, dict] = {}
    for v in ai_verifications:
        ai_verification_map[v.get("name", "")] = v

    items = []
    total = 0.0
    for ci in criteria_items:
        name = ci.get("name", "")
        max_score = ci.get("max_score", 100)
        weight = ci.get("weight", 1.0)

        matched_count = 0
        total_required = 1
        detail_parts = []
        ai_verified = False
        ai_detail = ""
        missing_items: list[str] = []

        ai_v = ai_verification_map.get(name)
        if ai_v:
            ai_verified = True
            matched_count = int(ai_v.get("matched_count", 0))
            total_required = max(1, int(ai_v.get("total_required", 1)))
            ai_detail = str(ai_v.get("detail", ""))
            missing_items = ai_v.get("missing", [])
            ratio = float(ai_v.get("match_ratio", matched_count / total_required if total_required > 0 else 0.5))
            detail_parts.append(f"AI校验: 匹配{matched_count}/{total_required}项")
            if missing_items:
                detail_parts.append(f"缺失: {', '.join(missing_items[:5])}")
        else:
            if "资质" in name:
                matched_count = len(qualifications)
                total_required = max(1, matched_count)
                detail_parts.append(f"提供{matched_count}项资质")
            elif "案例" in name or "业绩" in name:
                matched_count = len(cases)
                total_required = max(1, matched_count)
                detail_parts.append(f"提供{matched_count}个案例")
            elif "参数" in name:
                matched_count = len(technical_params)
                total_required = max(1, matched_count)
                detail_parts.append(f"响应{matched_count}项参数")
            else:
                matched_count = max(1, len(qualifications) + len(cases))
                total_required = max(1, matched_count)
                detail_parts.append(f"综合匹配{matched_count}项")

            ratio = min(1.0, matched_count / total_required) if total_required > 0 else 0.5

        score = round(max_score * ratio * weight, 2)
        total += score

        items.append(ObjectiveScoreItem(
            name=name, score=score, max_score=max_score,
            matched=ratio >= 0.8, detail="; ".join(detail_parts),
            ai_verified=ai_verified,
            ai_verification_detail=ai_detail,
            missing_items=missing_items,
        ))

    confidence = 0.9 if ai_verifications else (0.85 if qualifications or cases else 0.5)
    return ObjectiveScoreResult(total=round(total, 2), items=items, confidence=confidence)


def evaluate_tech_score(payload: TechScoreEvaluateRequest) -> TechScoreEvaluateResponse:
    logger.info("Evaluating tech score for project: %s", payload.project_id)

    criteria = payload.scoring_criteria
    materials = payload.company_materials

    objective_result = _evaluate_objective_items(
        criteria_items=[item.model_dump() for item in criteria.objective_items],
        qualifications=materials.qualifications,
        cases=materials.cases,
        technical_params=materials.technical_params,
        manual_score=payload.manual_objective_score,
    )

    subjective_items_data = [item.model_dump() for item in criteria.subjective_items]
    if not subjective_items_data:
        subjective_result = SubjectiveScoreResult(items=[], total=0.0)
    else:
        raw_evals = _llm_client.evaluate_subjective_items(
            subjective_items=subjective_items_data,
            proposal_text=materials.proposal_text,
            qualifications=materials.qualifications,
            cases=materials.cases,
        )

        subj_items = []
        subj_total = 0.0
        for raw in raw_evals:
            name = raw.get("name", "")
            matching_criteria = next(
                (c for c in criteria.subjective_items if c.name == name), None
            )
            if not matching_criteria:
                continue

            ai_tier = max(1, min(4, int(raw.get("tier", 3))))
            ai_score = min(float(raw.get("score", 0)), matching_criteria.max_score)
            confidence = max(0.0, min(1.0, float(raw.get("confidence", 0.5))))
            reasoning = str(raw.get("reasoning", ""))
            references = raw.get("references", [])

            subj_items.append(SubjectiveScoreItem(
                name=name, ai_tier=ai_tier, ai_score=round(ai_score, 2),
                max_score=matching_criteria.max_score, confidence=confidence,
                reasoning=reasoning, references=references,
            ))
            subj_total += ai_score

        subjective_result = SubjectiveScoreResult(
            items=subj_items, total=round(subj_total, 2)
        )

    total_tech = objective_result.total + subjective_result.total

    obj_conf = objective_result.confidence
    subj_conf_values = [s.confidence for s in subjective_result.items] or [0.5]
    avg_subj_conf = sum(subj_conf_values) / len(subj_conf_values)
    combined_conf = (obj_conf * 0.6 + avg_subj_conf * 0.4)

    margin = (1 - combined_conf) * total_tech * 0.5
    confidence_range = [
        round(max(0, total_tech - margin), 2),
        round(min(100, total_tech + margin), 2),
    ]

    needs_manual = avg_subj_conf < 0.7 or len(subjective_result.items) > 0

    return TechScoreEvaluateResponse(
        objective_score=objective_result,
        subjective_score=subjective_result,
        total_tech_score=round(total_tech, 2),
        confidence_range=confidence_range,
        needs_manual_review=needs_manual,
    )
