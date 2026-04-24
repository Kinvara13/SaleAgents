from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class TaskStatusResponse(BaseModel):
    """任务状态响应"""
    model_config = ConfigDict(from_attributes=True)

    id: str
    task_type: str
    project_id: str
    status: str  # pending, processing, completed, failed
    result: dict | None = None
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None


class TaskSubmitResponse(BaseModel):
    """任务提交响应"""
    task_id: str
    status: str
    message: str


class TaskListParams(BaseModel):
    """任务列表查询参数"""
    project_id: str | None = Field(default=None, description="按项目ID过滤")
    task_type: str | None = Field(default=None, description="按任务类型过滤")
    status: str | None = Field(default=None, description="按状态过滤")
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
