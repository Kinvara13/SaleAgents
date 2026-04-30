import re
from pathlib import PurePosixPath
from typing import Any


TEMPLATE_FILE_EXTENSIONS = {".docx", ".doc", ".pdf", ".txt", ".xlsx", ".xls"}


def normalize_template_path(path: str) -> str:
    value = str(path or "").replace("\\", "/").strip()
    parts = [part for part in PurePosixPath(value).parts if part not in ("", ".")]
    return "/".join(parts)


def classify_template_file(name: str, path: str = "") -> str:
    text = f"{path}/{name}".lower()
    chinese_text = f"{path}/{name}"

    if any(keyword in chinese_text for keyword in ("商务", "报价", "开标", "法定代表", "授权", "营业执照", "承诺函", "偏离表")):
        return "business"
    if any(keyword in chinese_text for keyword in ("技术", "方案", "建议书", "架构", "实施", "服务", "运维", "维保", "人员", "项目经理", "案例")):
        return "technical"
    if any(keyword in chinese_text for keyword in ("方案建议", "硬件资源", "资源占用")):
        return "proposal"
    if any(keyword in text for keyword in ("business", "commercial", "quote", "quotation")):
        return "business"
    if any(keyword in text for keyword in ("technical", "tech", "proposal", "solution", "maintenance")):
        return "technical"
    return "other"


def template_section_label(section_type: str) -> str:
    return {
        "business": "商务部分",
        "technical": "技术部分",
        "proposal": "方案/报价部分",
        "other": "其他回标模板",
    }.get(section_type, "其他回标模板")


def should_include_template_file(name: str, path: str = "") -> bool:
    suffix = PurePosixPath(str(name)).suffix.lower()
    if suffix not in TEMPLATE_FILE_EXTENSIONS:
        return False

    text = f"{path}/{name}"
    lower_text = text.lower()
    tender_keywords = ("招标文件", "采购文件", "采购需求", "需求书", "评分办法", "评标办法", "技术规范书", "tender", "bidding-doc")
    template_keywords = ("模板", "模版", "回标", "投标", "应答", "响应", "格式", "附件", "template", "response", "proposal")
    if any(keyword in lower_text for keyword in tender_keywords) and not any(keyword in lower_text for keyword in template_keywords):
        return False
    return True


def normalize_template_files(files: list[dict[str, Any]] | dict[str, Any] | None) -> list[dict[str, Any]]:
    if not isinstance(files, list):
        return []

    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, raw in enumerate(files):
        if not isinstance(raw, dict):
            continue
        name = str(raw.get("name") or raw.get("filename") or "").strip()
        path = normalize_template_path(str(raw.get("path") or name))
        if not name and path:
            name = PurePosixPath(path).name
        if not name:
            continue
        if not should_include_template_file(name, path):
            continue

        key = re.sub(r"\s+", "", f"{path or name}".lower())
        if key in seen:
            continue
        seen.add(key)

        section_type = str(raw.get("section_type") or "").strip() or classify_template_file(name, path)
        result.append({
            **raw,
            "id": str(raw.get("id") or f"tpl_{index + 1}"),
            "name": name,
            "path": path or name,
            "status": raw.get("status") or "待分配",
            "selected": bool(raw.get("selected", True)),
            "icon": raw.get("icon") or "📄",
            "section_type": section_type,
            "section_name": template_section_label(section_type),
        })
    return result
