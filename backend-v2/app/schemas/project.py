from pydantic import BaseModel, ConfigDict, Field


class ProjectSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    status: str
    owner: str
    client: str = ""
    deadline: str = ""
    amount: str = ""
    risk: str = "P2"
    # 投标项目清单字段
    bidding_company: str = ""
    agent_name: str = ""
    agent_phone: str = ""
    agent_email: str = ""
    company_address: str = ""
    bank_name: str = ""
    bank_account: str = ""
    description: str = ""
    confirm_status: str = "待确认"
    confirm_feedback: str = ""
    confirmed_by: str = ""
    confirmed_at: str = ""
    user_id: str = "user-001"
    # === 解析与工作台链路（F052-F053） ===
    tender_id: str | None = None
    parse_status: str | None = None
    file_list: list | None = None
    node_status: dict | None = None
    extracted_fields: list | None = None


class ProjectCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    owner: str = Field(default="admin", max_length=128)
    user_id: str = Field(default="user-001", max_length=64)
    client: str = Field(default="", max_length=255)
    deadline: str = Field(default="", max_length=64)
    amount: str = Field(default="", max_length=64)
    risk: str = Field(default="P2", max_length=16)
    bidding_company: str = Field(default="", max_length=255)
    agent_name: str = Field(default="", max_length=128)
    agent_phone: str = Field(default="", max_length=64)
    agent_email: str = Field(default="", max_length=128)
    company_address: str = Field(default="", max_length=512)
    bank_name: str = Field(default="", max_length=255)
    bank_account: str = Field(default="", max_length=128)
    confirm_status: str = Field(default="待确认", max_length=32)
    description: str = Field(default="", max_length=2000)


class ProjectUpdateRequest(BaseModel):
    status: str | None = Field(default=None, max_length=64)
    name: str | None = Field(default=None, max_length=255)
    client: str | None = Field(default=None, max_length=255)
    deadline: str | None = Field(default=None, max_length=64)
    amount: str | None = Field(default=None, max_length=64)
    risk: str | None = Field(default=None, max_length=16)
    bidding_company: str | None = Field(default=None, max_length=255)
    agent_name: str | None = Field(default=None, max_length=128)
    agent_phone: str | None = Field(default=None, max_length=64)
    agent_email: str | None = Field(default=None, max_length=128)
    company_address: str | None = Field(default=None, max_length=512)
    bank_name: str | None = Field(default=None, max_length=255)
    bank_account: str | None = Field(default=None, max_length=128)
    confirm_status: str | None = Field(default=None, max_length=32)
    confirm_feedback: str | None = Field(default=None, max_length=1024)
    confirmed_by: str | None = Field(default=None, max_length=128)
    confirmed_at: str | None = Field(default=None, max_length=64)
    description: str | None = Field(default=None, max_length=2000)
    # === 解析与工作台（F052-F053） ===
    tender_id: str | None = Field(default=None, max_length=64)
    parse_status: str | None = Field(default=None, max_length=32)
    file_list: list | None = Field(default=None)
    node_status: dict | None = Field(default=None)
    extracted_fields: list | None = Field(default=None)


class BidFile(BaseModel):
    id: str
    name: str
    status: str
    icon: str = "📄"
    responsible: str = ""


class BidSection(BaseModel):
    id: int
    name: str
    icon: str
    completed: int
    total: int
    files: list[BidFile]


class BidProgress(BaseModel):
    sections: list[BidSection]


class ScoringCriteriaItem(BaseModel):
    primary: str
    secondary: str
    standard: str
    maxScore: int
    type: str
    estimatedScore: int
    isFirstInGroup: bool
    groupSpan: int = 1


class ProjectActivity(BaseModel):
    icon: str
    iconBg: str
    iconColor: str
    title: str
    time: str


class ProjectActivities(BaseModel):
    activities: list[ProjectActivity]
