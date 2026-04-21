# sale-agents-v2: pricing module
# 报价策略计算模块
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.session import get_db

router = APIRouter()


# ============ Request/Response Schemas ============

class PricingCalculateRequest(BaseModel):
    """报价计算请求"""
    project_id: str | None = Field(default=None, description="项目ID")
    budget: float | None = Field(default=None, description="预算上限")
    ex_tax_price: float | None = Field(default=None, description="不含税报价")
    inc_tax_price: float | None = Field(default=None, description="含税报价")
    tax_rate: float = Field(default=0.06, description="税率")
    profit_margin: float = Field(default=15.0, ge=0, le=100, description="利润率(%)")
    risk_factor: float = Field(default=3.0, ge=1, le=5, description="风险系数(1-5)")
    pricing_method: str = Field(default="linear", description="价格评分方法: vertexRandomK/vertexFixedK/linear")
    k_value: float = Field(default=95.0, ge=90, le=100, description="K值(%)")
    sensitivity: float = Field(default=2.0, ge=0.5, le=5, description="敏感系数λ(%)")
    tech_score: float = Field(default=75.0, ge=0, le=100, description="技术分")
    competitors: list[dict] = Field(default_factory=list, description="竞品列表 [{name, discount_rate}]")


class CompetitorResult(BaseModel):
    """竞品计算结果"""
    id: str
    name: str
    is_our: bool
    quote_price: float
    discount_rate: float
    price_score: float
    rank: int


class PricingBreakdown(BaseModel):
    """报价明细"""
    ex_tax_price: float
    inc_tax_price: float
    ex_tax_cost: float
    inc_tax_cost: float
    discount_rate: float
    profit_margin: float
    tax_rate: float


class PricingCalculateResponse(BaseModel):
    """报价计算响应"""
    success: bool = True
    message: str = ""
    # 报价明细
    breakdown: PricingBreakdown | None = None
    # 竞品模拟结果
    competitors: list[CompetitorResult] = []
    our_rank: int = 0
    our_price_score: float = 0
    # 基准价
    benchmark_price: float = 0
    min_review_price: float = 0
    # 评分
    total_score: float = 0
    scores: dict = {}
    # AI建议
    ai_advice: str = ""


# ============ 计算逻辑 ============

def calc_average(values: list[float]) -> float:
    """计算平均值"""
    if not values:
        return 0
    return sum(values) / len(values)


def calc_vertex_benchmark(review_prices: list[float], k_value: float) -> float:
    """顶点中间值法计算基准价"""
    if not review_prices:
        return 0
    
    n = len(review_prices)
    
    # 有效应答人数量 ≤5：全部参与计算
    if n <= 5:
        return calc_average(review_prices) * k_value
    
    # 有效应答人数量 >5：去掉最高和最低价后计算
    sorted_prices = sorted(review_prices)
    trimmed = sorted_prices[1:-1]  # 去掉最高和最低
    
    if not trimmed:
        return calc_average(sorted_prices) * k_value
    
    # 判断是否有偏离值（与平均值偏差超过20%）
    avg = calc_average(trimmed)
    if avg == 0:
        return calc_average(trimmed) * k_value
    
    filtered = [p for p in trimmed if abs(p - avg) / avg <= 0.2]
    final_list = filtered if filtered else trimmed
    
    return calc_average(final_list) * k_value


def calc_vertex_score(d1: float, d: float, e: float = 1.0) -> float:
    """顶点中间值法价格得分"""
    if not d:
        return 0
    if d1 == d:
        return 100
    if d1 > d:
        return max(0, 100 - abs(d1 - d) / d * 100 * e)
    return max(0, 100 - abs(d1 - d) / d * 100 * (e / 2))


def calc_linear_score(d1: float, d2: float, d: float, lambda_val: float) -> float:
    """线性评分法价格得分"""
    if not d or not lambda_val:
        return 0
    return max(0, 100 - (d1 - d2) / (d * lambda_val))


