from typing import Any
import json
import re
import logging

from app.models.settings import AIConfig

logger = logging.getLogger(__name__)


class LLMParsingClient:
    def extract_tender_fields(self, text: str) -> dict[str, Any]:
        from app.db.session import SessionLocal
        from openai import OpenAI

        try:
            with SessionLocal() as db:
                provider = db.query(AIConfig).filter(
                    AIConfig.is_active == True
                ).first()

                if not provider or not provider.api_key:
                    logger.warning("[LLM] No active provider found - skipping extraction")
                    return {}

                logger.info(f"[LLM] Extract: model={provider.model}, provider={provider.provider}, text_len={len(text)}")
                client = OpenAI(
                    api_key=provider.api_key,
                    base_url=provider.base_url,
                    timeout=180.0,
                    default_headers={"User-Agent": "claude-code/0.1.0"},
                )

                model = provider.model
                protocol = provider.provider

                return self._call_llm(client, model, protocol, text)
        except Exception as e:
            logger.warning(f"LLM Parsing error: {e}")
            return {}

    def _call_llm(self, client, model: str, protocol: str, text: str) -> dict[str, Any]:
        prompt = """
        你是一个专业的招投标文档解析专家。请仔细阅读以下招标文件内容（可能包含招标公告、技术规范、评审办法、合同条款、附件表格等），并提取出以下关键信息。
        如果某些信息在文档中找不到，请填写 "待补充"。

        === 星标项提取规则（非常重要）===
        ★ 和 * 符号出现在行首时，通常表示关键条款。星标项常见于以下章节：评分标准、资质要求、废标条款、技术要求。
        星标项通常格式为：★内容 或 *内容，也可能写作"关键条款"、"实质性要求"、"否决条款"。请特别注意评分标准表格中的星标行。
        每个星标项必须提取：项名称、具体内容、来源章节、符号类型（★或*）。

        === 评分标准提取规则 ===
        评分重点必须包含完整的评分表格内容，包括每项的分值、评分标准、加分项。如果评分标准以表格形式出现，请逐行提取。
        需要包含：评分大类（价格分/技术分/商务分）、各类权重、每小项的分值和评分细则。

        === 废标条款提取规则 ===
        废标条款必须完整列出所有会导致投标无效的情形，不要遗漏任何一条。
        包括但不限于：未按要求密封、未签字盖章、未提交保证金、资质不满足、技术参数偏离、逾期送达等。

        === 交叉验证提示 ===
        如果文档中存在规则可提取的字段（如项目名称、招标编号、截止时间），请仍然尝试提取作为交叉验证。

        要求提取的字段：
        1. 项目名称 - 完整的招标项目名称
        2. 招标编号 - 招标公告或文件编号
        3. 标书类型 - 如：公开招标、邀请招标、竞争性谈判等
        4. 投标截止时间 - 递交投标文件的截止时间
        5. 预算金额 - 项目预算或最高限价
        6. 标书起始时间 - 招标文件开始发售时间
        7. 标书结束时间 - 招标文件发售截止时间
        8. 是否有保证金 - 是否需要缴纳投标保证金（是/否）
        9. 保证金金额 - 保证金的具体金额
        10. 保证金形式 - 保证金缴纳方式（如：银行转账、保函等）
        11. 必备资质 - 投标人资格要求
        12. 付款条款 - 合同付款方式和条件
        13. 交付周期 - 工期或服务期要求
        14. 评分重点 - 详细说明价格、商务、技术等评分比重，以及关键加分项，**必须包含评分表中的详细内容**
        15. 技术要求 - 核心建设内容和技术规范
        16. 服务承诺 - 售后服务要求
        17. 是否需要签字盖章 - 投标文件是否需要签字盖章（是/否）
        18. 是否有项目澄清会 - 是否召开投标答疑或澄清会议（是/否）
        19. 项目澄清会时间 - 澄清会议的时间
        20. 项目澄清会链接 - 澄清会议的链接或地址
        21. 星标项列表 - **非常重要**：提取所有带星标（★或*）或标注为"关键条款"、"实质性要求"、"否决条款"的内容，每项单独列出，包含名称、内容、来源章节、符号类型
        22. 废标条款 - 所有会导致投标被否决的条款，逐条列出
        23. 合同条款 - 合同主要条款，包括违约责任、验收标准、质保期等
        24. 商务条款 - 商务要求，包括付款方式、发票要求、履约保证金等
        25. 投标人须知 - 投标人须知中的关键要求，包括投标文件组成、密封要求、递交方式等

        请务必以 JSON 格式返回，包含以下结构，不要输出其他无关内容：
        ```json
        {
          "项目名称": {"value": "...", "confidence": "95%"},
          "招标编号": {"value": "...", "confidence": "98%"},
          "标书类型": {"value": "...", "confidence": "90%"},
          "投标截止时间": {"value": "...", "confidence": "90%"},
          "预算金额": {"value": "...", "confidence": "90%"},
          "标书起始时间": {"value": "...", "confidence": "85%"},
          "标书结束时间": {"value": "...", "confidence": "85%"},
          "是否有保证金": {"value": "是/否", "confidence": "90%"},
          "保证金金额": {"value": "...", "confidence": "85%"},
          "保证金形式": {"value": "...", "confidence": "85%"},
          "必备资质": {"value": "...", "confidence": "85%"},
          "付款条款": {"value": "...", "confidence": "85%"},
          "交付周期": {"value": "...", "confidence": "85%"},
          "评分重点": {"value": "详细的评分标准：...", "confidence": "95%"},
          "技术要求": {"value": "...", "confidence": "80%"},
          "服务承诺": {"value": "...", "confidence": "80%"},
          "是否需要签字盖章": {"value": "是/否", "confidence": "90%"},
          "是否有项目澄清会": {"value": "是/否", "confidence": "90%"},
          "项目澄清会时间": {"value": "...", "confidence": "85%"},
          "项目澄清会链接": {"value": "...", "confidence": "80%"},
          "星标项列表": [
            {"name": "项名称", "content": "具体要求", "source_section": "来源章节", "symbol": "★或*", "confidence": "95%"}
          ],
          "废标条款": {"value": "逐条列出所有废标情形", "confidence": "90%"},
          "合同条款": {"value": "合同主要条款内容", "confidence": "85%"},
          "商务条款": {"value": "商务要求内容", "confidence": "85%"},
          "投标人须知": {"value": "投标人须知关键要求", "confidence": "85%"}
        }
        ```

待解析文本(截取前40000字，规则引擎已处理结构化字段，你专注于复杂语义提取)：
        """ + text[:40000]

        system_prompt = "你是一个专业的招投标解析AI助手。"
        user_prompt = prompt

        try:
            if protocol == "anthropic":
                import httpx
                headers = {
                    "x-api-key": client.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                }
                base_url_raw = client.base_url
                if hasattr(base_url_raw, "rstrip"):
                    base_url_str = str(base_url_raw)
                else:
                    base_url_str = str(base_url_raw) if base_url_raw else "https://api.anthropic.com/v1"
                if not base_url_str.endswith("/messages"):
                    base_url_str = base_url_str.rstrip("/") + "/messages"

                payload = {
                    "model": model,
                    "max_tokens": 2048,
                    "temperature": 0.1,
                    "system": system_prompt,
                    "messages": [{"role": "user", "content": user_prompt}],
                }

                response = httpx.post(base_url_str, headers=headers, json=payload, timeout=180.0)
                response.raise_for_status()
                data = response.json()
                content = data.get("content", [{}])[0].get("text", "")
            else:
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.1,
                    extra_headers={"User-Agent": "claude-code/0.1.0"}
                )
                content = response.choices[0].message.content or ""

            return self._parse_json_payload(content)
        except Exception as e:
            logger.warning(f"LLM call error: {e}")
            return {}

    def _parse_json_payload(self, content: str) -> dict[str, Any]:
        match = re.search(r"```json\s*(.*?)\s*```", content, re.DOTALL)
        if not match:
            match = re.search(r"```\s*(.*?)\s*```", content, re.DOTALL)
        json_str = match.group(1) if match else content
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.warning(f"[LLM] Initial JSON parse failed: {e}")
            match2 = re.search(r"\{.*\}", json_str, re.DOTALL)
            if match2:
                try:
                    return json.loads(match2.group(0))
                except Exception as e2:
                    logger.warning(f"[LLM] Fallback JSON parse also failed: {e2}")
            # Regex fallback: extract key-value pairs from malformed output
            return self._regex_fallback_extract(content)

    def _regex_fallback_extract(self, content: str) -> dict[str, Any]:
        logger.info("[LLM] Attempting regex fallback extraction")
        result: dict[str, Any] = {}
        known_fields = [
            "项目名称", "招标编号", "标书类型", "投标截止时间", "预算金额",
            "标书起始时间", "标书结束时间", "是否有保证金", "保证金金额",
            "保证金形式", "必备资质", "付款条款", "交付周期", "评分重点",
            "技术要求", "服务承诺", "是否需要签字盖章", "是否有项目澄清会",
            "项目澄清会时间", "项目澄清会链接", "废标条款", "合同条款",
            "商务条款", "投标人须知",
        ]
        for field in known_fields:
            pattern = rf'"{field}"\s*:\s*\{{\s*"value"\s*:\s*"([^"]*)"'
            m = re.search(pattern, content)
            if m:
                result[field] = {"value": m.group(1), "confidence": "60%"}
        star_pattern = r'"name"\s*:\s*"([^"]*)"[^}]*"content"\s*:\s*"([^"]*)"'
        star_matches = re.findall(star_pattern, content)
        if star_matches:
            result["星标项列表"] = [
                {"name": name, "content": content_val, "source_section": "", "symbol": "★", "confidence": "60%"}
                for name, content_val in star_matches
            ]
        if result:
            logger.info(f"[LLM] Regex fallback extracted {len(result)} fields")
        else:
            logger.warning("[LLM] Regex fallback extracted nothing")
        return result


    def summarize_text(self, text: str, title: str = "", max_words: int = 2000) -> str:
        from app.db.session import SessionLocal
        from openai import OpenAI

        try:
            with SessionLocal() as db:
                provider = db.query(AIConfig).filter(AIConfig.is_active == True).first()
                if not provider or not provider.api_key:
                    return ""

                client = OpenAI(
                    api_key=provider.api_key,
                    base_url=provider.base_url,
                    timeout=180.0,
                    default_headers={"User-Agent": "claude-code/0.1.0"},
                )

                system_prompt = (
                    "你是招投标文档摘要助手。请对以下超长章节生成精炼摘要，"
                    "保留所有关键评分点、资质要求、技术参数、合同条款和商务条件。"
                    "摘要需包含：核心要求、关键数字、硬性门槛、注意事项。"
                )
                user_prompt = f"章节名称：{title}\n\n原始内容（前12000字）：\n{text[:12000]}\n\n请生成摘要（约{max_words}字）："

                model = provider.model
                protocol = provider.provider

                if protocol == "anthropic":
                    import httpx
                    headers = {
                        "x-api-key": client.api_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json",
                    }
                    base_url_str = str(client.base_url) if client.base_url else "https://api.anthropic.com/v1"
                    if not base_url_str.endswith("/messages"):
                        base_url_str = base_url_str.rstrip("/") + "/messages"
                    payload = {
                        "model": model,
                        "max_tokens": min(max_words, 4096),
                        "temperature": 0.2,
                        "system": system_prompt,
                        "messages": [{"role": "user", "content": user_prompt}],
                    }
                    resp = httpx.post(base_url_str, headers=headers, json=payload, timeout=180.0)
                    resp.raise_for_status()
                    data = resp.json()
                    return data.get("content", [{}])[0].get("text", "").strip()
                else:
                    resp = client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                        temperature=0.2,
                        max_tokens=min(max_words, 4096),
                        extra_headers={"User-Agent": "claude-code/0.1.0"},
                    )
                    return (resp.choices[0].message.content or "").strip()
        except Exception as e:
            logger.warning(f"Summarization error: {e}")
            return ""


llm_parsing_client = LLMParsingClient()
