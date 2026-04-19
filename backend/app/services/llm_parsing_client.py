from typing import Any
import json
import re

from app.models.llm_provider import LLMProviderModel


class LLMParsingClient:
    def extract_tender_fields(self, text: str) -> dict[str, Any]:
        """使用数据库中激活的 LLM Provider 进行解析"""
        from app.db.session import SessionLocal
        from openai import OpenAI

        try:
            with SessionLocal() as db:
                provider = db.query(LLMProviderModel).filter(
                    LLMProviderModel.is_active == True
                ).first()

                if not provider or not provider.api_key:
                    print("No active LLM provider found in database")
                    return {}

                client = OpenAI(
                    api_key=provider.api_key,
                    base_url=provider.base_url,
                    timeout=45.0,
                )

                model = provider.model
                protocol = getattr(provider, "protocol", "openai")

                return self._call_llm(client, model, protocol, text)
        except Exception as e:
            print(f"LLM Parsing error: {e}")
            return {}

    def _call_llm(self, client, model: str, protocol: str, text: str) -> dict[str, Any]:
        prompt = """
        你是一个专业的招投标文档解析专家。请仔细阅读以下招标文件内容（可能包含招标公告、技术规范、评审办法、合同条款、附件表格等），并提取出以下关键信息。
        如果某些信息在文档中找不到，请填写 "待补充"。

        要求提取的字段：
        1. 项目名称
        2. 招标编号
        3. 投标截止时间
        4. 预算金额 (或最高限价)
        5. 必备资质 (投标人资格要求)
        6. 付款条款
        7. 交付周期 (或工期要求)
        8. 评分重点 (详细说明价格、商务、技术等评分比重，以及关键加分项，**必须包含评分表中的详细内容**)
        9. 技术要求 (核心建设内容)
        10. 服务承诺 (售后要求)

        请务必以 JSON 格式返回，包含以下结构，不要输出其他无关内容：
        ```json
        {
          "项目名称": {"value": "...", "confidence": "95%"},
          "招标编号": {"value": "...", "confidence": "98%"},
          "投标截止时间": {"value": "...", "confidence": "90%"},
          "预算金额": {"value": "...", "confidence": "90%"},
          "必备资质": {"value": "...", "confidence": "85%"},
          "付款条款": {"value": "...", "confidence": "85%"},
          "交付周期": {"value": "...", "confidence": "85%"},
          "评分重点": {"value": "详细的评分标准：...", "confidence": "95%"},
          "技术要求": {"value": "...", "confidence": "80%"},
          "服务承诺": {"value": "...", "confidence": "80%"}
        }
        ```

        待解析文本(截取前80000字以防超出长度)：
        """ + text[:80000]

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

                response = httpx.post(base_url_str, headers=headers, json=payload, timeout=45.0)
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
                )
                content = response.choices[0].message.content or ""

            return self._parse_json_payload(content)
        except Exception as e:
            print(f"LLM call error: {e}")
            return {}

    def _parse_json_payload(self, content: str) -> dict[str, Any]:
        match = re.search(r"```json\s*(.*?)\s*```", content, re.DOTALL)
        if not match:
            match = re.search(r"```\s*(.*?)\s*```", content, re.DOTALL)
        json_str = match.group(1) if match else content
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            match2 = re.search(r"\{.*\}", json_str, re.DOTALL)
            if match2:
                try:
                    return json.loads(match2.group(0))
                except Exception:
                    pass
            return {}


llm_parsing_client = LLMParsingClient()
