from uuid import uuid4
import json

from sqlalchemy.orm import Session

from app.models.proposal_plan import ProposalPlan
from app.models.project import Project
from app.schemas.proposal_plan import (
    ProposalPlanSummary,
    ProposalPlanDetail,
    ProposalPlanUpdateRequest,
)


# 4种方案建议书文档模板数据（对应 TASK_MANIFEST.md 行76-79）
PROPOSAL_PLAN_TEMPLATES = [
    {
        "doc_type": "maintenance_period",
        "doc_name": "维保期限",
        "has_fillable_fields": True,
        "is_star_item": True,
        "score_point": "方案评分",
        "rule_description": "根据技术规范书和打分表要求，计算最高得分下的维保期限，填写文档。维保期限越长得分越高，但需结合公司实际服务能力综合考虑。支持人工修改后二次计算得分。",
        "return_file_list": json.dumps([
            {"file_name": "维保方案.docx", "file_type": "word", "description": "维保服务方案"}
        ], ensure_ascii=False),
        "original_content": """维保期限方案

项目名称：__________
招标编号：__________

一、维保期限选择

根据招标文件技术规范书要求和公司服务能力，现就本项目维保期限说明如下：

【打分规则说明】
维保期限评分规则：
- 维保期1年：得基本分
- 维保期2年：得标准分
- 维保期3年：得较高分
- 维保期4年及以上：得最高分

（如招标文件另有规定，以招标文件为准）

二、维保期限承诺

□ 维保期1年（自项目终验合格之日起）
□ 维保期2年（自项目终验合格之日起）
□ 维保期3年（自项目终验合格之日起）
□ 维保期__________年（自项目终验合格之日起）

三、维保服务内容

1. 服务范围
   本次投标产品/系统的维保服务，包括：
   □ 远程技术支持  □ 现场技术支持  □ 软件版本升级  □ 故障响应处理

2. 响应时间承诺
   - 紧急故障：_______小时内响应，_______小时内到达现场
   - 一般故障：_______小时内响应，_______小时内解决
   - 远程支持：_______分钟内响应

3. 维保期服务费用
   □ 维保期内服务费用已包含在投标总价中
   □ 维保期服务费用另计，收费标准为：__________

四、维保期届满后续服务
维保期届满后，我方可继续提供有偿维保服务，收费标准按市场优惠价执行。

投标人（盖章）：__________
日期：__________
""",
    },
    {
        "doc_type": "project_manager",
        "doc_name": "项目经理能力",
        "has_fillable_fields": True,
        "is_star_item": True,
        "score_point": "方案评分",
        "rule_description": "根据打分表要求，检索素材库中符合项目经理资质要求的人员信息，计算最高得分下的人员配置，填写文档。支持人工修改。",
        "return_file_list": json.dumps([
            {"file_name": "项目经理资质证明.pdf", "file_type": "pdf", "description": "项目经理简历、资质证书、业绩证明"}
        ], ensure_ascii=False),
        "original_content": """项目经理能力说明

项目名称：__________
招标编号：__________

一、项目经理基本信息

姓名：__________
性别：__________
年龄：__________
学历：__________
职称：__________
专业：__________
从业年限：__________年

二、资质认证

□ PMP认证（证书编号：__________）
□ IPMP认证（证书编号：__________）
□ 一级建造师（证书编号：__________）
□ 系统集成项目管理工程师（证书编号：__________）
□ 其他认证：__________

三、项目经验

1. 主导同类项目经验
   已完成同类项目数量：__________个
   最近3年同类项目数量：__________个

   代表性项目：
   （1）项目名称：__________
       客户单位：__________
       合同金额：__________万元
       担任角色：项目经理
       项目周期：__________

   （2）项目名称：__________
       客户单位：__________
       合同金额：__________万元
       担任角色：项目经理
       项目周期：__________

四、技术能力说明

1. 核心技术能力
   （请描述项目经理在投标项目相关领域的技术能力）

   _________________________________________________

2. 管理能力
   （请描述项目经理的项目管理经验和方法论）

   _________________________________________________

五、证明材料

已附项目经理简历、资质证书、业绩证明材料，请参见回标文件清单。

投标人（盖章）：__________
日期：__________
""",
    },
    {
        "doc_type": "staff_capability",
        "doc_name": "人员能力",
        "has_fillable_fields": True,
        "is_star_item": True,
        "score_point": "方案评分",
        "rule_description": "根据打分表要求，检索素材库中符合资质要求的人员信息，计算最高得分下的人员配置方案，填写文档。支持人工修改。",
        "return_file_list": json.dumps([
            {"file_name": "项目团队资质证明.pdf", "file_type": "pdf", "description": "团队成员简历、资质证书、社保记录"}
        ], ensure_ascii=False),
        "original_content": """项目团队人员能力说明

项目名称：__________
招标编号：__________

一、项目团队配置

根据招标文件要求和公司资源情况，本项目拟配置核心团队人员如下：

序号 | 姓名 | 岗位 | 学历 | 职称/资质 | 从业年限 | 主要职责
--- | --- | --- | --- | --- | --- | ---
1 | | 项目经理 | | | | 全面负责
2 | | 技术负责人 | | | | 技术把控
3 | | 开发工程师 | | | | 系统开发
4 | | 测试工程师 | | | | 质量保障
5 | | 项目助理 | | | | 协调管理
6 | | | | | | 
7 | | | | | | 

合计：__________人

二、团队人员资质汇总

1. 高级工程师（高级职称）：__________人
2. 中级工程师（中级职称）：__________人
3. 初级工程师：__________人
4. 注册建筑师/建造师：__________人
5. PMP/IPMP认证：__________人

三、核心人员简历

3.1 项目经理（详见"项目经理能力"章节）

3.2 技术负责人
姓名：__________
学历：__________
专业：__________
职称：__________
主要业绩：__________

3.3 其他核心成员
（请附主要成员简历）

四、稳定性保障

1. 团队成员与公司签订正式劳动合同
2. 关键岗位人员已在我公司任职__________年
3. 项目实施期间，不随意更换项目核心成员

投标人（盖章）：__________
日期：__________
""",
    },
    {
        "doc_type": "hardware_resource",
        "doc_name": "硬件资源占用情况",
        "has_fillable_fields": True,
        "is_star_item": True,
        "score_point": "方案评分",
        "rule_description": "根据技术规范书要求，计算最高得分下的硬件资源配置方案，填写文档。支持人工修改后二次计算得分。",
        "return_file_list": json.dumps([
            {"file_name": "硬件配置方案.docx", "file_type": "word", "description": "硬件资源配置方案说明"}
        ], ensure_ascii=False),
        "original_content": """硬件资源占用情况说明

项目名称：__________
招标编号：__________

一、硬件资源配置方案

根据招标文件技术规范书要求和本次投标产品/系统的实际需求，我方硬件资源配置方案如下：

【打分规则说明】
（如招标文件对硬件资源有明确要求，以招标文件为准）

二、服务器配置

1. 应用服务器
   □ 云服务器（配置：CPU__________核，内存__________GB，存储__________GB）
   □ 物理服务器（配置：CPU__________核，内存__________GB，存储__________GB）
   数量：__________台
   用途：应用部署

2. 数据库服务器
   □ 云数据库服务（RDS）
   □ 自建数据库服务器
   配置：CPU__________核，内存__________GB，存储__________GB
   数量：__________台
   数据库类型：__________

3. 缓存/存储服务器
   配置：CPU__________核，内存__________GB，存储__________GB
   数量：__________台
   用途：__________

三、网络带宽

1. 带宽需求
   峰值带宽：__________Mbps
   常规带宽：__________Mbps

2. 专线/公网
   □ 互联网出口
   □ 专线接入
   □ 混合架构

四、资源占用估算

1. 存储空间估算
   - 项目数据量：__________GB/年
   - 日志数据量：__________GB/年
   - 备份数据量：__________GB/年
   - 总计：__________GB

2. 计算资源估算
   - 日均并发用户数：__________
   - 峰值并发用户数：__________
   - CPU利用率（预期）：__________%

五、可靠性保障

1. □ 数据备份：每日全量备份，每周增量备份
2. □ 容灾方案：同城容灾 / 异地容灾
3. □ 监控告警：7×24小时监控

六、其他说明

（如有特殊硬件需求或节能减排措施，请在此说明）

投标人（盖章）：__________
日期：__________
""",
    },
]


