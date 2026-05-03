from __future__ import annotations

import json
import logging
import time
from typing import Any, Dict, Optional

from common.logging_utils import build_log_message
from .llm_response_support import (
    build_retry_prompt,
    coerce_message_text,
    format_input_data,
    merge_missing_fields,
    parse_json_response,
    post_process_response,
    strip_reasoning_blocks,
)

logger = logging.getLogger(__name__)


# 维护意图：结构化 LLM 调用、JSON 修复与结果清洗能力
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
class LLMResponseMixin:
    """结构化 LLM 调用、JSON 修复与结果清洗能力。"""

    _SYSTEM_CONTENT = """You are the AI analysis engine for an adaptive learning system.

# Output rules
1. Output valid JSON only.
2. The response must be directly parseable by json.loads().
3. Use natural language descriptions instead of internal IDs.
4. Keep recommendations concrete, complete, and actionable.
5. If information is limited, still return the full JSON structure with the best available content."""

    _format_input_data = staticmethod(format_input_data)
    _strip_reasoning_blocks = staticmethod(strip_reasoning_blocks)
    _parse_json_response = staticmethod(parse_json_response)
    _coerce_message_text = staticmethod(coerce_message_text)

    # 维护意图：要求模型将原始内容修复为可直接解析的合法 JSON
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
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

    # 维护意图：恢复调用前的温度配置
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    @staticmethod
    def _restore_temperature(llm: Any, original_temperature: float | None) -> None:
        """恢复调用前的温度配置。"""
        if original_temperature is not None:
            llm.temperature = original_temperature

    # 维护意图：临时覆盖模型温度，并返回原始值
    # 边界说明：写入边界集中在这里，便于控制事务、审计和失败语义。
    # 风险说明：改动副作用、事务或审计字段时，需同步调用方和回归测试。
    @staticmethod
    def _apply_temperature_override(llm: Any, temperature: float | None) -> float | None:
        """临时覆盖模型温度，并返回原始值。"""
        if temperature is None or not hasattr(llm, "temperature"):
            return None
        original_temperature = llm.temperature
        llm.temperature = temperature
        return original_temperature

    _build_retry_prompt = staticmethod(build_retry_prompt)

    # 维护意图：统一补齐缺失字段并执行轻量清洗
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def _finalize_success_response(
        self,
        result: Dict[str, Any],
        fallback_response: Dict[str, Any],
        call_type: str,
    ) -> Dict[str, Any]:
        """统一补齐缺失字段并执行轻量清洗。"""
        merged_result = self._merge_missing_fields(result, fallback_response)
        return self._post_process_response(merged_result, call_type)

    # 维护意图：尝试通过 Agent 服务完成结构化 JSON 调用
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
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

    # 维护意图：执行一次 LangChain 消息调用，并提取规范化后的文本内容
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
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

    # 维护意图：解析当前输出，必要时再尝试一次 JSON 修复
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
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

    # 维护意图：执行直接 LLM 调用、重试和 JSON 修复流程
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
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

    _merge_missing_fields = staticmethod(merge_missing_fields)

    # 维护意图：解析执行策略并截断 prompt
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def _prepare_structured_call(self, prompt: str, call_type: str) -> tuple[float, Any, str]:
        """解析执行策略并截断 prompt。"""
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
        return start_time, execution_policy, prepared_prompt

    # 维护意图：按调用类型尝试 Agent JSON 通道
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def _try_agent_structured_call(
        self,
        *,
        call_type: str,
        prepared_prompt: str,
        fallback_response: Dict[str, Any],
        start_time: float,
    ) -> Dict[str, Any] | None:
        """按调用类型尝试 Agent JSON 通道。"""
        agent_service = (
            self._get_agent_service()
            if self._should_use_agent_service(call_type)
            else None
        )
        if agent_service and agent_service.is_available:
            return self._run_agent_json_call(
                agent_service=agent_service,
                call_type=call_type,
                prepared_prompt=prepared_prompt,
                fallback_response=fallback_response,
                start_time=start_time,
            )
        if self.is_available:
            logger.debug(
                build_log_message(
                    "llm.agent.skipped",
                    call_type=call_type,
                    reason="non_agent_call_type",
                )
            )
        return None

    # 维护意图：执行模型 JSON 调用，并确保临时温度被恢复
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    def _run_model_structured_call(
        self,
        *,
        llm: Any,
        prepared_prompt: str,
        call_type: str,
        fallback_response: Dict[str, Any],
        execution_policy: Any,
        start_time: float,
        temperature: float | None,
    ) -> Dict[str, Any]:
        """执行模型 JSON 调用，并确保临时温度被恢复。"""
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

    # 维护意图：调用 LLM，并在所有结构化输出尝试都失败后才降级
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
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
        start_time, execution_policy, prepared_prompt = self._prepare_structured_call(
            prompt,
            call_type,
        )
        agent_result = self._try_agent_structured_call(
            call_type=call_type,
            prepared_prompt=prepared_prompt,
            fallback_response=fallback_response,
            start_time=start_time,
        )
        if agent_result is not None:
            return agent_result

        llm = self._get_llm_for_policy(execution_policy, extra_body_overrides)
        if llm is None:
            logger.debug(
                build_log_message(
                    "llm.call.fallback", call_type=call_type, reason="model_unavailable"
                )
            )
            return fallback_response

        try:
            return self._run_model_structured_call(
                llm=llm,
                prepared_prompt=prepared_prompt,
                call_type=call_type,
                fallback_response=fallback_response,
                execution_policy=execution_policy,
                start_time=start_time,
                temperature=temperature,
            )
        except Exception as e:
            logger.error(
                build_log_message(
                    "llm.call.fail", call_type=call_type, model=self.model_name, error=e
                )
            )
            return fallback_response

    # 维护意图：通过公共入口执行带降级保护的 LLM 调用
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
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

    _post_process_response = staticmethod(post_process_response)
