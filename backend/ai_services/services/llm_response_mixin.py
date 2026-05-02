from __future__ import annotations

import json
import logging
import re
import time
from typing import Any, Dict, List, Optional

from common.logging_utils import build_log_message

logger = logging.getLogger(__name__)


class LLMResponseMixin:
    """结构化 LLM 调用、JSON 修复与结果清洗能力。"""

    _SYSTEM_CONTENT = """You are the AI analysis engine for an adaptive learning system.

# Output rules
1. Output valid JSON only.
2. The response must be directly parseable by json.loads().
3. Use natural language descriptions instead of internal IDs.
4. Keep recommendations concrete, complete, and actionable.
5. If information is limited, still return the full JSON structure with the best available content."""

    @staticmethod
    def _format_input_data(
        data: Dict[str, Any], data_type: str = "general"
    ) -> str:
        """
        格式化输入数据为结构化文本

        Args:
            data: 输入数据字典
            data_type: 数据类型（用于选择格式化策略）

        Returns:
            格式化后的文本
        """
        if not data:
            return "无数据"

        if isinstance(data, dict):
            formatted_lines = []
            for key, value in data.items():
                if isinstance(value, (list, dict)):
                    formatted_lines.append(
                        f"- {key}: {json.dumps(value, ensure_ascii=False)}"
                    )
                else:
                    formatted_lines.append(f"- {key}: {value}")
            return "\n".join(formatted_lines)

        return str(data)

    @staticmethod
    def _strip_reasoning_blocks(content: str) -> str:
        """移除兼容网关可能返回的 <think> 推理片段，保留最终答案。"""
        if not content:
            return ""
        return re.sub(
            r"<think>[\s\S]*?</think>",
            "",
            str(content),
            flags=re.IGNORECASE,
        ).strip()

    @staticmethod
    def _parse_json_response(content: str) -> Dict[str, Any]:
        """
        安全解析LLM返回的JSON响应

        处理各种可能的格式问题：
        1. 纯JSON
        2. 带有markdown代码块的JSON
        3. 带有额外文本的JSON

        Args:
            content: LLM返回的原始内容

        Returns:
            解析后的字典
        """
        content = LLMResponseMixin._strip_reasoning_blocks(content)

        # 尝试直接解析
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass

        # 尝试从markdown代码块中提取JSON
        json_pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
        matches = re.findall(json_pattern, content)
        for match in matches:
            try:
                return json.loads(match.strip())
            except json.JSONDecodeError:
                continue

        # 尝试查找JSON对象
        try:
            start = content.find("{")
            end = content.rfind("}") + 1
            if start != -1 and end > start:
                return json.loads(content[start:end])
        except json.JSONDecodeError:
            pass

        # 无法解析时保留原始内容，便于后续降级或修复。
        return {"content": content, "parse_error": True}

    @staticmethod
    def _coerce_message_text(content: str | List[Any] | None) -> str:
        """Normalize LangChain message content into a single text string."""
        if isinstance(content, str):
            return LLMResponseMixin._strip_reasoning_blocks(content)
        if isinstance(content, list):
            message_text = "\n".join(
                item if isinstance(item, str) else json.dumps(item, ensure_ascii=False)
                for item in content
                if item is not None
            )
            return LLMResponseMixin._strip_reasoning_blocks(message_text)
        return ""

    def _repair_json_response(
        self, llm, raw_content: str, fallback_response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """要求模型将原始内容修复为可直接解析的合法 JSON。"""
        from langchain_core.messages import HumanMessage, SystemMessage

        schema_hint = json.dumps(fallback_response, ensure_ascii=False)
        repair_prompt = (
            "Please rewrite the following content as complete, valid JSON that can be parsed "
            "directly by json.loads(). Do not add explanations and do not omit any existing information.\n\n"
            f"Target schema example: {schema_hint}\n\n"
            f"Original content:\n{raw_content}"
        )
        repaired = llm.invoke(
            [
                SystemMessage(
                    content="You are a JSON repair assistant. Output valid JSON only."
                ),
                HumanMessage(content=repair_prompt),
            ]
        )
        return self._parse_json_response(self._coerce_message_text(repaired.content))

    @staticmethod
    def _restore_temperature(llm: Any, original_temperature: float | None) -> None:
        """恢复调用前的温度配置。"""
        if original_temperature is not None:
            llm.temperature = original_temperature

    @staticmethod
    def _apply_temperature_override(llm: Any, temperature: float | None) -> float | None:
        """临时覆盖模型温度，并返回原始值。"""
        if temperature is None or not hasattr(llm, "temperature"):
            return None
        original_temperature = llm.temperature
        llm.temperature = temperature
        return original_temperature

    @staticmethod
    def _build_retry_prompt(prepared_prompt: str, attempt_index: int) -> str:
        """为后续重试补充更明确的 JSON 约束提示。"""
        if attempt_index != 1:
            return prepared_prompt
        return (
            prepared_prompt
            + "\n\nPlease output the complete JSON again. Ensure all fields are present and no content is omitted."
        )

    def _finalize_success_response(
        self,
        result: Dict[str, Any],
        fallback_response: Dict[str, Any],
        call_type: str,
    ) -> Dict[str, Any]:
        """统一补齐缺失字段并执行轻量清洗。"""
        merged_result = self._merge_missing_fields(result, fallback_response)
        return self._post_process_response(merged_result, call_type)

    def _run_agent_json_call(
        self,
        *,
        agent_service: Any,
        call_type: str,
        prepared_prompt: str,
        fallback_response: Dict[str, Any],
        start_time: float,
    ) -> Dict[str, Any] | None:
        """尝试通过 Agent 服务完成结构化 JSON 调用。"""
        if not agent_service or not agent_service.is_available:
            return None

        agent_result = agent_service.invoke_json(
            call_type=call_type,
            prompt=prepared_prompt,
            fallback_response=fallback_response,
        )
        if not agent_result or agent_result == fallback_response:
            return None

        duration_ms = int((time.time() - start_time) * 1000)
        logger.debug(
            build_log_message(
                "llm.agent.success",
                call_type=call_type,
                duration_ms=duration_ms,
                model=self.model_name,
            )
        )
        return self._finalize_success_response(
            agent_result,
            fallback_response,
            call_type,
        )

    def _invoke_llm_messages(self, llm: Any, prompt: str) -> str:
        """执行一次 LangChain 消息调用，并提取规范化后的文本内容。"""
        from langchain_core.messages import HumanMessage, SystemMessage

        response = llm.invoke(
            [
                SystemMessage(content=self._SYSTEM_CONTENT),
                HumanMessage(content=prompt),
            ]
        )
        return self._coerce_message_text(response.content)

    def _attempt_llm_json_response(
        self,
        *,
        llm: Any,
        raw_content: str,
        fallback_response: Dict[str, Any],
        execution_policy: Any,
    ) -> tuple[Dict[str, Any] | None, bool]:
        """解析当前输出，必要时再尝试一次 JSON 修复。"""
        parsed_result = self._parse_json_response(raw_content)
        if not parsed_result.get("parse_error"):
            return parsed_result, False
        if not execution_policy.allow_repair:
            return None, False

        repaired_result = self._repair_json_response(
            llm,
            raw_content,
            fallback_response,
        )
        if repaired_result.get("parse_error"):
            return None, False
        return repaired_result, True

    def _run_llm_json_call(
        self,
        *,
        llm: Any,
        prepared_prompt: str,
        call_type: str,
        fallback_response: Dict[str, Any],
        execution_policy: Any,
        start_time: float,
    ) -> Dict[str, Any]:
        """执行直接 LLM 调用、重试和 JSON 修复流程。"""
        last_raw_content = ""
        for attempt_index in range(execution_policy.max_attempts):
            current_prompt = self._build_retry_prompt(prepared_prompt, attempt_index)
            last_raw_content = self._invoke_llm_messages(llm, current_prompt)
            result, repaired = self._attempt_llm_json_response(
                llm=llm,
                raw_content=last_raw_content,
                fallback_response=fallback_response,
                execution_policy=execution_policy,
            )
            if result is None:
                continue

            duration_ms = int((time.time() - start_time) * 1000)
            log_event = "llm.call.repaired" if repaired else "llm.call.success"
            logger.debug(
                build_log_message(
                    log_event,
                    call_type=call_type,
                    attempt=attempt_index + 1,
                    duration_ms=duration_ms,
                    model=self.model_name,
                )
            )
            return self._finalize_success_response(
                result,
                fallback_response,
                call_type,
            )

        logger.warning(
            build_log_message(
                "llm.call.parse_fail",
                call_type=call_type,
                raw=last_raw_content[:300],
            )
        )
        return fallback_response

    @staticmethod
    def _merge_missing_fields(
        result: Dict[str, Any], fallback_response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """仅补齐缺失的顶层字段，不覆盖模型已经生成的内容。"""
        merged = dict(result)
        for key, value in (fallback_response or {}).items():
            if key not in merged or merged[key] is None:
                merged[key] = value
        return merged

    def _call_with_fallback(
        self,
        prompt: str,
        call_type: str,
        fallback_response: Dict[str, Any],
        temperature: float = None,
        extra_body_overrides: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        调用 LLM，并在所有结构化输出尝试都失败后才降级。
        """
        start_time = time.time()
        execution_policy = self._resolve_execution_policy(call_type)
        prepared_prompt = self._truncate_prompt(
            prompt,
            execution_policy.max_prompt_chars,
        )
        if len(prepared_prompt) != len(str(prompt or "").strip()):
            logger.info(
                build_log_message(
                    "llm.prompt.truncated",
                    call_type=call_type,
                    original_chars=len(str(prompt or "")),
                    kept_chars=len(prepared_prompt),
                )
            )

        agent_service = (
            self._get_agent_service()
            if self._should_use_agent_service(call_type)
            else None
        )
        if agent_service and agent_service.is_available:
            agent_result = self._run_agent_json_call(
                agent_service=agent_service,
                call_type=call_type,
                prepared_prompt=prepared_prompt,
                fallback_response=fallback_response,
                start_time=start_time,
            )
            if agent_result is not None:
                return agent_result
        elif self.is_available:
            logger.debug(
                build_log_message(
                    "llm.agent.skipped",
                    call_type=call_type,
                    reason="non_agent_call_type",
                )
            )

        llm = self._get_llm_for_policy(execution_policy, extra_body_overrides)
        if llm is None:
            # 写入日志记录
            logger.debug(
                build_log_message(
                    "llm.call.fallback", call_type=call_type, reason="model_unavailable"
                )
            )
            return fallback_response

        try:
            original_temp = self._apply_temperature_override(llm, temperature)
            try:
                return self._run_llm_json_call(
                    llm=llm,
                    prepared_prompt=prepared_prompt,
                    call_type=call_type,
                    fallback_response=fallback_response,
                    execution_policy=execution_policy,
                    start_time=start_time,
                )
            finally:
                self._restore_temperature(llm, original_temp)
        except Exception as e:
            # 写入日志记录
            logger.error(
                build_log_message(
                    "llm.call.fail", call_type=call_type, model=self.model_name, error=e
                )
            )
            return fallback_response

    def call_with_fallback(
        self,
        prompt: str,
        call_type: str,
        fallback_response: Dict[str, Any],
        temperature: float = None,
        extra_body_overrides: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """通过公共入口执行带降级保护的 LLM 调用。"""
        return self._call_with_fallback(
            prompt=prompt,
            call_type=call_type,
            fallback_response=fallback_response,
            temperature=temperature,
            extra_body_overrides=extra_body_overrides,
        )

    _FIELD_MAX_LEN = {}

    @staticmethod
    def _post_process_response(
        result: Dict[str, Any], call_type: str
    ) -> Dict[str, Any]:
        """Light cleanup only; do not truncate model content."""
        _ = call_type
        cleaned = {}
        for key, value in (result or {}).items():
            if isinstance(value, str):
                cleaned[key] = value.strip()
            elif isinstance(value, list):
                normalized_list = []
                for item in value:
                    if isinstance(item, str):
                        item = item.strip()
                        if item:
                            normalized_list.append(item)
                    elif item is not None:
                        normalized_list.append(item)
                cleaned[key] = normalized_list
            else:
                cleaned[key] = value
        return cleaned
