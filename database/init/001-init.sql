-- ============================================================
-- SaleAgents V2 Database Schema
-- Generated from backend-v2/app/models/*.py
-- Last updated: 2026-04-28
-- ============================================================

-- 启用 vector 扩展（用于向量搜索）
CREATE EXTENSION IF NOT EXISTS vector;

-- 启动标记表
CREATE TABLE IF NOT EXISTS app_bootstrap_marker (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO app_bootstrap_marker (name)
VALUES ('bid-agent-bootstrap')
ON CONFLICT (name) DO NOTHING;

-- ============================================================
-- 用户与认证
-- ============================================================

CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(64) PRIMARY KEY,
    username VARCHAR(64) NOT NULL UNIQUE,
    password_hash VARCHAR(128) NOT NULL,
    name VARCHAR(128) NOT NULL DEFAULT '',
    role VARCHAR(32) NOT NULL DEFAULT 'executor',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 项目管理
-- ============================================================

CREATE TABLE IF NOT EXISTS projects (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    status VARCHAR(64) NOT NULL DEFAULT '待决策',
    owner VARCHAR(128) NOT NULL DEFAULT 'admin',
    client VARCHAR(255) NOT NULL DEFAULT '',
    deadline VARCHAR(64) NOT NULL DEFAULT '',
    amount VARCHAR(64) NOT NULL DEFAULT '',
    risk VARCHAR(16) NOT NULL DEFAULT 'P2',
    -- 应标信息
    bidding_company VARCHAR(255) NOT NULL DEFAULT '',
    agent_name VARCHAR(128) NOT NULL DEFAULT '',
    agent_phone VARCHAR(64) NOT NULL DEFAULT '',
    agent_email VARCHAR(128) NOT NULL DEFAULT '',
    company_address VARCHAR(512) NOT NULL DEFAULT '',
    bank_name VARCHAR(255) NOT NULL DEFAULT '',
    bank_account VARCHAR(128) NOT NULL DEFAULT '',
    description VARCHAR(2000) NOT NULL DEFAULT '',
    -- 确认反馈
    confirm_status VARCHAR(32) NOT NULL DEFAULT '待确认',
    confirm_feedback VARCHAR(1024) NOT NULL DEFAULT '',
    confirmed_by VARCHAR(128) NOT NULL DEFAULT '',
    confirmed_at VARCHAR(64) NOT NULL DEFAULT '',
    user_id VARCHAR(64) NOT NULL DEFAULT 'user-001',
    -- 解析与工作台
    tender_id VARCHAR(64) NOT NULL DEFAULT '',
    parse_status VARCHAR(32) NOT NULL DEFAULT '未上传',
    file_list TEXT NOT NULL DEFAULT '[]',
    node_status TEXT NOT NULL DEFAULT '{}',
    extracted_fields TEXT NOT NULL DEFAULT '[]',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 招标信息
-- ============================================================

CREATE TABLE IF NOT EXISTS tenders (
    id VARCHAR(64) PRIMARY KEY,
    title VARCHAR(512) NOT NULL DEFAULT '',
    source_url VARCHAR(1024) NOT NULL DEFAULT '',
    publish_date VARCHAR(64) NOT NULL DEFAULT '',
    deadline VARCHAR(64) NOT NULL DEFAULT '',
    amount VARCHAR(64) NOT NULL DEFAULT '',
    margin VARCHAR(64) NOT NULL DEFAULT '',
    project_type VARCHAR(128) NOT NULL DEFAULT '',
    description TEXT NOT NULL DEFAULT '',
    decision VARCHAR(32) NOT NULL DEFAULT 'pending',
    reject_reason VARCHAR(1024) NOT NULL DEFAULT '',
    project_id VARCHAR(64) NOT NULL DEFAULT '',
    service_commitment TEXT NOT NULL DEFAULT '',
    user_id VARCHAR(64) NOT NULL DEFAULT 'user-001',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 文档解析
-- ============================================================

CREATE TABLE IF NOT EXISTS parsing_sections (
    id VARCHAR(64) PRIMARY KEY,
    project_id VARCHAR(64) NOT NULL REFERENCES projects(id),
    section_name VARCHAR(255) NOT NULL,
    section_type VARCHAR(16) NOT NULL,
    content TEXT NOT NULL DEFAULT '',
    is_star_item BOOLEAN NOT NULL DEFAULT FALSE,
    source_file VARCHAR(255) NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 商务文档
-- ============================================================

CREATE TABLE IF NOT EXISTS business_documents (
    id VARCHAR(64) PRIMARY KEY,
    project_id VARCHAR(64) NOT NULL REFERENCES projects(id),
    doc_type VARCHAR(64) NOT NULL,
    doc_name VARCHAR(255) NOT NULL,
    original_content TEXT NOT NULL DEFAULT '',
    editable_content TEXT NOT NULL DEFAULT '',
    has_fillable_fields BOOLEAN NOT NULL DEFAULT FALSE,
    is_star_item BOOLEAN NOT NULL DEFAULT FALSE,
    score_point VARCHAR(512) NOT NULL DEFAULT '',
    rule_description TEXT NOT NULL DEFAULT '',
    status VARCHAR(32) NOT NULL DEFAULT 'pending',
    return_file_list TEXT NOT NULL DEFAULT '[]',
    source_file VARCHAR(255) NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 技术文档
-- ============================================================

CREATE TABLE IF NOT EXISTS technical_documents (
    id VARCHAR(64) PRIMARY KEY,
    project_id VARCHAR(64) NOT NULL REFERENCES projects(id),
    doc_type VARCHAR(64) NOT NULL,
    doc_name VARCHAR(255) NOT NULL,
    original_content TEXT NOT NULL DEFAULT '',
    editable_content TEXT NOT NULL DEFAULT '',
    has_fillable_fields BOOLEAN NOT NULL DEFAULT FALSE,
    is_star_item BOOLEAN NOT NULL DEFAULT FALSE,
    score_point VARCHAR(512) NOT NULL DEFAULT '',
    rule_description TEXT NOT NULL DEFAULT '',
    status VARCHAR(32) NOT NULL DEFAULT 'pending',
    return_file_list TEXT NOT NULL DEFAULT '[]',
    source_file VARCHAR(255) NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 方案建议书
-- ============================================================

CREATE TABLE IF NOT EXISTS proposal_plans (
    id VARCHAR(64) PRIMARY KEY,
    project_id VARCHAR(64) NOT NULL REFERENCES projects(id),
    doc_type VARCHAR(64) NOT NULL,
    doc_name VARCHAR(255) NOT NULL,
    original_content TEXT NOT NULL DEFAULT '',
    editable_content TEXT NOT NULL DEFAULT '',
    has_fillable_fields BOOLEAN NOT NULL DEFAULT FALSE,
    is_star_item BOOLEAN NOT NULL DEFAULT FALSE,
    score_point VARCHAR(512) NOT NULL DEFAULT '',
    rule_description TEXT NOT NULL DEFAULT '',
    status VARCHAR(32) NOT NULL DEFAULT 'pending',
    return_file_list TEXT NOT NULL DEFAULT '[]',
    source_file VARCHAR(255) NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 提案章节
-- ============================================================

CREATE TABLE IF NOT EXISTS proposal_sections (
    id VARCHAR(64) PRIMARY KEY,
    project_id VARCHAR(64) NOT NULL REFERENCES projects(id),
    section_name VARCHAR(255) NOT NULL,
    content TEXT NOT NULL DEFAULT '',
    score INTEGER NOT NULL DEFAULT 0,
    is_confirmed BOOLEAN NOT NULL DEFAULT FALSE,
    is_generated BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 技术案例
-- ============================================================

CREATE TABLE IF NOT EXISTS technical_cases (
    id VARCHAR(64) PRIMARY KEY,
    project_id VARCHAR(64) NOT NULL,
    title VARCHAR(255) NOT NULL,
    primary_review_item VARCHAR(128) NOT NULL DEFAULT '',
    secondary_review_item VARCHAR(128) NOT NULL DEFAULT '',
    case_type VARCHAR(64) NOT NULL DEFAULT '项目案例',
    scene_tags TEXT NOT NULL DEFAULT '[]',
    keywords TEXT NOT NULL DEFAULT '[]',
    summary TEXT NOT NULL DEFAULT '',
    contract_name VARCHAR(255) NOT NULL DEFAULT '',
    contract_amount VARCHAR(64) NOT NULL DEFAULT '',
    client_name VARCHAR(255) NOT NULL DEFAULT '',
    contract_overview TEXT NOT NULL DEFAULT '',
    key_highlights TEXT NOT NULL DEFAULT '',
    content TEXT NOT NULL DEFAULT '',
    score VARCHAR(32) NOT NULL DEFAULT '0.80',
    status VARCHAR(32) NOT NULL DEFAULT '可用',
    source VARCHAR(255) NOT NULL DEFAULT '',
    video_url VARCHAR(512) NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_technical_cases_project_id ON technical_cases(project_id);
CREATE INDEX IF NOT EXISTS idx_technical_cases_title ON technical_cases(title);

-- ============================================================
-- 标前评估
-- ============================================================

CREATE TABLE IF NOT EXISTS pre_evaluation_jobs (
    id VARCHAR(64) PRIMARY KEY,
    project_id VARCHAR(64),
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(512) NOT NULL DEFAULT '',
    status VARCHAR(32) NOT NULL DEFAULT 'pending',
    source_text TEXT NOT NULL DEFAULT '',
    review_method TEXT NOT NULL DEFAULT '{}',
    tech_review_table TEXT NOT NULL DEFAULT '[]',
    starred_items TEXT NOT NULL DEFAULT '[]',
    summary TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_pre_evaluation_jobs_project_id ON pre_evaluation_jobs(project_id);
CREATE INDEX IF NOT EXISTS idx_pre_evaluation_jobs_status ON pre_evaluation_jobs(status);

-- ============================================================
-- 聊天记录
-- ============================================================

CREATE TABLE IF NOT EXISTS chat_messages (
    id VARCHAR(64) PRIMARY KEY,
    project_id VARCHAR(64) NOT NULL REFERENCES projects(id),
    role VARCHAR(16) NOT NULL,
    content TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS chat_contexts (
    id VARCHAR(64) PRIMARY KEY,
    project_id VARCHAR(64) NOT NULL REFERENCES projects(id),
    context_type VARCHAR(32) NOT NULL,
    content TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- AI 配置与素材
-- ============================================================

CREATE TABLE IF NOT EXISTS ai_configs (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(128) NOT NULL DEFAULT '未命名配置',
    provider VARCHAR(32) NOT NULL DEFAULT 'zhipu',
    api_key VARCHAR(256) NOT NULL DEFAULT '',
    base_url VARCHAR(256) NOT NULL DEFAULT '',
    model VARCHAR(64) NOT NULL DEFAULT 'glm-4',
    temperature VARCHAR(16) NOT NULL DEFAULT '0.7',
    max_tokens INTEGER NOT NULL DEFAULT 4096,
    is_active BOOLEAN NOT NULL DEFAULT FALSE,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS materials (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(256) NOT NULL,
    category VARCHAR(64) NOT NULL DEFAULT 'other',
    tags TEXT NOT NULL DEFAULT '[]',
    content TEXT NOT NULL DEFAULT '',
    file_path VARCHAR(512) NOT NULL DEFAULT '',
    description VARCHAR(512) NOT NULL DEFAULT '',
    organization VARCHAR(256) NOT NULL DEFAULT '',
    acquired_date VARCHAR(32) NOT NULL DEFAULT '',
    valid_until VARCHAR(32) NOT NULL DEFAULT '',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    metadata_json TEXT NOT NULL DEFAULT '{}',
    material_type VARCHAR(64) NOT NULL DEFAULT 'general',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS rules (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(256) NOT NULL,
    rule_type VARCHAR(32) NOT NULL DEFAULT 'general',
    content TEXT NOT NULL DEFAULT '',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 工作台面板
-- ============================================================

CREATE TABLE IF NOT EXISTS workspace_panels (
    key VARCHAR(128) PRIMARY KEY,
    payload TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 异步任务
-- ============================================================

CREATE TABLE IF NOT EXISTS async_tasks (
    id VARCHAR(64) PRIMARY KEY,
    task_type VARCHAR(64) NOT NULL DEFAULT '',
    project_id VARCHAR(64) NOT NULL DEFAULT '',
    status VARCHAR(32) NOT NULL DEFAULT 'pending',
    result TEXT,
    error_message TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMPTZ
);

-- ============================================================
-- 文档评分历史
-- ============================================================

CREATE TABLE IF NOT EXISTS document_score_histories (
    id VARCHAR(64) PRIMARY KEY,
    project_id VARCHAR(64) NOT NULL,
    doc_id VARCHAR(64) NOT NULL,
    doc_kind VARCHAR(32) NOT NULL,
    score FLOAT NOT NULL,
    max_score FLOAT NOT NULL,
    breakdown TEXT NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_document_score_histories_project_id ON document_score_histories(project_id);
CREATE INDEX IF NOT EXISTS idx_document_score_histories_doc_id ON document_score_histories(doc_id);

-- ============================================================
-- 招标抓取日志
-- ============================================================

CREATE TABLE IF NOT EXISTS tender_fetch_logs (
    id SERIAL PRIMARY KEY,
    task_name VARCHAR(128) NOT NULL DEFAULT 'default_fetch',
    source VARCHAR(256) NOT NULL DEFAULT '',
    status VARCHAR(32) NOT NULL DEFAULT 'success',
    new_count INTEGER NOT NULL DEFAULT 0,
    updated_count INTEGER NOT NULL DEFAULT 0,
    error_message TEXT NOT NULL DEFAULT '',
    started_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMPTZ
);

-- ============================================================
-- 知识库
-- ============================================================

CREATE TABLE IF NOT EXISTS knowledge_assets_records (
    id VARCHAR(64) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    asset_type VARCHAR(64) NOT NULL DEFAULT '通用素材',
    score VARCHAR(32) NOT NULL DEFAULT '0.80',
    status VARCHAR(32) NOT NULL DEFAULT '可引用',
    summary TEXT NOT NULL DEFAULT '',
    keywords TEXT NOT NULL DEFAULT '',
    scene_tags TEXT NOT NULL DEFAULT '',
    section_tags TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_knowledge_assets_title ON knowledge_assets_records(title);

CREATE TABLE IF NOT EXISTS knowledge_asset_chunks_records (
    id VARCHAR(64) PRIMARY KEY,
    asset_id VARCHAR(64) NOT NULL,
    title VARCHAR(255) NOT NULL DEFAULT '',
    content TEXT NOT NULL DEFAULT '',
    keywords TEXT NOT NULL DEFAULT '',
    section_tags TEXT NOT NULL DEFAULT '',
    sort_order INTEGER NOT NULL DEFAULT 1,
    weight FLOAT NOT NULL DEFAULT 1.0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_asset_id ON knowledge_asset_chunks_records(asset_id);

CREATE TABLE IF NOT EXISTS knowledge_asset_sources_records (
    id VARCHAR(64) PRIMARY KEY,
    asset_id VARCHAR(64) NOT NULL,
    source_kind VARCHAR(32) NOT NULL DEFAULT 'manual',
    file_name VARCHAR(255) NOT NULL DEFAULT '',
    source_text TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_knowledge_sources_asset_id ON knowledge_asset_sources_records(asset_id);

CREATE TABLE IF NOT EXISTS knowledge_asset_index_jobs (
    id VARCHAR(64) PRIMARY KEY,
    asset_id VARCHAR(64) NOT NULL DEFAULT '',
    status VARCHAR(32) NOT NULL DEFAULT 'queued',
    triggered_by VARCHAR(128) NOT NULL DEFAULT 'system',
    refreshed_count INTEGER NOT NULL DEFAULT 0,
    error_message TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_knowledge_index_jobs_asset_id ON knowledge_asset_index_jobs(asset_id);

CREATE TABLE IF NOT EXISTS knowledge_asset_workflows (
    id VARCHAR(64) PRIMARY KEY,
    asset_id VARCHAR(64) NOT NULL UNIQUE,
    owner VARCHAR(128) NOT NULL DEFAULT 'system',
    visibility VARCHAR(32) NOT NULL DEFAULT 'internal',
    review_status VARCHAR(32) NOT NULL DEFAULT 'approved',
    reviewer VARCHAR(128) NOT NULL DEFAULT '',
    review_note TEXT NOT NULL DEFAULT '',
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_knowledge_workflows_asset_id ON knowledge_asset_workflows(asset_id);

-- ============================================================
-- 生成任务
-- ============================================================

CREATE TABLE IF NOT EXISTS generation_jobs (
    id VARCHAR(64) PRIMARY KEY,
    project_id VARCHAR(64),
    project_name VARCHAR(255) NOT NULL DEFAULT '',
    template_name VARCHAR(128) NOT NULL DEFAULT '标准回标模板',
    status VARCHAR(32) NOT NULL DEFAULT 'completed',
    section_count INTEGER NOT NULL DEFAULT 0,
    overall_progress VARCHAR(32) NOT NULL DEFAULT '已生成',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS generation_sections_records (
    id VARCHAR(64) PRIMARY KEY,
    job_id VARCHAR(64) NOT NULL,
    section_no INTEGER NOT NULL DEFAULT 0,
    title VARCHAR(255) NOT NULL DEFAULT '',
    content TEXT NOT NULL DEFAULT '',
    status VARCHAR(32) NOT NULL DEFAULT '已生成',
    citations INTEGER NOT NULL DEFAULT 0,
    todos INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_generation_sections_job_id ON generation_sections_records(job_id);

CREATE TABLE IF NOT EXISTS generation_section_asset_refs (
    id VARCHAR(64) PRIMARY KEY,
    job_id VARCHAR(64) NOT NULL,
    section_id VARCHAR(64) NOT NULL,
    asset_id VARCHAR(64) NOT NULL,
    asset_title VARCHAR(255) NOT NULL DEFAULT '',
    chunk_title VARCHAR(255) NOT NULL DEFAULT '',
    reason TEXT NOT NULL DEFAULT '',
    snippet TEXT NOT NULL DEFAULT '',
    score FLOAT NOT NULL DEFAULT 0.0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_generation_refs_job_id ON generation_section_asset_refs(job_id);
CREATE INDEX IF NOT EXISTS idx_generation_refs_section_id ON generation_section_asset_refs(section_id);
CREATE INDEX IF NOT EXISTS idx_generation_refs_asset_id ON generation_section_asset_refs(asset_id);

-- ============================================================
-- 决策任务
-- ============================================================

CREATE TABLE IF NOT EXISTS project_decision_jobs (
    id VARCHAR(64) PRIMARY KEY,
    project_id VARCHAR(64) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'pending',
    score TEXT,
    rule_hits TEXT,
    ai_reasons TEXT,
    pending_checks TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_decision_jobs_project_id ON project_decision_jobs(project_id);

-- ============================================================
-- 审查任务
-- ============================================================

CREATE TABLE IF NOT EXISTS review_jobs (
    id VARCHAR(64) PRIMARY KEY,
    project_id VARCHAR(64),
    contract_name VARCHAR(255) NOT NULL,
    contract_type VARCHAR(64) NOT NULL DEFAULT '采购合同',
    source_text TEXT NOT NULL DEFAULT '',
    trigger VARCHAR(32) NOT NULL DEFAULT 'manual',
    status VARCHAR(32) NOT NULL DEFAULT 'queued',
    overall_risk VARCHAR(16) NOT NULL DEFAULT 'P3',
    issue_count INTEGER NOT NULL DEFAULT 0,
    high_risk_issue_count INTEGER NOT NULL DEFAULT 0,
    summary TEXT NOT NULL DEFAULT '[]',
    review_actions TEXT NOT NULL DEFAULT '[]',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_review_jobs_project_id ON review_jobs(project_id);
CREATE INDEX IF NOT EXISTS idx_review_jobs_status ON review_jobs(status);

CREATE TABLE IF NOT EXISTS review_issues_records (
    id VARCHAR(64) PRIMARY KEY,
    job_id VARCHAR(64) NOT NULL REFERENCES review_jobs(id),
    title VARCHAR(255) NOT NULL,
    type VARCHAR(64) NOT NULL,
    level VARCHAR(16) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT '待处理',
    document VARCHAR(255) NOT NULL DEFAULT '合同条款扫描',
    detail TEXT NOT NULL,
    evidence TEXT NOT NULL DEFAULT '',
    suggestion TEXT NOT NULL DEFAULT '',
    rule_name VARCHAR(128) NOT NULL DEFAULT '',
    resolution_note TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_review_issues_job_id ON review_issues_records(job_id);
CREATE INDEX IF NOT EXISTS idx_review_issues_level ON review_issues_records(level);
CREATE INDEX IF NOT EXISTS idx_review_issues_status ON review_issues_records(status);

CREATE TABLE IF NOT EXISTS review_clauses_records (
    id VARCHAR(64) PRIMARY KEY,
    job_id VARCHAR(64) NOT NULL REFERENCES review_jobs(id),
    clause_no INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL DEFAULT '',
    content TEXT NOT NULL,
    source_ref VARCHAR(128) NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_review_clauses_job_id ON review_clauses_records(job_id);

CREATE TABLE IF NOT EXISTS review_feedback_records (
    id VARCHAR(64) PRIMARY KEY,
    issue_id VARCHAR(64) NOT NULL REFERENCES review_issues_records(id),
    job_id VARCHAR(64) NOT NULL REFERENCES review_jobs(id),
    rule_name VARCHAR(128) NOT NULL DEFAULT '',
    feedback_type VARCHAR(32) NOT NULL,
    feedback_note TEXT NOT NULL DEFAULT '',
    reviewer VARCHAR(64) NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_review_feedback_issue_id ON review_feedback_records(issue_id);
CREATE INDEX IF NOT EXISTS idx_review_feedback_job_id ON review_feedback_records(job_id);
CREATE INDEX IF NOT EXISTS idx_review_feedback_rule_name ON review_feedback_records(rule_name);

-- ============================================================
-- 规则配置
-- ============================================================

CREATE TABLE IF NOT EXISTS rule_configs (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(128) NOT NULL UNIQUE,
    title VARCHAR(255) NOT NULL,
    issue_type VARCHAR(64) NOT NULL,
    level VARCHAR(16) NOT NULL,
    detail TEXT NOT NULL,
    suggestion TEXT NOT NULL,
    patterns TEXT NOT NULL DEFAULT '',
    document VARCHAR(255) NOT NULL DEFAULT '合同条款',
    match_mode VARCHAR(16) NOT NULL DEFAULT 'any',
    is_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    priority INTEGER NOT NULL DEFAULT 100,
    category VARCHAR(64) NOT NULL DEFAULT '付款风险',
    description TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_rule_configs_name ON rule_configs(name);

CREATE TABLE IF NOT EXISTS rule_statistics (
    rule_name VARCHAR(128) PRIMARY KEY,
    hit_count INTEGER NOT NULL DEFAULT 0,
    confirmed_count INTEGER NOT NULL DEFAULT 0,
    dismissed_count INTEGER NOT NULL DEFAULT 0,
    modified_count INTEGER NOT NULL DEFAULT 0,
    accuracy_rate FLOAT NOT NULL DEFAULT 0.0,
    last_feedback_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 项目文档与版本
-- ============================================================

CREATE TABLE IF NOT EXISTS project_documents (
    id VARCHAR(64) PRIMARY KEY,
    project_id VARCHAR(64) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_type VARCHAR(32) NOT NULL DEFAULT 'txt',
    document_type VARCHAR(64) NOT NULL DEFAULT '招标文件',
    parse_status VARCHAR(32) NOT NULL DEFAULT '已解析',
    source_text TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_project_documents_project_id ON project_documents(project_id);

CREATE TABLE IF NOT EXISTS project_document_versions (
    id VARCHAR(64) PRIMARY KEY,
    document_id VARCHAR(64) NOT NULL,
    project_id VARCHAR(64) NOT NULL,
    version_no INTEGER NOT NULL DEFAULT 1,
    file_name VARCHAR(255) NOT NULL,
    file_type VARCHAR(32) NOT NULL DEFAULT 'txt',
    document_type VARCHAR(64) NOT NULL DEFAULT '招标文件',
    storage_backend VARCHAR(32) NOT NULL DEFAULT 'local',
    object_key VARCHAR(512) NOT NULL DEFAULT '',
    file_size INTEGER NOT NULL DEFAULT 0,
    parse_status VARCHAR(32) NOT NULL DEFAULT '已解析',
    source_text TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_project_doc_versions_document_id ON project_document_versions(document_id);
CREATE INDEX IF NOT EXISTS idx_project_doc_versions_project_id ON project_document_versions(project_id);

-- ============================================================
-- 项目解析章节与提取字段
-- ============================================================

CREATE TABLE IF NOT EXISTS project_parse_sections (
    id VARCHAR(64) PRIMARY KEY,
    project_id VARCHAR(64) NOT NULL,
    document_id VARCHAR(64) NOT NULL,
    title VARCHAR(255) NOT NULL,
    page VARCHAR(64) NOT NULL DEFAULT '',
    state VARCHAR(32) NOT NULL DEFAULT '已抽取',
    sort_order INTEGER NOT NULL DEFAULT 0,
    source_text VARCHAR(16384) NOT NULL DEFAULT '',
    source_file VARCHAR(255) NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_project_parse_sections_project_id ON project_parse_sections(project_id);
CREATE INDEX IF NOT EXISTS idx_project_parse_sections_document_id ON project_parse_sections(document_id);

CREATE TABLE IF NOT EXISTS project_extracted_fields (
    id VARCHAR(64) PRIMARY KEY,
    project_id VARCHAR(64) NOT NULL,
    document_id VARCHAR(64) NOT NULL,
    label VARCHAR(255) NOT NULL,
    value TEXT NOT NULL DEFAULT '',
    confidence VARCHAR(32) NOT NULL DEFAULT '80%',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_project_extracted_fields_project_id ON project_extracted_fields(project_id);
CREATE INDEX IF NOT EXISTS idx_project_extracted_fields_document_id ON project_extracted_fields(document_id);

-- ============================================================
-- 项目资产偏好
-- ============================================================

CREATE TABLE IF NOT EXISTS project_asset_preferences (
    id VARCHAR(64) PRIMARY KEY,
    project_id VARCHAR(64) NOT NULL,
    asset_title VARCHAR(255) NOT NULL,
    preference_mode VARCHAR(32) NOT NULL DEFAULT 'fixed',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_project_asset_prefs_project_id ON project_asset_preferences(project_id);
CREATE INDEX IF NOT EXISTS idx_project_asset_prefs_asset_title ON project_asset_preferences(asset_title);

-- ============================================================
-- 统计视图
-- ============================================================

-- 项目统计视图
CREATE OR REPLACE VIEW v_project_stats AS
SELECT
    p.id,
    p.name,
    p.status,
    p.parse_status,
    (SELECT COUNT(*) FROM parsing_sections ps WHERE ps.project_id = p.id) AS section_count,
    (SELECT COUNT(*) FROM business_documents bd WHERE bd.project_id = p.id) AS business_doc_count,
    (SELECT COUNT(*) FROM technical_documents td WHERE td.project_id = p.id) AS tech_doc_count,
    (SELECT COUNT(*) FROM proposal_plans pp WHERE pp.project_id = p.id) AS proposal_count,
    (SELECT COUNT(*) FROM technical_cases tc WHERE tc.project_id = p.id) AS case_count,
    p.created_at,
    p.updated_at
FROM projects p;
