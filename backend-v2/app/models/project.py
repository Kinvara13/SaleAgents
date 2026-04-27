from datetime import datetime

from sqlalchemy import JSON, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(64), nullable=False, default="待决策")
    owner: Mapped[str] = mapped_column(String(128), nullable=False, default="admin")
    client: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    deadline: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    amount: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    risk: Mapped[str] = mapped_column(String(16), nullable=False, default="P2")
    # 投标项目清单 - 应标信息
    bidding_company: Mapped[str] = mapped_column(String(255), nullable=False, default="")  # 应标公司
    agent_name: Mapped[str] = mapped_column(String(128), nullable=False, default="")       # 代理人
    agent_phone: Mapped[str] = mapped_column(String(64), nullable=False, default="")        # 电话
    agent_email: Mapped[str] = mapped_column(String(128), nullable=False, default="")       # 邮箱
    company_address: Mapped[str] = mapped_column(String(512), nullable=False, default="")   # 公司地址
    bank_name: Mapped[str] = mapped_column(String(255), nullable=False, default="")         # 开户银行
    bank_account: Mapped[str] = mapped_column(String(128), nullable=False, default="")     # 银行账号
    description: Mapped[str] = mapped_column(String(2000), nullable=False, default="")      # 项目描述
    # 相关人员确认反馈
    confirm_status: Mapped[str] = mapped_column(String(32), nullable=False, default="待确认")  # 确认状态: 待确认/已确认
    confirm_feedback: Mapped[str] = mapped_column(String(1024), nullable=False, default="")   # 确认反馈
    confirmed_by: Mapped[str] = mapped_column(String(128), nullable=False, default="")       # 确认人
    confirmed_at: Mapped[str] = mapped_column(String(64), nullable=False, default="")           # 确认时间
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, default="user-001")   # 所属用户ID
    # === 解析与工作台链路字段（F052-F053） ===
    tender_id: Mapped[str] = mapped_column(String(64), nullable=False, default="")         # 关联招标信息ID
    parse_status: Mapped[str] = mapped_column(String(32), nullable=False, default="未上传")   # 未上传/解析中/已解析/解析失败
    file_list: Mapped[list | dict] = mapped_column(JSON, nullable=False, default=list)       # 上传文件清单 [{name, path, uploaded_at}]
    node_status: Mapped[list | dict] = mapped_column(JSON, nullable=False, default=dict)     # 节点工作台状态 {decision, parsing, generation, review}
    extracted_fields: Mapped[list | dict] = mapped_column(JSON, nullable=False, default=list) # LLM解析提取的字段 [{label, value, confidence}]
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )
