import json
import logging
import re
from typing import Any

from app.core.config import settings
from app.db.session import SessionLocal
from app.models.llm_provider import LLMProviderModel

logger = logging.getLogger(__name__)


class _BaseLLMClient:
    def _get_active_provider(self):
        try:
            with SessionLocal() as db:
                return db.query(LLMProviderModel).filter(LLMProviderModel.is_active == True).first()
        except Exception as e:
            logger.error(f"Error querying active LLM provider: {e}")
            return None

    @property
    def is_llm_ready(self) -> bool:
        provider = self._get_active_provider()
        if provider and provider.api_key:
            return True
        return settings.llm_ready

    @property
    def current_model(self) -> str:
        provider = self._get_active_provider()
        if provider and provider.model:
            return provider.model
        return settings.llm_model

    def _chat_completion(self, system_prompt: str, user_prompt: str, temperature: float = 0.3, max_tokens: int = 2048) -> str | None:
        provider = self._get_active_provider()
        
        if provider:
            base_url = (provider.base_url or "").strip() or None
            api_key = (provider.api_key or "").strip()
            model = provider.model
            protocol = getattr(provider, "protocol", "openai")
        else:
            base_url = (settings.llm_base_url or "").strip() or None
            api_key = (settings.llm_api_key or "").strip()
            model = settings.llm_model
            protocol = "openai"

        if protocol == "anthropic":
            import httpx
            headers = {
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            url = base_url or "https://api.anthropic.com/v1"
            if not url.endswith("/messages"):
                url = url.rstrip("/") + "/messages"
                
            payload = {
                "model": model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "system": system_prompt,
                "messages": [
                    {"role": "user", "content": user_prompt}
                ]
            }
            
            response = httpx.post(url, headers=headers, json=payload, timeout=float(settings.llm_timeout_seconds))
            response.raise_for_status()
            data = response.json()
            return data.get("content", [{}])[0].get("text", "")
            
        else: # openai
            try:
                from openai import OpenAI
            except ImportError as exc:
                raise RuntimeError("openai package is not installed.") from exc

            client = OpenAI(
                api_key=api_key,
                base_url=base_url,
                timeout=float(settings.llm_timeout_seconds),
            )

            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content

    def _parse_json_payload(self, content: str) -> dict[str, Any]:
        candidate = content.strip()
        if candidate.startswith("```"):
            candidate = re.sub(r"^```(?:json)?\s*", "", candidate)
            candidate = re.sub(r"\s*```$", "", candidate)

        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", candidate, flags=re.DOTALL)
            if not match:
                raise
            return json.loads(match.group(0))


class LLMReviewClient(_BaseLLMClient):
    """Thin wrapper around the external LLM provider for contract semantic review."""

    def review_contract_semantics(
        self,
        *,
        contract_name: str,
        contract_type: str,
        clauses: list[dict[str, str]],
        rule_issues: list[dict[str, str]],
    ) -> list[dict[str, str]]:
        if not self.is_llm_ready:
            return []

        prompt = self._build_prompt(
            contract_name=contract_name,
            contract_type=contract_type,
            clauses=clauses,
            rule_issues=rule_issues,
        )

        try:
            content = self._chat_completion(
                system_prompt=self._system_prompt(),
                user_prompt=prompt,
                temperature=0.3,
                max_tokens=2048,
            )
            content = (content or "").strip()
            if not content:
                logger.warning("LLM semantic review returned empty content.")
                return []
            payload = self._parse_json_payload(content)
            return self._normalize_issues(payload, clauses)
        except Exception as exc:  # noqa: BLE001
            logger.warning("LLM semantic review failed, falling back to heuristic checks: %s", exc)
            return []

    def _system_prompt(self) -> str:
        return (
            "你是资深企业法务审查助手。"
            "你的任务是补充规则引擎没有稳定覆盖的语义风险。"
            "只基于给定合同条款输出高置信度问题，不要臆造条款，不要泛泛而谈。"
            "重点识别模糊责任、隐含范围扩张、单方变更、绝对结果承诺、缺少前置条件或免责边界。"
            "输出必须是 JSON 对象，不要带 Markdown 代码块。"
        )

    def _build_prompt(
        self,
        *,
        contract_name: str,
        contract_type: str,
        clauses: list[dict[str, str]],
        rule_issues: list[dict[str, str]],
    ) -> str:
        max_issues = settings.llm_max_review_issues
        clause_lines = []
        for clause in clauses[:40]:
            clause_lines.append(
                f"[ClauseNo={clause['clause_no']}] [Title={clause['title']}] [Source={clause['source_ref']}]\n"
                f"{clause['content']}"
            )

        existing_rule_titles = [item["title"] for item in rule_issues if item.get("rule_name") != "no_rule_hit"]

        schema = {
            "issues": [
                {
                    "title": "风险标题",
                    "type": "语义责任风险",
                    "level": "P1",
                    "clause_no": 1,
                    "document": "服务条款",
                    "detail": "解释为什么该措辞会带来责任或履约风险",
                    "evidence": "直接摘录命中的合同原文",
                    "suggestion": "具体修订建议",
                }
            ]
        }

        return (
            f"合同名称：{contract_name}\n"
            f"合同类型：{contract_type}\n"
            f"已由规则引擎命中的问题标题：{json.dumps(existing_rule_titles, ensure_ascii=False)}\n"
            f"请补充最多 {max_issues} 条“规则之外”的语义风险，避免重复已有规则结论。\n"
            "优先输出高价值问题；如果没有明确语义风险，则返回 {\"issues\":[]}。\n"
            "返回字段要求：\n"
            f"{json.dumps(schema, ensure_ascii=False)}\n"
            "合同条款如下：\n"
            f"{chr(10).join(clause_lines)}"
        )

    def _normalize_issues(
        self,
        payload: dict[str, Any],
        clauses: list[dict[str, str]],
    ) -> list[dict[str, str]]:
        raw_issues = payload.get("issues", [])
        if not isinstance(raw_issues, list):
            return []

        clause_by_no = {item["clause_no"]: item for item in clauses}
        normalized: list[dict[str, str]] = []

        for index, raw in enumerate(raw_issues[: settings.llm_max_review_issues], start=1):
            if not isinstance(raw, dict):
                continue

            title = str(raw.get("title", "")).strip()
            detail = str(raw.get("detail", "")).strip()
            evidence = str(raw.get("evidence", "")).strip()
            suggestion = str(raw.get("suggestion", "")).strip()
            if not title or not detail or not evidence or not suggestion:
                continue

            clause_no = self._safe_int(raw.get("clause_no"))
            clause = clause_by_no.get(clause_no)
            document = str(raw.get("document", "")).strip()
            if clause is not None:
                document = f"{document or '合同语义审查'} · {clause['title']}"
            elif not document:
                document = "合同语义审查"

            level = self._normalize_level(str(raw.get("level", "P2")).strip())
            issue_type = str(raw.get("type", "")).strip() or "LLM 语义风险"

            normalized.append(
                {
                    "title": title[:255],
                    "type": issue_type[:64],
                    "level": level,
                    "status": "待处理",
                    "document": document[:255],
                    "detail": detail[:2000],
                    "evidence": evidence[:280],
                    "suggestion": suggestion[:2000],
                    "rule_name": f"llm_semantic_{index}",
                }
            )

        return normalized

    def _normalize_level(self, value: str) -> str:
        if value in {"P0", "P1", "P2", "P3"}:
            return value
        return "P2"

    def _safe_int(self, value: Any) -> int | None:
        try:
            return int(value)
        except (TypeError, ValueError):
            return None


class LLMGenerationClient(_BaseLLMClient):
    """Optional LLM generation client for bid response sections."""

    def generate_bid_section(
        self,
        *,
        project_name: str,
        client_name: str,
        section_title: str,
        project_summary: str,
        tender_requirements: str,
        delivery_deadline: str,
        service_commitment: str,
        selected_assets: list[str],
        extracted_fields: dict[str, str],
        generation_todos: list[str],
    ) -> dict[str, Any] | None:
        if not self.is_llm_ready:
            return None

        prompt = self._build_prompt(
            project_name=project_name,
            client_name=client_name,
            section_title=section_title,
            project_summary=project_summary,
            tender_requirements=tender_requirements,
            delivery_deadline=delivery_deadline,
            service_commitment=service_commitment,
            selected_assets=selected_assets,
            extracted_fields=extracted_fields,
            generation_todos=generation_todos,
        )

        try:
            content = self._chat_completion(
                system_prompt=self._system_prompt(),
                user_prompt=prompt,
                temperature=0.3,
                max_tokens=2048,
            )
            content = (content or "").strip()
            if not content:
                logger.warning("LLM bid generation returned empty content for section %s.", section_title)
                return None
            payload = self._parse_json_payload(content)
            return self._normalize_section(payload, section_title)
        except Exception as exc:  # noqa: BLE001
            logger.warning("LLM bid generation failed for section %s, using fallback: %s", section_title, exc)
            return None

    def _system_prompt(self) -> str:
        return (
            "你是企业投标文件编写助手。"
            "你的任务是根据项目摘要、招标要求、交付约束和可选素材，生成单个回标章节。"
            "内容必须专业、克制、可直接进入正式回标文件。"
            "不要虚构资质、业绩、参数或客户事实；不确定的信息只能写成待补充或建议补充。"
            "输出必须是 JSON 对象，不要带 Markdown 代码块。"
        )

    def _build_prompt(
        self,
        *,
        project_name: str,
        client_name: str,
        section_title: str,
        project_summary: str,
        tender_requirements: str,
        delivery_deadline: str,
        service_commitment: str,
        selected_assets: list[str],
        extracted_fields: dict[str, str],
        generation_todos: list[str],
    ) -> str:
        schema = {
            "content": "使用 Markdown 的章节正文，必须以二级标题开头，例如 ## 总体技术方案",
            "citations": 3,
            "todos": 1,
        }

        return (
            f"项目名称：{project_name}\n"
            f"客户名称：{client_name}\n"
            f"章节标题：{section_title}\n"
            f"项目摘要：{project_summary or '待补充'}\n"
            f"招标要求：{tender_requirements or '待补充'}\n"
            f"交付时限：{delivery_deadline or '待补充'}\n"
            f"服务承诺：{service_commitment or '待补充'}\n"
            f"可引用素材：{json.dumps(selected_assets, ensure_ascii=False)}\n"
            f"抽取字段：{json.dumps(extracted_fields, ensure_ascii=False)}\n"
            f"待确认事项：{json.dumps(generation_todos[:5], ensure_ascii=False)}\n"
            "请只生成当前这个章节，不要输出整份标书。"
            "如果输入不足，请在内容中明确标出“待补充”，不要编造。"
            "返回字段要求：\n"
            f"{json.dumps(schema, ensure_ascii=False)}"
        )

    def _normalize_section(self, payload: dict[str, Any], section_title: str) -> dict[str, Any] | None:
        content = str(payload.get("content", "")).strip()
        if not content:
            return None

        citations = self._safe_int(payload.get("citations"))
        todos = self._safe_int(payload.get("todos"))
        if not content.startswith("## "):
            content = f"## {section_title}\n\n{content}"

        return {
            "content": content[:20000],
            "citations": max(1, citations or 1),
            "todos": max(0, todos or 0),
        }

    def _safe_int(self, value: Any) -> int | None:
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    def revise_bid_section(
        self,
        *,
        section_title: str,
        current_content: str,
        missing_requirements: list[str],
        check_notes: list[str],
        routed_assets: list[str],
        extracted_fields: dict[str, str],
    ) -> dict[str, Any] | None:
        if not self.is_llm_ready:
            return None

        schema = {
            "content": "修订后的 Markdown 章节正文，必须以二级标题开头",
            "citations": 3,
            "todos": 0,
        }
        prompt = (
            f"章节标题：{section_title}\n"
            f"当前章节内容：{current_content[:12000]}\n"
            f"待补评分点：{json.dumps(missing_requirements, ensure_ascii=False)}\n"
            f"自检问题：{json.dumps(check_notes, ensure_ascii=False)}\n"
            f"可引用素材：{json.dumps(routed_assets, ensure_ascii=False)}\n"
            f"项目字段：{json.dumps(extracted_fields, ensure_ascii=False)}\n"
            "请在不编造事实的前提下修订该章节，优先补足未覆盖评分点和显性缺口。"
            "无法确认的内容可以保留“待补充”，但不要遗漏评分项响应。"
            f"返回 JSON：{json.dumps(schema, ensure_ascii=False)}"
        )

        try:
            content = self._chat_completion(
                system_prompt="你是企业投标文件修订助手。你的任务是根据评分缺口和自检问题，对单个章节做二轮修订。不得编造资质、案例、参数或商务承诺。输出必须是 JSON 对象。",
                user_prompt=prompt,
                temperature=0.3,
                max_tokens=2048,
            )
            content = (content or "").strip()
            if not content:
                return None
            payload = self._parse_json_payload(content)
            return self._normalize_section(payload, section_title)
        except Exception as exc:  # noqa: BLE001
            logger.warning("LLM bid revision failed for section %s: %s", section_title, exc)
            return None


class LLMDecisionClient(_BaseLLMClient):
    """Thin wrapper around the external LLM provider for bid decision making."""

    def evaluate_project(
        self,
        *,
        project_name: str,
        client_name: str,
        extracted_fields: dict[str, str],
        rule_hits: list[dict[str, str]],
    ) -> dict[str, Any] | None:
        if not self.is_llm_ready:
            return None

        prompt = self._build_prompt(
            project_name=project_name,
            client_name=client_name,
            extracted_fields=extracted_fields,
            rule_hits=rule_hits,
        )

        try:
            content = self._chat_completion(
                system_prompt=self._system_prompt(),
                user_prompt=prompt,
                temperature=0.3,
                max_tokens=2048,
            )
            content = (content or "").strip()
            if not content:
                logger.warning("LLM decision evaluation returned empty content.")
                return None
            return self._parse_json_payload(content)
        except Exception as exc:
            logger.warning("LLM decision evaluation failed, falling back to heuristics: %s", exc)
            return None

    def _system_prompt(self) -> str:
        return (
            "你是资深招投标决策专家。你的任务是根据项目基本信息、前面从长篇标书中提取的详细关键要求（特别是**评分重点**和**必备资质**）以及硬性规则卡口结果，输出多维度的评估打分、决策原因摘要以及待确认事项。\n"
            "你的评估必须真实反映给定的信息。如果评分重点中对技术参数或类似业绩要求极高，你应该在打分和风险提示中体现出来。\n"
            "输出必须是符合以下结构的 JSON 对象，请确保它是一个合法的 JSON，不要带有 markdown 代码块标记：\n"
            "{\n"
            '  "score": {\n'
            '    "total": 85,\n'
            '    "dimensions": [\n'
            '      {"label": "资质与合规", "score": 90, "note": "满足所有硬性资质要求..."},\n'
            '      {"label": "技术能力匹配", "score": 80, "note": "技术规范中的X项可能有偏离风险..."},\n'
            '      {"label": "商业与利润", "score": 85, "note": "预算充足但付款条件一般..."},\n'
            '      {"label": "竞争与环境", "score": 88, "note": "常规项目..."}\n'
            '    ]\n'
            '  },\n'
            '  "ai_reasons": ["资质门槛达标，满足基本要求", "技术评分比重高，需重点准备XX方案", "预算明确，利润空间可见"],\n'
            '  "pending_checks": ["需确认是否满足近期类似业绩要求", "需业务进一步确认付款账期能否接受"]\n'
            "}"
        )

    def _build_prompt(
        self,
        *,
        project_name: str,
        client_name: str,
        extracted_fields: dict[str, str],
        rule_hits: list[dict[str, str]],
    ) -> str:
        fields_str = json.dumps(extracted_fields, ensure_ascii=False, indent=2)
        rules_str = json.dumps(rule_hits, ensure_ascii=False, indent=2)
        
        return (
            f"项目名称：{project_name}\n"
            f"客户名称：{client_name}\n"
            f"从招标文件提取的关键要求详情（核心依据）：\n{fields_str}\n"
            f"硬性规则卡口结果：\n{rules_str}\n\n"
            "请基于以上信息，生成深度且专业的综合评估决策。注意总分应该等于各维度加权或算术平均。ai_reasons 请控制在3-5条内，重点提炼核心赢单点或失单风险。"
        )

llm_review_client = LLMReviewClient()
llm_generation_client = LLMGenerationClient()
llm_decision_client = LLMDecisionClient()
