from app.schemas.pricing import (
    PricingCalculateRequest,
    PricingCalculateResponse,
    PricingBreakdown,
    CompetitorResult,
    PricingScores,
)
from typing import List
import json
import logging

from app.services.llm_client import _BaseLLMClient

logger = logging.getLogger(__name__)


class _PricingLLMClient(_BaseLLMClient):
    def generate_pricing_advice(
        self,
        tech_score: float,
        our_rank: int,
        price_score: float,
        profit_margin: float,
        discount_rate: float,
        budget: float,
        competitor_summary: str,
    ) -> str | None:
        if not self.is_llm_ready:
            return None

        system_prompt = (
            "你是招投标报价策略顾问。"
            "根据当前报价参数和竞争态势，给出简洁专业的策略建议（不超过80字）。"
            "建议应包含具体行动方向，不要泛泛而谈。"
        )

        user_prompt = (
            f"当前报价状态：\n"
            f"- 技术分: {tech_score}分\n"
            f"- 我方排名: 第{our_rank}名\n"
            f"- 价格得分: {price_score:.1f}分\n"
            f"- 利润率: {profit_margin}%\n"
            f"- 折扣率: {discount_rate:.2f}%\n"
            f"- 项目预算: ¥{budget:,.0f}\n"
            f"- 竞争态势: {competitor_summary}\n\n"
            "请给出报价策略建议。"
        )

        try:
            content = self._chat_completion(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.4,
                max_tokens=256,
            )
            if content:
                return content.strip()
            return None
        except Exception as exc:
            logger.warning("LLM pricing advice generation failed: %s", exc)
            return None


_pricing_llm = _PricingLLMClient()


