from uuid import uuid4
import json

from sqlalchemy.orm import Session

from app.models.business_document import BusinessDocument
from app.models.project import Project
from app.schemas.business_document import (
    BusinessDocumentSummary,
    BusinessDocumentDetail,
    BusinessDocumentUpdateRequest,
)


# 13种商务文档模板数据（对应 TASK_MANIFEST.md 行54-79）
BUSINESS_DOCUMENT_TEMPLATES = [
    {
        "doc_type": "deviation",
        "doc_name": "商务偏离表",
        "has_fillable_fields": True,
        "is_star_item": True,
        "score_point": "商务评分 - 15分",
        "rule_description": "投标文件商务条款与招标文件要求的偏差情况，无偏离得满分15分，每偏离一项扣分",
        "return_file_list": json.dumps([
            {"file_name": "商务偏离表.xlsx", "file_type": "excel", "description": "逐项列明商务条款偏离情况"}
        ], ensure_ascii=False),
        "original_content": """商务偏离表

一、偏离说明
本表用于说明投标文件商务条款与招标文件要求的偏离情况。

序号 | 招标文件条款号 | 招标文件要求 | 投标文件响应 | 偏离说明
--- | --- | --- | --- | ---
1 | | | | |
2 | | | | |
3 | | | | |

二、无偏离承诺
□ 本投标文件对招标文件的商务条款全部响应，无任何偏离。
□ 存在上述偏离项，请参见上表说明。

投标人（盖章）：__________
日期：__________
""",
    },
    {
        "doc_type": "commitment",
        "doc_name": "应答承诺函",
        "has_fillable_fields": True,
        "is_star_item": True,
        "score_point": "商务评分 - 5分",
        "rule_description": "投标人对招标文件各项要求的正式应答承诺",
        "return_file_list": json.dumps([
            {"file_name": "应答承诺函.docx", "file_type": "word", "description": "正式应答承诺函"}
        ], ensure_ascii=False),
        "original_content": """应答承诺函

致：【招标人名称】

我方（投标人名称）已详细阅读并充分理解招标文件（项目名称：____）的全部内容，现正式提交投标文件，并就以下事项作出承诺：

一、服务承诺
我方承诺按照招标文件要求，按时、保质完成本项目。

二、价格承诺
我方投标总价为：人民币（大写）________元（RMB ￥________元）。

三、履约承诺
我方承诺在合同签订后，按招标文件要求及投标文件响应内容履约。

四、资质承诺
我方承诺本投标文件提交的所有资料真实、合法、有效。

五、保密承诺
我方承诺对招标文件中涉及的商业秘密予以保密。

投标人（盖章）：__________
法定代表人或授权代表（签字）：__________
日期：__________
""",
    },
    {
        "doc_type": "authorization",
        "doc_name": "法定代表人（或非法人单位负责人）身份证明或授权委托书",
        "has_fillable_fields": True,
        "is_star_item": True,
        "score_point": "商务评分 - 必备文件",
        "rule_description": "证明授权代表身份合法有效的文件",
        "return_file_list": json.dumps([
            {"file_name": "身份证明.pdf", "file_type": "pdf", "description": "法定代表人身份证明"},
            {"file_name": "授权委托书.docx", "file_type": "word", "description": "授权委托书"}
        ], ensure_ascii=False),
        "original_content": """法定代表人（或非法人单位负责人）身份证明

兹证明__________（姓名）在我公司（__________）担任__________职务，为我单位法定代表人（或非法人单位负责人），其签字具有法律效力。

特此证明。

附：法定代表人（或非法人单位负责人）身份证复印件（加盖公章）

投标人（盖章）：__________
日期：__________

---
授权委托书

致：【招标人名称】

我__________（姓名）作为__________（投标人名称）的法定代表人（或非法人单位负责人），现授权__________（姓名，身份证号：__________）为我方代理人，代表我方全权办理本项目（项目名称：__________）的投标、谈判、签约等一切相关事宜，其法律后果由我方承担。

委托期限：自签字之日起至本项目结束。

法定代表人（或非法人单位负责人）（签字）：__________
投标人（盖章）：__________
日期：__________

附：被授权人身份证复印件（加盖公章）
""",
    },
    {
        "doc_type": "business_license",
        "doc_name": "营业执照（事业单位法人证书）",
        "has_fillable_fields": True,
        "is_star_item": False,
        "score_point": "商务评分 - 必备文件",
        "rule_description": "证明投标人依法成立、具有经营资格的有效证照",
        "return_file_list": json.dumps([
            {"file_name": "营业执照.pdf", "file_type": "pdf", "description": "加盖公章的营业执照副本复印件"}
        ], ensure_ascii=False),
        "original_content": """营业执照

投标人名称：__________
统一社会信用代码：__________
法定代表人：__________
注册资本：__________
成立日期：__________
营业期限：__________
经营范围：__________
登记机关：__________

【说明】请上传加盖公章的营业执照副本复印件（事业单位请上传事业单位法人证书）。

状态核查：□存续  □在业  □其他（请注明）__________
""",
    },
    {
        "doc_type": "qualification",
        "doc_name": "资格审查资料（严重违法失信信息截图）",
        "has_fillable_fields": False,
        "is_star_item": False,
        "score_point": "商务评分 - 重大扣分项",
        "rule_description": "核查投标人是否被列入严重违法失信企业名单，列入者投标无效",
        "return_file_list": json.dumps([
            {"file_name": "信用截图.pdf", "file_type": "pdf", "description": "国家企业信用信息公示系统严重违法失信信息截图"}
        ], ensure_ascii=False),
        "original_content": """资格审查资料 - 严重违法失信信息

一、严重违法失信信息核查

根据招标文件要求，投标人须在投标文件中提供国家企业信用信息公示系统（https://www.gsxt.gov.cn）严重违法失信信息截图。

□ 经核查，本公司未被列入严重违法失信企业名单。
□ 经核查，本公司已被列入严重违法失信企业名单（请说明）：__________

二、核查方式
1. 访问国家企业信用信息公示系统
2. 输入企业名称或统一社会信用代码
3. 截图"严重违法失信企业名单"查询结果页面
4. 加盖公章后作为投标文件组成部分

【人工补充说明】
如查询结果为空，请截图"未找到相关记录"页面并加盖公章。
""",
    },
    {
        "doc_type": "special_invoice",
        "doc_name": "资格证明文件-专票开具承诺",
        "has_fillable_fields": True,
        "is_star_item": False,
        "score_point": "商务评分 - 2分",
        "rule_description": "投标人是否可开具增值税专用发票的承诺",
        "return_file_list": json.dumps([
            {"file_name": "专票开具承诺.docx", "file_type": "word", "description": "增值税专用发票开具承诺函"}
        ], ensure_ascii=False),
        "original_content": """专票开具承诺函

致：【招标人名称】

关于本项目（项目名称：__________）的增值税发票开具事宜，我方承诺如下：

□ 我方可以开具增值税专用发票
□ 我方仅能开具增值税普通发票

如可开具专票，税点为：__________%

开票信息：
单位名称：__________
纳税人识别号：__________
开户银行：__________
银行账号：__________
注册地址：__________
电话：__________

投标人（盖章）：__________
日期：__________
""",
    },
    {
        "doc_type": "non_control",
        "doc_name": "资格证明文件-无控股管理关系承诺",
        "has_fillable_fields": True,
        "is_star_item": False,
        "score_point": "商务评分 - 2分",
        "rule_description": "投标人与其他投标人不存在控股、管理关系的承诺",
        "return_file_list": json.dumps([
            {"file_name": "无控股管理关系承诺.docx", "file_type": "word", "description": "无控股管理关系承诺函"}
        ], ensure_ascii=False),
        "original_content": """无控股管理关系承诺函

致：【招标人名称】

我方（投标人名称）就本项目（项目名称：__________）参与投标事宜，郑重承诺如下：

一、本公司与参与本项目投标的其他投标人之间不存在以下情形：
1. 相互持股情形；
2. 被同一第三方控股情形；
3. 本公司的控股股东、实际控制人同时为其他投标人控股股东、实际控制人的情形；
4. 本公司与招标文件规定的其他关联关系情形。

二、本公司已知悉，如违反上述承诺，招标人有权取消我方投标资格，由此造成的一切后果由我方承担。

三、本承诺函自投标文件提交之日起至合同履行完毕之日持续有效。

投标人（盖章）：__________
日期：__________
""",
    },
    {
        "doc_type": "non_consortium",
        "doc_name": "资格证明文件-非联合体要求",
        "has_fillable_fields": False,
        "is_star_item": False,
        "score_point": "商务评分 - 2分",
        "rule_description": "投标人承诺本项目不接受联合体投标",
        "return_file_list": json.dumps([
            {"file_name": "非联合体声明.docx", "file_type": "word", "description": "非联合体投标声明"}
        ], ensure_ascii=False),
        "original_content": """非联合体投标声明

致：【招标人名称】

我方（投标人名称）就本项目（项目名称：__________）郑重声明：

本项目由我方独立投标，不存在以下情形：
1. 与其他投标人组成联合体参加投标；
2. 以其他投标人名义投标；
3. 向其他投标人转让中标项目；
4. 将中标项目违法分包或转包给其他投标人。

如违反上述声明，我方愿承担一切法律责任并接受招标人作出的处理决定。

投标人（盖章）：__________
日期：__________
""",
    },
    {
        "doc_type": "holding_relation",
        "doc_name": "资格证明文件-应答人控股及管理关系情况申报表",
        "has_fillable_fields": True,
        "is_star_item": False,
        "score_point": "商务评分 - 3分",
        "rule_description": "填报投标人控股及管理关系情况",
        "return_file_list": json.dumps([
            {"file_name": "控股管理关系申报表.xlsx", "file_type": "excel", "description": "控股及管理关系情况申报表"}
        ], ensure_ascii=False),
        "original_content": """应答人控股及管理关系情况申报表

一、控股股东/实际控制人情况

控股股东名称：__________
持股比例：__________%
实际控制人姓名：__________
身份证号：__________

二、向上穿透（持股5%以上的股东）

序号 | 股东名称 | 持股比例 | 备注
--- | --- | --- | ---
1 | | | 
2 | | | 
3 | | | 

三、向下管理（直接控股的子公司）

序号 | 子公司名称 | 持股比例 | 备注
--- | --- | --- | ---
1 | | | 
2 | | | 

四、与招标人/采购人关联关系说明

□ 无关联关系
□ 存在以下关联关系（请说明）：__________

填报人（签字）：__________
填报日期：__________
""",
    },
    {
        "doc_type": "operation_commitment",
        "doc_name": "资格证明文件-应答人经营状况承诺书",
        "has_fillable_fields": True,
        "is_star_item": False,
        "score_point": "商务评分 - 3分",
        "rule_description": "投标人承诺经营状况正常、无重大违法违规",
        "return_file_list": json.dumps([
            {"file_name": "经营状况承诺书.docx", "file_type": "word", "description": "经营状况承诺书"}
        ], ensure_ascii=False),
        "original_content": """应答人经营状况承诺书

致：【招标人名称】

我方（投标人名称）就本项目（项目名称：__________）的投标事宜，郑重承诺如下：

一、经营状况声明
1. 本单位依法注册，合法经营，当前处于正常经营状态；
2. 最近三年内无重大违法违规记录；
3. 财务状况良好，无资不抵债情况；
4. 未被列入经营异常名录、严重违法失信企业名单。

二、近三年经营情况
年 | 营业收入（万元） | 净利润（万元） | 备注
--- | --- | --- | ---
____年 | | | 
____年 | | | 
____年 | | | 

三、依法纳税及社保情况
□ 依法按时足额纳税
□ 依法为员工缴纳社会保险

如违反上述承诺，我方愿承担一切法律责任。

投标人（盖章）：__________
日期：__________
""",
    },
    {
        "doc_type": "integrity_notice",
        "doc_name": "资格证明文件-供应商廉洁从业信息告知书",
        "has_fillable_fields": False,
        "is_star_item": False,
        "score_point": "商务评分 - 2分",
        "rule_description": "告知投标人廉洁从业相关要求",
        "return_file_list": json.dumps([
            {"file_name": "廉洁从业告知书确认回执.docx", "file_type": "word", "description": "廉洁从业信息告知书确认回执"}
        ], ensure_ascii=False),
        "original_content": """供应商廉洁从业信息告知书

各投标人：

为维护公平、公正的招标采购秩序，防止商业贿赂和不正当竞争行为，现将廉洁从业相关要求告知如下：

一、禁止行为
1. 禁止向招标人工作人员、评审专家行贿或提供不当利益；
2. 禁止以其他投标人名义投标或串通投标；
3. 禁止以非法手段干预招标评审活动；
4. 禁止伪造资质证书、业绩等材料。

二、责任追究
如投标人违反上述禁止行为，一经查实，招标人有权：
1. 取消投标资格；
2. 纳入供应商黑名单；
3. 依法追究法律责任。

三、廉洁投标承诺
□ 我方已阅知上述内容，承诺廉洁参与本项目投标，不从事任何违法违规行为。

投标人（盖章）：__________
日期：__________
""",
    },
    {
        "doc_type": "bid_bond",
        "doc_name": "投标保证金凭证",
        "has_fillable_fields": False,
        "is_star_item": False,
        "score_point": "商务评分 - 必备",
        "rule_description": "证明投标人已缴纳投标保证金的凭证",
        "return_file_list": json.dumps([
            {"file_name": "保证金凭证.pdf", "file_type": "pdf", "description": "银行转账凭证或保函扫描件"}
        ], ensure_ascii=False),
        "original_content": """投标保证金凭证

投标人名称：__________
项目名称：__________
招标编号：__________

一、保证金缴纳信息
缴纳金额：人民币（大写）________元（RMB ￥________元）
缴纳方式：□银行转账  □保函  □其他
缴纳时间：__________
收款账户信息（招标人指定）：
开户名称：__________
开户银行：__________
账号：__________

二、凭证附件
□ 银行转账凭证（加盖银行章）
□ 银行保函正本
□ 其他凭证

投标人（盖章）：__________
日期：__________

【备注】未中标人的保证金将在中标结果公示后7个工作日内无息退还。
""",
    },
    {
        "doc_type": "additional_commitment",
        "doc_name": "其他商务文件-附加承诺函",
        "has_fillable_fields": True,
        "is_star_item": False,
        "score_point": "商务评分 - 视项目要求",
        "rule_description": "根据具体项目要求提供额外商务承诺",
        "return_file_list": json.dumps([
            {"file_name": "附加承诺函.docx", "file_type": "word", "description": "项目特定商务承诺函"}
        ], ensure_ascii=False),
        "original_content": """附加承诺函

致：【招标人名称】

我方（投标人名称）就本项目（项目名称：__________，招标编号：__________）补充承诺如下：

【请根据招标文件要求填写具体承诺内容】

一、服务承诺（如有特殊服务要求）
_________________________________________________

二、质保承诺（如有特殊质保要求）
_________________________________________________

三、其他承诺
_________________________________________________

以上承诺作为投标文件组成部分，与投标文件其他内容具有同等法律效力。

投标人（盖章）：__________
法定代表人或授权代表（签字）：__________
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


def ensure_business_documents(db: Session, project_id: str) -> list[BusinessDocument]:
    """确保项目有商务文档模板数据，如无则创建"""
    get_or_create_project(db, project_id)

    existing = db.query(BusinessDocument).filter(BusinessDocument.project_id == project_id).all()
    if existing:
        return existing

    created = []
    for tpl in BUSINESS_DOCUMENT_TEMPLATES:
        doc = BusinessDocument(
            id=f"bd_{uuid4().hex[:12]}",
            project_id=project_id,
            doc_type=tpl["doc_type"],
            doc_name=tpl["doc_name"],
            has_fillable_fields=tpl["has_fillable_fields"],
            is_star_item=tpl["is_star_item"],
            score_point=tpl["score_point"],
            rule_description=tpl["rule_description"],
            return_file_list=tpl["return_file_list"],
            original_content=tpl["original_content"],
            editable_content=tpl["original_content"],  # 默认相同
            status="pending",
            source_file="",
        )
        db.add(doc)
        created.append(doc)

    db.commit()
    return created


def list_business_documents(db: Session, project_id: str) -> list[BusinessDocumentSummary]:
    docs = ensure_business_documents(db, project_id)
    return [BusinessDocumentSummary.model_validate(d) for d in docs]


def get_business_document_detail(db: Session, project_id: str, doc_id: str) -> BusinessDocumentDetail:
    docs = ensure_business_documents(db, project_id)
    for d in docs:
        if d.id == doc_id:
            return BusinessDocumentDetail.model_validate(d)
    from fastapi import HTTPException, status
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在")


def update_business_document(
    db: Session, project_id: str, doc_id: str, payload: BusinessDocumentUpdateRequest
) -> BusinessDocumentDetail:
    doc = db.query(BusinessDocument).filter(
        BusinessDocument.id == doc_id,
        BusinessDocument.project_id == project_id,
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
    return BusinessDocumentDetail.model_validate(doc)


def generate_business_document(
    db: Session, project_id: str, doc_id: str
) -> BusinessDocumentDetail:
    doc = db.query(BusinessDocument).filter(
        BusinessDocument.id == doc_id,
        BusinessDocument.project_id == project_id,
    ).first()
    if not doc:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在")

    project = get_or_create_project(db, project_id)
    
    # Gather real project & tender info for generation
    from app.models.tender import Tender
    tender = db.query(Tender).filter(Tender.project_id == project_id).first()
    
    # Extract tender requirements from parsing sections
    from app.models.parsing_section import ParsingSection
    parsing_sections = db.query(ParsingSection).filter(ParsingSection.project_id == project_id).all()
    tender_requirements = "\n\n".join([
        f"[{s.section_name}]\n{s.content[:500]}" 
        for s in parsing_sections if s.content
    ]) if parsing_sections else ""
    
    # Build project summary
    project_summary = f"项目名称: {project.name}\n"
    if project.client:
        project_summary += f"招标人: {project.client}\n"
    if project.amount:
        project_summary += f"投标金额: {project.amount}\n"
    if project.deadline:
        project_summary += f"截止日期: {project.deadline}\n"
    if project.bidding_company:
        project_summary += f"投标公司: {project.bidding_company}\n"
    if project.agent_name:
        project_summary += f"联系人: {project.agent_name}\n"
    
    delivery_deadline = project.deadline or ""
    service_commitment = tender.service_commitment if tender else ""
    
    from app.services.workspace_service import get_extracted_fields
    extracted_fields = {item.label: item.value for item in get_extracted_fields(db)}
    
    # Also include project's extracted_fields if available
    if project.extracted_fields:
        for f in project.extracted_fields:
            if isinstance(f, dict) and "label" in f and "value" in f:
                extracted_fields[f["label"]] = str(f["value"])

    from app.services.asset_routing_service import asset_routing_service
    routed_assets = asset_routing_service.route_assets_for_section(
        db,
        section_title=doc.doc_name,
        project_summary=project_summary,
        tender_requirements=tender_requirements,
        delivery_deadline=delivery_deadline,
        service_commitment=service_commitment,
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

    from app.services.llm_client import llm_generation_client
    generated_content = llm_generation_client.generate_document_content(
        project_name=project.name,
        doc_name=doc.doc_name,
        original_content=doc.original_content,
        score_point=doc.score_point,
        rule_description=doc.rule_description,
        extracted_fields=extracted_fields,
        routed_assets=routed_asset_payloads,
        technical_cases=[],
    )

    if generated_content:
        doc.editable_content = generated_content
        doc.status = "filled"
        db.commit()
        db.refresh(doc)

    return BusinessDocumentDetail.model_validate(doc)