def get_or_create_project(db: Session, project_id: str) -> Project:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")
    return project


def ensure_proposal_plans(db: Session, project_id: str) -> list[ProposalPlan]:
    """确保项目有方案建议书模板数据，如无则创建"""
    get_or_create_project(db, project_id)

    existing = db.query(ProposalPlan).filter(ProposalPlan.project_id == project_id).all()
    if existing:
        return existing

    created = []
    for tpl in PROPOSAL_PLAN_TEMPLATES:
        doc = ProposalPlan(
            id=f"pp_{uuid4().hex[:12]}",
            project_id=project_id,
            doc_type=tpl["doc_type"],
            doc_name=tpl["doc_name"],
            has_fillable_fields=tpl["has_fillable_fields"],
            is_star_item=tpl["is_star_item"],
            score_point=tpl["score_point"],
            rule_description=tpl["rule_description"],
            return_file_list=tpl["return_file_list"],
            original_content=tpl["original_content"],
            editable_content=tpl["original_content"],
            status="pending",
            source_file="",
        )
        db.add(doc)
        created.append(doc)

    db.commit()
    return created


def list_proposal_plans(db: Session, project_id: str) -> list[ProposalPlanSummary]:
    docs = ensure_proposal_plans(db, project_id)
    return [ProposalPlanSummary.model_validate(d) for d in docs]


