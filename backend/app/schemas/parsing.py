from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.workspace import ExtractedField, ParseSection


class ProjectDocumentVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    document_id: str
    project_id: str
    version_no: int
    file_name: str
    file_type: str
    document_type: str
    storage_backend: str
    object_key: str
    file_size: int
    parse_status: str
    created_at: datetime


class ProjectDocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    file_name: str
    file_type: str
    document_type: str
    parse_status: str
    created_at: datetime
    updated_at: datetime
    latest_version_no: int = 1
    versions: list[ProjectDocumentVersionResponse] = Field(default_factory=list)


class ProjectParsingContextResponse(BaseModel):
    project_id: str
    documents: list[ProjectDocumentResponse]
    parse_sections: list[ParseSection]
    extracted_fields: list[ExtractedField]
    source_excerpt: str = ""


class ProjectParsingRunResponse(BaseModel):
    project_id: str
    parse_sections: list[ParseSection]
    extracted_fields: list[ExtractedField]
    source_excerpt: str = ""


class ProjectParsingFieldUpdateRequest(BaseModel):
    value: str = Field(min_length=1, max_length=4000)


class ParsedFileInfo(BaseModel):
    file_name: str
    file_type: str
    parse_status: str
    document_type: str
    section_found: str = ""
    word_count: int = 0


class ProjectDocumentUploadResponse(BaseModel):
    document: ProjectDocumentResponse
    parse_sections: list[ParseSection]
    extracted_fields: list[ExtractedField]
    source_excerpt: str = ""
    parsed_files: list[ParsedFileInfo] = Field(default_factory=list)
