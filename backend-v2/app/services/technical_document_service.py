from uuid import uuid4
import json

from sqlalchemy.orm import Session

from app.models.technical_document import TechnicalDocument
from app.models.project import Project
from app.schemas.technical_document import (
    TechnicalDocumentSummary,
    TechnicalDocumentDetail,
    TechnicalDocumentUpdateRequest,
)


# 9种技术文档模板数据（对应 TASK_MANIFEST.md 行67-75）
TECHNICAL_DOCUMENT_TEMPLATES = [
    {
        "doc_type": "tech_overview",
        "doc_name": "技术部分",
        "has_fillable_fields": True,
        "is_star_item": True,
        "score_point": "技术评分",
        "rule_description": "技术部分标书文件清单，展示标书对应的回标文件清单，每个文件结构与对应的规则、打分点",
        "return_file_list": json.dumps([
            {"file_name": "技术投标文件.pdf", "file_type": "pdf", "description": "完整技术投标文件"},
            {"file_name": "技术偏离表.xlsx", "file_type": "excel", "description": "技术条款偏离情况说明"},
        ], ensure_ascii=False),
        "original_content": """技术部分 - 标书文件清单

一、技术部分文件清单

序号 | 文件名称 | 文件类型 | 说明
--- | --- | --- | ---
1 | 技术投标文件 | PDF | 完整技术方案
2 | 技术偏离表 | Excel | 技术条款偏离情况
3 | CMMI认证证书 | PDF | 公司资质证明
4 | 软件著作权证书 | PDF | 知识产权证明
5 | 项目实力证明 | PDF | 合同/案例材料
6 | 合规自查确认单 | Excel | 自查结果
7 | 服务承诺书 | Word | 服务保障承诺
8 | 其他阐述材料 | Word | 补充说明
9 | 封面 | PDF | 投标文件封面

二、技术打分点说明

1. 技术方案完整性（20分）
   - 技术方案覆盖招标文件所有要求
   - 方案具有针对性和可实施性

2. 公司资质（15分）
   - CMMI认证等级
   - 软件著作权数量
   - 同类项目业绩

3. 项目实力（20分）
   - 同类项目数量
   - 合同金额规模
   - 客户满意度

4. 服务承诺（15分）
   - 维保期限
   - 响应时间
   - 服务保障措施

三、回标文件要求

请按上表清单准备技术部分回标文件，确保每个文件内容完整、签章齐全。
""",
    },
    {
        "doc_type": "tech_deviation",
        "doc_name": "技术条款偏离表",
        "has_fillable_fields": True,
        "is_star_item": True,
        "score_point": "技术评分 - 10分",
        "rule_description": "技术条款与招标文件要求的偏差情况，无偏离得满分，每偏离一项扣分",
        "return_file_list": json.dumps([
            {"file_name": "技术条款偏离表.xlsx", "file_type": "excel", "description": "逐项列明技术条款偏离情况"}
        ], ensure_ascii=False),
        "original_content": """技术条款偏离表

一、偏离说明
本表用于说明投标文件技术条款与招标文件要求的偏离情况。

序号 | 招标文件条款号 | 招标文件技术要求 | 投标文件技术响应 | 偏离说明
--- | --- | --- | --- | ---
1 | | | | 
2 | | | | 
3 | | | | 

二、无偏离承诺
□ 本投标文件对招标文件的全部技术条款完全响应，无任何偏离。
□ 存在上述偏离项，请参见上表说明。

三、偏离项处理说明
（请对偏离项进行详细说明，并提供技术替代方案或补偿措施）

投标人（盖章）：__________
日期：__________
""",
    },
    {
        "doc_type": "cmmi_cert",
        "doc_name": "CMMI认证证书",
        "has_fillable_fields": False,
        "is_star_item": True,
        "score_point": "技术评分 - 5分",
        "rule_description": "CMMI认证证书用于证明公司软件能力成熟度，是技术评审的重要资质材料",
        "return_file_list": json.dumps([
            {"file_name": "CMMI认证证书.pdf", "file_type": "pdf", "description": "CMMI认证证书扫描件（加盖公章）"}
        ], ensure_ascii=False),
        "original_content": """CMMI认证证书

一、证书信息
证书名称：__________
证书等级：__________（如CMMI 5级）
证书编号：__________
获证日期：__________
有效期至：__________
认证范围：__________

二、认证机构
认证机构名称：__________
认可编号：__________

三、证书说明
本证书由美国CMMI研究所授权的评估机构颁发，证明持证单位在软件能力成熟度方面达到国际先进水平。

【说明】请上传加盖公章的CMMI认证证书扫描件。
""",
    },
    {
        "doc_type": "software_copyright",
        "doc_name": "计算机软件著作权证书",
        "has_fillable_fields": True,
        "is_star_item": True,
        "score_point": "技术评分 - 5分",
        "rule_description": "计算机软件著作权证书用于证明公司自主研发能力，是技术评审的重要指标",
        "return_file_list": json.dumps([
            {"file_name": "软件著作权证书.pdf", "file_type": "pdf", "description": "软件著作权登记证书扫描件"}
        ], ensure_ascii=False),
        "original_content": """计算机软件著作权证书

一、著作权清单

序号 | 软件名称 | 登记号 | 著作权人 | 首次发表日期 | 登记日期
--- | --- | --- | --- | --- | ---
1 | | | | | 
2 | | | | | 
3 | | | | | 
4 | | | | | 
5 | | | | | 

二、软件说明
主要产品/技术平台：

1. __________
   功能描述：__________
   技术特点：__________

2. __________
   功能描述：__________
   技术特点：__________

三、知识产权声明
本公司声明以上软件产品均为自主研发，拥有全部知识产权，无侵权风险。

投标人（盖章）：__________
日期：__________

【说明】请上传软件著作权登记证书扫描件（加盖公章），每项著作权对应一份证书。
""",
    },
    {
        "doc_type": "project_strength",
        "doc_name": "项目实力-项目数量/金额",
        "has_fillable_fields": True,
        "is_star_item": True,
        "score_point": "技术评分 - 20分",
        "rule_description": "项目数量和合同金额是技术评审的核心指标，需提供真实有效的合同证明材料",
        "return_file_list": json.dumps([
            {"file_name": "项目业绩证明.pdf", "file_type": "pdf", "description": "合同关键页（盖章）或验收报告"}
        ], ensure_ascii=False),
        "original_content": """项目实力证明 - 项目数量与金额

一、同类项目业绩汇总

序号 | 项目名称 | 客户单位 | 合同金额(万元) | 合同签订时间 | 项目状态 | 备注
--- | --- | --- | --- | --- | --- | ---
1 | | | | | | 
2 | | | | | | 
3 | | | | | | 
4 | | | | | | 
5 | | | | | | 

合计 | — | — | | — | — | 

二、项目详细说明

项目1：__________
客户背景：__________
项目规模：__________
合同金额：人民币（大写）________元（RMB ￥________元）
实施周期：__________
主要成果：__________

三、证明材料说明
1. 请附合同关键页（含甲乙双方盖章、项目名称、金额、期限等）;
2. 如合同涉及保密条款，可隐去敏感信息，但关键数据需清晰可辨;
3. 附验收报告或客户满意度评价更佳。

投标人（盖章）：__________
日期：__________
""",
    },
    {
        "doc_type": "compliance_check",
        "doc_name": "应答前合规自查确认单",
        "has_fillable_fields": True,
        "is_star_item": True,
        "score_point": "技术评分 - 5分",
        "rule_description": "应答前合规自查确认单用于确保投标文件符合招标文件要求，减少被否决的风险",
        "return_file_list": json.dumps([
            {"file_name": "合规自查确认单.xlsx", "file_type": "excel", "description": "逐项合规检查结果"}
        ], ensure_ascii=False),
        "original_content": """应答前合规自查确认单

项目名称：__________
招标编号：__________

一、投标文件合规检查

序号 | 检查项目 | 检查内容 | 检查结果 | 备注
--- | --- | --- | --- | ---
1 | 文件完整性 | 投标文件是否包含所有要求的章节 | | 
2 | 签章合规性 | 关键页是否按要求签字盖章 | | 
3 | 资质证书 | 营业执照、资质证书是否有效 | | 
4 | 业绩证明 | 合同、验收报告是否齐全 | | 
5 | 技术方案 | 是否完整响应招标文件技术要求 | | 
6 | 商务条款 | 是否满足招标文件商务条款 | | 
7 | 密封要求 | 投标文件是否按要求密封 | | 
8 | 递交时限 | 是否在截止时间前递交 | | 
9 | 保证金 | 投标保证金是否按时缴纳 | | 
10 | 授权文件 | 法定代表人授权书是否有效 | | 

二、自查结论
□ 全部检查项通过，投标文件完全符合要求
□ 存在以下问题，已采取补救措施：

问题说明：__________
补救措施：__________

三、确认签字

编制人（签字）：__________ 日期：__________
审核人（签字）：__________ 日期：__________

【说明】请在"检查结果"列填写：不涉及 / 已核查（通过） / 已核查（有问题）
""",
    },
    {
        "doc_type": "service_commitment",
        "doc_name": "服务承诺书",
        "has_fillable_fields": True,
        "is_star_item": False,
        "score_point": "技术评分 - 10分",
        "rule_description": "服务承诺书是技术评审的重要内容，需明确服务范围、维保期限、响应时间等关键指标",
        "return_file_list": json.dumps([
            {"file_name": "服务承诺书.docx", "file_type": "word", "description": "服务承诺书"}
        ], ensure_ascii=False),
        "original_content": """服务承诺书

致：【招标人名称】

我方（投标人名称）就本项目（项目名称：__________，招标编号：__________）的售后服务郑重承诺如下：

一、服务范围
本项目范围内的系统/产品/服务，包括：
1. __________
2. __________
3. __________

二、维保期限
□ 质保期__________年（自项目验收合格之日起计算）
□ 维保期__________年（自质保期满后计算）

三、服务内容
1. 技术支持：7×24小时技术支持热线，15分钟内响应
2. 软件升级：免费提供有效期内的版本升级
3. 故障处理：
   - 紧急故障：2小时内到达现场，4小时内恢复
   - 一般故障：4小时内远程解决，24小时内现场处理
4. 定期巡检：每季度提供一次系统巡检服务
5. 培训支持：提供操作培训和技术文档

四、服务保障
1. 配备专职服务团队，人员数量__________名
2. 建立客户档案，制定个性化服务方案
3. 定期回访，及时了解客户需求
4. 设立服务监督热线：__________

五、违约责任
如我方未按上述承诺提供服务，愿承担相应违约责任。

投标人（盖章）：__________
法定代表人或授权代表（签字）：__________
日期：__________
""",
    },
    {
        "doc_type": "additional_content",
        "doc_name": "应答人认为有必要进行阐述的其他内容",
        "has_fillable_fields": True,
        "is_star_item": False,
        "score_point": "技术评分 - 视内容",
        "rule_description": "用于投标人补充说明技术方案中的亮点、创新点或其他需要阐述的内容",
        "return_file_list": json.dumps([
            {"file_name": "补充说明材料.docx", "file_type": "word", "description": "补充说明文档"}
        ], ensure_ascii=False),
        "original_content": """应答人认为有必要进行阐述的其他内容

致：【招标人名称】

我方（投标人名称）就本项目（项目名称：__________，招标编号：__________）补充说明如下：

一、技术亮点与创新

1. 技术创新点
   （请描述本项目采用的核心技术、创新方案或差异化优势）

   _________________________________________________
   _________________________________________________

2. 差异化优势
   与市场上其他解决方案相比，本方案的核心优势：

   _________________________________________________
   _________________________________________________

二、同类项目经验

1. 核心技术团队介绍
   团队负责人：__________
   团队规模：__________
   核心技术能力：__________

2. 已完成的同类项目
   （简述与本项目类似的成功案例）

   _________________________________________________

三、其他需要说明的事项

（如有专利技术、获奖证书、行业资质等补充材料，请在此说明）

_________________________________________________
_________________________________________________
_________________________________________________

投标人（盖章）：__________
法定代表人或授权代表（签字）：__________
日期：__________
""",
    },
    {
        "doc_type": "tech_cover",
        "doc_name": "技术部分封面",
        "has_fillable_fields": True,
        "is_star_item": False,
        "score_point": "必备文件",
        "rule_description": "技术部分投标文件封面，包含项目名称、投标人、日期等关键信息",
        "return_file_list": json.dumps([
            {"file_name": "技术投标文件.pdf", "file_type": "pdf", "description": "技术部分投标文件"}
        ], ensure_ascii=False),
        "original_content": """【技术投标文件封面】

项目名称：__________
项目编号：__________

【技术投标文件】

投标人：__________
（加盖公章）

法定代表人或授权代表（签字）：__________

日期：__________
（投标截止时间前一天）


========================================


投标文件内容清单

一、技术建议书
二、技术方案
三、技术偏离表
四、公司资质证明
五、项目业绩证明
六、服务承诺书
七、其他补充材料

========================================

投标人地址：__________
联系人：__________
联系电话：__________

【说明】本封面作为技术投标文件首页，需加盖投标人公章。
""",
    },
]