def run_simulation(
    budget: float,
    our_inc_tax_price: float,
    tax_rate: float,
    profit_margin: float,
    pricing_method: str,
    k_value: float,
    sensitivity: float,
    competitors: list[dict]
) -> dict:
    """运行竞品报价模拟"""
    # 计算我方折扣率
    if budget > 0:
        our_discount_rate = ((budget - our_inc_tax_price) / budget) * 100
        our_discount_rate = max(0, min(100, our_discount_rate))
    else:
        our_discount_rate = 0
    
    our_ex_tax_price = our_inc_tax_price / (1 + tax_rate)
    our_ex_tax_cost = our_ex_tax_price / (1 + profit_margin / 100)
    our_inc_tax_cost = our_ex_tax_cost * (1 + tax_rate)
    
    # 构建所有报价方
    rows = [
        {
            "id": "our",
            "name": "我方报价",
            "is_our": True,
            "quote_price": max(our_inc_tax_price, 0),
            "discount_rate": our_discount_rate
        }
    ]
    
    for idx, comp in enumerate(competitors):
        discount_rate = max(0, min(100, comp.get("discount_rate", 0)))
        quote_price = budget * (1 - discount_rate / 100) if budget > 0 else 0
        rows.append({
            "id": f"comp_{idx}",
            "name": comp.get("name", f"竞品{idx + 1}"),
            "is_our": False,
            "quote_price": max(quote_price, 0),
            "discount_rate": discount_rate
        })
    
    # 计算评审价
    method = pricing_method
    review_prices = []
    for row in rows:
        if method in ("vertexRandomK", "vertexFixedK"):
            # 折扣报价：评审价 = 1 - 折扣率
            review_prices.append(1 - row["discount_rate"] / 100)
        else:
            # 线性法：评审价 = 报价金额
            review_prices.append(row["quote_price"])
    
    # 计算基准价
    lambda_val = sensitivity / 100
    min_review_price = min(review_prices)
    
    if method == "vertexRandomK":
        benchmark = calc_vertex_benchmark(review_prices, k_value / 100)
    elif method == "vertexFixedK":
        benchmark = calc_vertex_benchmark(review_prices, 0.9)
    else:
        benchmark = calc_average(review_prices)
    
    # 计算价格得分
    scored_rows = []
    for i, row in enumerate(rows):
        d1 = review_prices[i]
        if method in ("vertexRandomK", "vertexFixedK"):
            raw_score = calc_vertex_score(d1, benchmark, 1)
        else:
            raw_score = calc_linear_score(d1, min_review_price, benchmark, lambda_val)
        
        price_score = max(0, round(raw_score * 100) / 100)
        scored_rows.append({
            **row,
            "review_price": d1,
            "price_score": price_score
        })
    
    # 排序（按价格得分降序，得分相同按报价升序）
    scored_rows.sort(key=lambda x: (-x["price_score"], x["quote_price"]))
    
    # 添加排名
    for i, row in enumerate(scored_rows):
        row["rank"] = i + 1
    
    return {
        "rows": scored_rows,
        "benchmark": benchmark,
        "min_review_price": min_review_price
    }


def calculate_pricing_scores(
    total_price: float,
    budget: float,
    profit_margin: float,
    risk_factor: float
) -> dict:
    """计算各项评分"""
    # 价格竞争力
    budget_ratio = total_price / budget if budget > 0 else 0
    if budget_ratio < 0.9:
        price_competitiveness = 90
    elif budget_ratio < 0.95:
        price_competitiveness = 80
    elif budget_ratio < 1:
        price_competitiveness = 70
    else:
        price_competitiveness = 50
    
    # 利润合理性
    if 15 <= profit_margin <= 22:
        profit_reasonability = 90
    elif profit_margin < 10 or profit_margin > 25:
        profit_reasonability = 60
    else:
        profit_reasonability = 75
    
    # 风险可控性
    if risk_factor <= 2:
        risk_controllability = 90
    elif risk_factor >= 4:
        risk_controllability = 65
    else:
        risk_controllability = 80
    
    return {
        "price_competitiveness": round(price_competitiveness, 2),
        "profit_reasonability": round(profit_reasonability, 2),
        "risk_controllability": round(risk_controllability, 2)
    }