def _calc_average(values: List[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def _calc_vertex_benchmark(review_prices: List[float], k_value: float) -> float:
    """顶点中间值法基准价计算"""
    if not review_prices:
        return 0.0
    if len(review_prices) <= 5:
        return _calc_average(review_prices) * k_value

    sorted_prices = sorted(review_prices)
    # 去掉最高和最低
    trimmed = sorted_prices[1:-1]
    if not trimmed:
        return _calc_average(sorted_prices) * k_value

    avg = _calc_average(trimmed)
    if avg == 0:
        return 0.0

    # 去掉偏离超过20%的
    filtered = [p for p in trimmed if abs(p - avg) / avg <= 0.2]
    final_list = filtered if filtered else trimmed
    return _calc_average(final_list) * k_value


def _calc_vertex_score(d1: float, d: float, e: float = 1.0) -> float:
    """顶点中间值法价格得分"""
    if not d:
        return 0.0
    if d1 == d:
        return 100.0
    if d1 > d:
        return max(0.0, 100 - (abs(d1 - d) / d) * 100 * e)
    return max(0.0, 100 - (abs(d1 - d) / d) * 100 * (e / 2))


def _calc_linear_score(d1: float, d2: float, d: float, lambda_val: float) -> float:
    """线性评分法价格得分"""
    if not d or not lambda_val:
        return 0.0
    return max(0.0, 100 - (d1 - d2) / (d * lambda_val))


def _run_simulation(
    our_inc_tax_price: float,
    budget: float,
    tax_rate: float,
    competitors: List[dict],
    pricing_method: str,
    k_value: float,
    sensitivity: float,
    effective_bidder_count: int,
) -> tuple:
    """运行竞商模拟，返回 (scored_rows, benchmark, min_review_price)"""

    our_ex_tax_price = our_inc_tax_price / (1 + tax_rate)
    our_discount_rate = ((budget - our_inc_tax_price) / budget * 100) if budget > 0 else 0

    rows = [
        {
            "id": "our",
            "name": "我方报价",
            "is_our": True,
            "inc_tax_price": our_inc_tax_price,
            "ex_tax_price": our_ex_tax_price,
            "quote_price": our_inc_tax_price,
            "discount_rate": max(0.0, min(100.0, our_discount_rate)),
        }
    ]

    for c in competitors:
        dr = max(0.0, min(100.0, c.get("discount_rate", 0)))
        quote_price = budget * (1 - dr / 100)
        rows.append(
            {
                "id": str(c.get("id", "")),
                "name": c.get("name", "未知公司"),
                "is_our": False,
                "inc_tax_price": quote_price,
                "ex_tax_price": quote_price / (1 + tax_rate),
                "quote_price": quote_price,
                "discount_rate": dr,
            }
        )

    # 计算评审价
    lambda_val = sensitivity / 100
    if pricing_method in ("vertexRandomK", "vertexFixedK"):
        review_prices = [1 - r["discount_rate"] / 100 for r in rows]
    else:
        review_prices = [r["quote_price"] for r in rows]

    # 基准价
    k = k_value / 100 if pricing_method == "vertexRandomK" else (0.9 if pricing_method == "vertexFixedK" else None)
    if pricing_method in ("vertexRandomK", "vertexFixedK"):
        benchmark = _calc_vertex_benchmark(review_prices, k)
    else:
        benchmark = _calc_average(review_prices)

    min_review_price = min(review_prices)

    # 评分
    scored_rows = []
    for i, row in enumerate(rows):
        d1 = review_prices[i]
        if pricing_method in ("vertexRandomK", "vertexFixedK"):
            raw_score = _calc_vertex_score(d1, benchmark, 1.0)
        else:
            raw_score = _calc_linear_score(d1, min_review_price, benchmark, lambda_val)

        price_score = max(0.0, round(raw_score, 2))
        scored_rows.append({**row, "review_price": d1, "price_score": price_score})

    # 排序
    scored_rows.sort(key=lambda r: (-r["price_score"], r["quote_price"]))
    for idx, row in enumerate(scored_rows):
        row["rank"] = idx + 1

    return scored_rows, benchmark, min_review_price


def _calc_price_score_component(
    inc_tax_price: float, budget: float, profit_margin: float, risk_factor: int
) -> PricingScores:
    """计算价格竞争力、利润合理性、风险可控性"""
    budget_ratio = inc_tax_price / budget if budget > 0 else 0

    if budget_ratio < 0.9:
        price_competitiveness = 90.0
    elif budget_ratio < 0.95:
        price_competitiveness = 80.0
    elif budget_ratio < 1.0:
        price_competitiveness = 70.0
    else:
        price_competitiveness = 50.0

    if 15 <= profit_margin <= 22:
        profit_reasonability = 90.0
    elif profit_margin < 10 or profit_margin > 25:
        profit_reasonability = 60.0
    else:
        profit_reasonability = 75.0

    if risk_factor <= 2:
        risk_controllability = 90.0
    elif risk_factor >= 4:
        risk_controllability = 65.0
    else:
        risk_controllability = 80.0

    return PricingScores(
        price_competitiveness=round(price_competitiveness, 2),
        profit_reasonability=round(profit_reasonability, 2),
        risk_controllability=round(risk_controllability, 2),
    )


def _generate_ai_advice(
    tech_score: float,
    our_rank: int,
    price_score: float,
    profit_margin: float,
    discount_rate: float = 0.0,
    budget: float = 0.0,
    competitor_summary: str = "",
) -> str:
    """Generate AI advice: LLM-first with rule-based fallback"""
    if tech_score < 60:
        return "技术分低于60分，不得参与报价分评审。请先提高技术方案质量。"

    llm_advice = _pricing_llm.generate_pricing_advice(
        tech_score=tech_score,
        our_rank=our_rank,
        price_score=price_score,
        profit_margin=profit_margin,
        discount_rate=discount_rate,
        budget=budget,
        competitor_summary=competitor_summary,
    )
    if llm_advice:
        logger.info("LLM pricing advice generated successfully")
        return llm_advice

    logger.info("LLM pricing advice unavailable, falling back to rule-based advice")

    if our_rank == 1 and price_score >= 90:
        return "当前报价在模拟对手中排名靠前且价格得分高，建议保持并关注利润空间。"

    if 1 <= our_rank <= 3:
        base = "当前报价具备竞争力，可微调折扣率并复算，观察排名变化后再定稿。"
        if profit_margin < 12:
            return base + " 利润空间偏低，建议适当提升利润率以降低风险。"
        if profit_margin > 25:
            return base + " 利润空间较高，注意市场竞争力。"
        return base

    return "当前模拟排名偏后，建议适当提高折扣率或优化成本结构后再次测算。"


def calculate_pricing(payload: PricingCalculateRequest) -> PricingCalculateResponse:
    """报价计算主函数"""

    # 计算含税/不含税价格
    if payload.inc_tax_price is not None:
        inc_tax_price = payload.inc_tax_price
        ex_tax_price = inc_tax_price / (1 + payload.tax_rate)
    elif payload.ex_tax_price is not None:
        ex_tax_price = payload.ex_tax_price
        inc_tax_price = ex_tax_price * (1 + payload.tax_rate)
    else:
        ex_tax_price = 0.0
        inc_tax_price = 0.0

    ex_tax_price = round(ex_tax_price, 2)
    inc_tax_price = round(inc_tax_price, 2)

    # 成本
    profit_factor = 1 + payload.profit_margin / 100
    ex_tax_cost = round(ex_tax_price / profit_factor, 2) if profit_factor > 0 else 0.0
    inc_tax_cost = round(ex_tax_cost * (1 + payload.tax_rate), 2)

    # 折扣率
    budget = payload.budget or 0
    if budget > 0 and inc_tax_price > 0:
        discount_rate = round((budget - inc_tax_price) / budget * 100, 4)
    else:
        discount_rate = 0.0

    # 竞品数据
    competitors = [
        {"id": c.name, "name": c.name, "discount_rate": c.discount_rate}
        for c in payload.competitors
    ]

    # 模拟
    scored_rows, benchmark, min_review_price = _run_simulation(
        our_inc_tax_price=inc_tax_price,
        budget=budget,
        tax_rate=payload.tax_rate,
        competitors=competitors,
        pricing_method=payload.pricing_method,
        k_value=payload.k_value,
        sensitivity=payload.sensitivity,
        effective_bidder_count=payload.effective_bidder_count,
    )

    our_row = next((r for r in scored_rows if r["is_our"]), None)
    our_rank = our_row["rank"] if our_row else 0
    our_price_score = our_row["price_score"] if our_row else 0.0

    # 各维度得分
    scores = _calc_price_score_component(
        inc_tax_price, budget, payload.profit_margin, payload.risk_factor
    )

    # 总得分 = 技术分*0.5 + 价格得分*0.5
    if payload.tech_score >= 60:
        total_score = round(payload.tech_score * 0.5 + our_price_score * 0.5, 2)
    else:
        total_score = 0.0

    competitor_summary_parts = []
    for r in scored_rows:
        if not r["is_our"]:
            competitor_summary_parts.append(
                f"{r['name']}(折扣{r['discount_rate']:.1f}%, 得分{r['price_score']:.1f})"
            )
    competitor_summary = "; ".join(competitor_summary_parts) if competitor_summary_parts else "无竞商数据"

    ai_advice = _generate_ai_advice(
        tech_score=payload.tech_score,
        our_rank=our_rank,
        price_score=our_price_score,
        profit_margin=payload.profit_margin,
        discount_rate=discount_rate,
        budget=budget,
        competitor_summary=competitor_summary,
    )

    breakdown = PricingBreakdown(
        ex_tax_price=ex_tax_price,
        inc_tax_price=inc_tax_price,
        ex_tax_cost=ex_tax_cost,
        inc_tax_cost=inc_tax_cost,
        discount_rate=discount_rate,
        profit_margin=payload.profit_margin,
        tax_rate=payload.tax_rate,
    )

    competitor_results = [
        CompetitorResult(
            id=r["id"],
            name=r["name"],
            is_our=r["is_our"],
            quote_price=round(r["quote_price"], 2),
            discount_rate=round(r["discount_rate"], 4),
            price_score=r["price_score"],
            rank=r["rank"],
        )
        for r in scored_rows
    ]

    return PricingCalculateResponse(
        success=True,
        message="计算成功",
        breakdown=breakdown,
        competitors=competitor_results,
        our_rank=our_rank,
        our_price_score=our_price_score,
        benchmark_price=round(benchmark, 4),
        min_review_price=round(min_review_price, 4),
        total_score=total_score,
        scores=scores,
        ai_advice=ai_advice,
    )
