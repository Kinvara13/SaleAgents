from typing import Any
import json
import re
from openai import OpenAI
from app.core.config import settings

class LLMParsingClient:
    def __init__(self, api_key: str, base_url: str, model_name: str):
        self.api_key = api_key
        self.base_url = base_url
        self.model_name = model_name
        self._build_client()

    def _build_client(self):
        try:
            self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        except ImportError:
            self.client = None

    def _parse_json_payload(self, content: str) -> dict[str, Any]:
        match = re.search(r"```json\s*(.*?)\s*```", content, re.DOTALL)
        if not match:
            match = re.search(r"```\s*(.*?)\s*```", content, re.DOTALL)
        json_str = match.group(1) if match else content
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            return {}

    def extract_tender_fields(self, text: str) -> dict[str, Any]:
        if not self.client:
            return {}
        
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

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "你是一个专业的招投标解析AI助手。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
            )
            content = response.choices[0].message.content or ""
            return self._parse_json_payload(content)
        except Exception as e:
            print(f"LLM Parsing error: {e}")
            return {}

llm_parsing_client = LLMParsingClient(
    api_key=settings.llm_api_key,
    base_url=settings.llm_base_url,
    model_name=settings.llm_model,
)
