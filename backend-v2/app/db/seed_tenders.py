"""招标信息种子数据"""
from uuid import uuid4

SEED_TENDERS = [
    {
        "id": "tend_a1b2c3d4e5f6",
        "title": "某市政府智慧城市平台建设项目招标公告",
        "source_url": "https://www.example.gov.cn/zbgg/2024/001",
        "publish_date": "2024-01-15",
        "deadline": "2024-02-28",
        "amount": "¥ 5,000,000",
        "project_type": "智慧城市/政府信息化",
        "description": "本项目旨在建设全市统一的智慧城市数据平台，整合政务、医疗、教育、交通等数据资源，提供跨部门数据共享和业务协同能力。",
        "decision": "pending",
        "reject_reason": "",
        "project_id": "",
        "user_id": "user-001",
    },
    {
        "id": "tend_b2c3d4e5f6a1",
        "title": "某省人民医院信息化建设二期招标",
        "source_url": "https://www.example-hospital.com.cn/zb/2024/015",
        "publish_date": "2024-01-20",
        "deadline": "2024-03-10",
        "amount": "¥ 3,200,000",
        "project_type": "医疗信息化",
        "description": "建设内容包括：HIS系统升级、PACS医学影像系统、远程会诊平台、智慧病房物联网系统。",
        "decision": "pending",
        "reject_reason": "",
        "project_id": "",
        "user_id": "user-001",
    },
    {
        "id": "tend_c3d4e5f6a1b2",
        "title": "某高校智慧校园建设项目招标",
        "source_url": "https://www.example-edu.cn/tender/2024/032",
        "publish_date": "2024-01-25",
        "deadline": "2024-03-15",
        "amount": "¥ 2,800,000",
        "project_type": "教育信息化/智慧校园",
        "description": "智慧校园建设，包括校园一张网、一个数据中心、一站式服务平台，及智能安防、智慧教学等应用。",
        "decision": "pending",
        "reject_reason": "",
        "project_id": "",
        "user_id": "user-001",
    },
    {
        "id": "tend_d4e5f6a1b2c3",
        "title": "某市公安局视频监控智能化改造项目",
        "source_url": "https://www.example-gov-security.cn/zb/2024/008",
        "publish_date": "2024-02-01",
        "deadline": "2024-03-20",
        "amount": "¥ 8,000,000",
        "project_type": "安防智能化",
        "description": "全市视频监控高清化、智能化改造，引入AI人脸识别、行为分析、车辆识别等能力，构建城市级视频感知网络。",
        "decision": "pending",
        "reject_reason": "",
        "project_id": "",
        "user_id": "user-001",
    },
    {
        "id": "tend_e5f6a1b2c3d4",
        "title": "某制造企业工业互联网平台建设招标",
        "source_url": "https://www.example-industry.com/bid/2024/021",
        "publish_date": "2024-02-05",
        "deadline": "2024-03-25",
        "amount": "¥ 4,500,000",
        "project_type": "工业互联网/制造业",
        "description": "建设连接工厂设备、供应链和客户的工业互联网平台，实现设备远程监控、预测性维护、智能排产。",
        "decision": "pending",
        "reject_reason": "",
        "project_id": "",
        "user_id": "user-001",
    },
]


def seed_tenders(db):
    from app.models.tender import Tender
    for data in SEED_TENDERS:
        tender = Tender(**data)
        db.add(tender)