def get_proposal_plan_detail(db: Session, project_id: str, doc_id: str) -> ProposalPlanDetail:
    docs = ensure_proposal_plans(db, project_id)
    for d in docs:
        if d.id == doc_id:
            return ProposalPlanDetail.model_validate(d)
    from fastapi import HTTPException, status
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在")


def update_proposal_plan(
    db: Session, project_id: str, doc_id: str, payload: ProposalPlanUpdateRequest
) -> ProposalPlanDetail:
    doc = db.query(ProposalPlan).filter(
        ProposalPlan.id == doc_id,
        ProposalPlan.project_id == project_id,
    ).first()
    if not doc:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在")

    if payload.editable_content is not None:
        doc.editable_content = payload.editable_content
    if payload.status is not None:
        doc.status = payload.status

    db.commit()
    db.refresh(doc)
    return ProposalPlanDetail.model_validate(doc)


def generate_proposal_plan(
    db: Session, project_id: str, doc_id: str
) -> ProposalPlanDetail:
    doc = db.query(ProposalPlan).filter(
        ProposalPlan.id == doc_id,
        ProposalPlan.project_id == project_id,
    ).first()
    if not doc:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在")

    project = get_or_create_project(db, project_id)

    from app.services.workspace_service import get_extracted_fields
    extracted_fields = {item.label: item.value for item in get_extracted_fields(db)}

    from app.services.asset_routing_service import asset_routing_service
    routed_assets = asset_routing_service.route_assets_for_section(
        db,
        section_title=doc.doc_name,
        project_summary="",
        tender_requirements="",
        delivery_deadline="",
        service_commitment="",
        selected_asset_titles=[],
        fixed_asset_titles=[],
        excluded_asset_titles=[],
        extracted_fields=extracted_fields,
        limit=3,
    )
    routed_asset_payloads = [
        f"{item.asset_title}｜{item.chunk_title}｜{item.snippet}"
        for item in routed_assets
    ]

    from app.services.technical_case_service import search_technical_cases
    cases = search_technical_cases(db, project_id, keyword=doc.doc_name)
    case_payloads = [
        f"案例名称：{case.title}｜合同：{case.contract_name}｜摘要：{case.summary}"
        for case in cases[:3]
    ]

    from app.services.llm_client import llm_generation_client
    generated_content = llm_generation_client.generate_document_content(
        project_name=project.name,
        doc_name=doc.doc_name,
        original_content=doc.original_content,
        score_point=doc.score_point,
        rule_description=doc.rule_description,
        extracted_fields=extracted_fields,
        routed_assets=routed_asset_payloads,
        technical_cases=case_payloads,
    )

    if generated_content:
        doc.editable_content = generated_content
        doc.status = "filled"
        db.commit()
        db.refresh(doc)

    return ProposalPlanDetail.model_validate(doc)