def get_or_create_project(db: Session, project_id: str) -> Project:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")
    return project


def ensure_technical_documents(db: Session, project_id: str) -> list[TechnicalDocument]:
    """确保项目有技术文档模板数据，如无则创建"""
    get_or_create_project(db, project_id)

    existing = db.query(TechnicalDocument).filter(TechnicalDocument.project_id == project_id).all()
    if existing:
        return existing

    created = []
    for tpl in TECHNICAL_DOCUMENT_TEMPLATES:
        doc = TechnicalDocument(
            id=f"td_{uuid4().hex[:12]}",
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


def list_technical_documents(db: Session, project_id: str) -> list[TechnicalDocumentSummary]:
    docs = ensure_technical_documents(db, project_id)
    return [TechnicalDocumentSummary.model_validate(d) for d in docs]


def get_technical_document_detail(db: Session, project_id: str, doc_id: str) -> TechnicalDocumentDetail:
    docs = ensure_technical_documents(db, project_id)
    for d in docs:
        if d.id == doc_id:
            return TechnicalDocumentDetail.model_validate(d)
    from fastapi import HTTPException, status
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在")


def update_technical_document(
    db: Session, project_id: str, doc_id: str, payload: TechnicalDocumentUpdateRequest
) -> TechnicalDocumentDetail:
    doc = db.query(TechnicalDocument).filter(
        TechnicalDocument.id == doc_id,
        TechnicalDocument.project_id == project_id,
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
    return TechnicalDocumentDetail.model_validate(doc)