def generate_ai_advice(
    tech_score: float,
    our_rank: int,
    price_score: float
) -> str:
    """生成AI建议"""
    if tech_score < 60:
        return "技术分低于60分，不得参与报价分评审。请先提高技术方案质量。"
    
    if our_rank == 1 and price_score >= 90:
        return "当前报价在模拟对手中排名靠前且价格得分高，建议保持并关注利润空间。"
    
    if 1 < our_rank <= 3:
        return "当前报价具备竞争力，可微调折扣率并复算，观察排名变化后再定稿。"
    
    return "当前模拟排名偏后，建议适当提高折扣率或优化成本结构后再次测算。"


# ============ API Routes ============

@router.post("/calculate", response_model=PricingCalculateResponse)
def calculate_pricing(
    payload: PricingCalculateRequest,
    db: Session = Depends(get_db)
) -> PricingCalculateResponse:
    """
    计算报价策略
    
    根据输入的参数计算报价、竞品模拟得分和总评分
    """
    try:
        # 解析参数
        budget = payload.budget or 0
        tax_rate = payload.tax_rate
        profit_margin = payload.profit_margin
        risk_factor = payload.risk_factor
        pricing_method = payload.pricing_method
        k_value = payload.k_value
        sensitivity = payload.sensitivity
        tech_score = payload.tech_score
        competitors = payload.competitors or []
        
        # 计算含税/不含税报价
        if payload.inc_tax_price:
            inc_tax_price = payload.inc_tax_price
            ex_tax_price = inc_tax_price / (1 + tax_rate)
        elif payload.ex_tax_price:
            ex_tax_price = payload.ex_tax_price
            inc_tax_price = ex_tax_price * (1 + tax_rate)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="必须提供 ex_tax_price 或 inc_tax_price 其中之一"
            )
        
        # 运行竞品模拟
        sim_result = run_simulation(
            budget=budget,
            our_inc_tax_price=inc_tax_price,
            tax_rate=tax_rate,
            profit_margin=profit_margin,
            pricing_method=pricing_method,
            k_value=k_value,
            sensitivity=sensitivity,
            competitors=competitors
        )
        
        # 提取我方结果
        our_row = next((r for r in sim_result["rows"] if r["is_our"]), None)
        our_rank = our_row["rank"] if our_row else 0
        our_price_score = our_row["price_score"] if our_row else 0
        
        # 计算成本
        ex_tax_cost = ex_tax_price / (1 + profit_margin / 100)
        inc_tax_cost = ex_tax_cost * (1 + tax_rate)
        discount_rate = ((budget - inc_tax_price) / budget * 100) if budget > 0 else 0
        
        # 报价明细
        breakdown = PricingBreakdown(
            ex_tax_price=round(ex_tax_price, 2),
            inc_tax_price=round(inc_tax_price, 2),
            ex_tax_cost=round(ex_tax_cost, 2),
            inc_tax_cost=round(inc_tax_cost, 2),
            discount_rate=round(discount_rate, 2),
            profit_margin=profit_margin,
            tax_rate=tax_rate
        )
        
        # 各项评分
        scores = calculate_pricing_scores(
            total_price=inc_tax_price,
            budget=budget,
            profit_margin=profit_margin,
            risk_factor=risk_factor
        )
        
        # 总分（技术分50% + 价格分50%）
        if tech_score < 60:
            total_score = 0
        else:
            total_score = round(tech_score * 0.5 + our_price_score * 0.5, 2)
        
        # AI建议
        ai_advice = generate_ai_advice(tech_score, our_rank, our_price_score)
        
        return PricingCalculateResponse(
            success=True,
            message="计算成功",
            breakdown=breakdown,
            competitors=[CompetitorResult(**r) for r in sim_result["rows"]],
            our_rank=our_rank,
            our_price_score=our_price_score,
            benchmark_price=round(sim_result["benchmark"], 4),
            min_review_price=round(sim_result["min_review_price"], 2),
            total_score=total_score,
            scores=scores,
            ai_advice=ai_advice
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"计算报价策略失败: {str(e)}"
        )
