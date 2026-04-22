from pydantic import BaseModel, ConfigDict, Field


class ProposalSectionSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    section_name: str
    score: int
    is_confirmed: bool
    is_generated: bool


class ProposalSectionDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    section_name: str
    content: str
    score: int
    is_confirmed: bool
    is_generated: bool


class ProposalSectionUpdateRequest(BaseModel):
    content: str | None = Field(default=None)
    is_confirmed: bool | None = Field(default=None)


class ProposalScoreResponse(BaseModel):
    sections: list[ProposalSectionSummary]
    total_score: int


# 评分标准定义（对应技术打分表）
# 分项得分 = 基础分 + 加分项
SCORING_RULES = {
    "整体解决方案": {"max": 100, "weight": 0.15, "criteria": "完整性、创新性，可落地性"},
    "软件架构": {"max": 100, "weight": 0.12, "criteria": "架构合理性，扩展性，先进性"},
    "功能实现方案": {"max": 100, "weight": 0.18, "criteria": "功能覆盖度，实现难度，关键技术"},
    "系统接口方案": {"max": 100, "weight": 0.10, "criteria": "接口规范，兼容性，安全性"},
    "部署方案": {"max": 100, "weight": 0.08, "criteria": "部署可行性，运维便捷性"},
    "兼容性": {"max": 100, "weight": 0.05, "criteria": "与客户现有系统兼容性"},
    "系统安全": {"max": 100, "weight": 0.10, "criteria": "安全等级，数据保护，应急响应"},
    "项目经理能力": {"max": 100, "weight": 0.08, "criteria": "PMP认证，类似项目经验"},
    "人员能力": {"max": 100, "weight": 0.07, "criteria": "资质证书，技术认证，团队配置"},
    "维保期限": {"max": 100, "weight": 0.07, "criteria": "维保期长度，服务响应承诺"},
}


class ProposalGenerationRequest(BaseModel):
    include_client_bg: bool = True      # 包含客户背景
    include_company_bg: bool = True    # 包含公司背景
    reference_scoring: bool = True     # 参考技术打分表