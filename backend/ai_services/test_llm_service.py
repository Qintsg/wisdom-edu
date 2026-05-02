"""Regression tests for AI-facing student and search services."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch
from uuid import UUID
from random import Random

from django.test import SimpleTestCase, override_settings
from rest_framework.test import APITestCase

from ai_services.services.student_graph_rag_service import student_graph_rag_service
from ai_services.services.web_search_service import (
    SEARCH_PROVIDERS,
    _search_with_provider,
    search_learning_resources,
)
from courses.models import Course
from typing import cast
from types import SimpleNamespace
from knowledge.models import KnowledgePoint, Resource
from platform_ai.mcp import ExternalResourceCandidate, InternalResourceCandidate
from platform_ai.mcp.resources import LearningResourceMCPService
from platform_ai.rag import student_learning_rag
from platform_ai.rag.runtime import (
    COURSE_RETRIEVAL_MODE,
    GraphRAGSearchHit,
    TokenHashEmbedder,
    student_graphrag_runtime,
)
from tools.kt_synthetic import _build_kp_profiles, _simulate_student_sequence
from users.models import User

class LLMProviderConfigTests(SimpleTestCase):
    """Validate multi-provider LLM configuration resolution."""

    @override_settings(
        LLM_PROVIDER="doubao",
        LLM_MODEL="ByteDance-Seed-1.8",
        LLM_API_FORMAT="openai-compatible",
        LLM_BASE_URL="",
        ARK_API_KEY="ark-demo-key",
        DOUBAO_API_KEY="",
        DOUBAO_BASE_URL="https://ark.example.com/api/v3",
    )
    def test_llm_service_should_resolve_explicit_doubao_provider(self):
        """Explicit provider settings should prefer provider-specific keys and URLs."""
        from ai_services.services.llm_service import LLMService

        service = LLMService()

        self.assertEqual(service.provider_name, "doubao")
        self.assertEqual(service.resolved_api_key, "ark-demo-key")
        self.assertEqual(service.resolved_base_url, "https://ark.example.com/api/v3")
        self.assertEqual(service.api_format, "openai-compatible")

    @override_settings(
        LLM_PROVIDER="custom",
        LLM_MODEL="campus-private-chat",
        LLM_API_FORMAT="chat-completions",
        LLM_BASE_URL="",
        LLM_API_KEY="",
        CUSTOM_LLM_API_KEY="custom-demo-key",
        CUSTOM_LLM_BASE_URL="https://llm.example.edu/v1",
    )
    def test_llm_service_should_resolve_custom_gateway_fields(self):
        """Custom provider should use dedicated custom gateway credentials when shared fields are blank."""
        from ai_services.services.llm_service import LLMService

        service = LLMService()

        self.assertEqual(service.provider_name, "custom")
        self.assertEqual(service.resolved_api_key, "custom-demo-key")
        self.assertEqual(service.resolved_base_url, "https://llm.example.edu/v1")
        self.assertEqual(service.api_format, "chat-completions")

    @override_settings(
        LLM_PROVIDER="deepseek",
        LLM_MODEL="deepseek-chat",
        DEEPSEEK_API_KEY="deepseek-demo-key",
        DEEPSEEK_BASE_URL="https://api.deepseek.com",
        LLM_HTTP_PROXY="http://127.0.0.1:8080",
        LLM_HTTPS_PROXY="http://127.0.0.1:8443",
        HTTP_PROXY="http://127.0.0.1:8080",
        HTTPS_PROXY="http://127.0.0.1:8443",
    )
    @patch("ai_services.services.llm_service.import_module")
    def test_llm_service_should_attach_https_proxy_to_chat_client(self, mock_import_module):
        """HTTPS model gateways should use the configured HTTPS proxy when initializing ChatOpenAI."""
        from ai_services.services.llm_service import LLMService

        chat_openai_class = Mock(return_value=Mock())
        mock_import_module.return_value = SimpleNamespace(ChatOpenAI=chat_openai_class)

        service = LLMService()
        service._create_llm_client(request_timeout=12, max_retries=0)

        self.assertEqual(service.resolved_proxy_url, "http://127.0.0.1:8443")
        self.assertEqual(
            chat_openai_class.call_args.kwargs["openai_proxy"],
            "http://127.0.0.1:8443",
        )

    @override_settings(
        LLM_PROVIDER="deepseek",
        LLM_MODEL="deepseek-v4-flash",
        LLM_API_FORMAT="openai-compatible",
        LLM_BASE_URL="",
        DEEPSEEK_API_KEY="deepseek-demo-key",
        DEEPSEEK_BASE_URL="https://api.deepseek.com",
        LLM_REASONING_ENABLED=False,
        LLM_REASONING_EFFORT="",
        LLM_EXTRA_BODY={},
    )
    @patch("ai_services.services.llm_service.import_module")
    def test_llm_service_should_default_deepseek_v4_to_non_thinking_mode(
        self,
        mock_import_module,
    ):
        """DeepSeek v4 default client should send the non-thinking gateway flag."""
        from ai_services.services.llm_service import LLMService

        chat_openai_class = Mock(return_value=Mock())
        mock_import_module.return_value = SimpleNamespace(ChatOpenAI=chat_openai_class)

        service = LLMService()
        service._create_llm_client(request_timeout=12, max_retries=0)

        self.assertEqual(service.provider_name, "deepseek")
        self.assertEqual(service.model_name, "deepseek-v4-flash")
        self.assertEqual(
            chat_openai_class.call_args.kwargs["extra_body"],
            {"enable_thinking": False},
        )
        self.assertNotIn("reasoning_effort", chat_openai_class.call_args.kwargs)

    @override_settings(
        LLM_PROVIDER="deepseek",
        LLM_MODEL="deepseek-v4-flash",
        LLM_API_FORMAT="openai-compatible",
        LLM_BASE_URL="",
        DEEPSEEK_API_KEY="deepseek-demo-key",
        DEEPSEEK_BASE_URL="https://api.deepseek.com",
        LLM_REASONING_ENABLED=False,
        LLM_REASONING_EFFORT="",
        LLM_EXTRA_BODY={},
    )
    @patch("ai_services.services.llm_service.import_module")
    def test_external_resource_recommendation_should_enable_provider_web_search(
        self,
        mock_import_module,
    ):
        """External resource recommendations should use provider-native web search directly."""
        from ai_services.services.llm_service import LLMService

        mock_llm = Mock()
        mock_llm.invoke.return_value = SimpleNamespace(
            content=(
                '{"resources":[{"title":"数组基础教程","url":"https://example.com/array",'
                '"type":"document","reason":"该资源适合数组基础入门学习。"}]}'
            )
        )
        chat_openai_class = Mock(return_value=mock_llm)
        mock_import_module.return_value = SimpleNamespace(ChatOpenAI=chat_openai_class)

        service = LLMService()
        result = service.recommend_external_resources(
            point_name="数组基础",
            student_mastery=0.2,
            course_name="数据结构",
            count=1,
        )

        self.assertEqual(result["resources"][0]["url"], "https://example.com/array")
        self.assertEqual(
            chat_openai_class.call_args.kwargs["extra_body"],
            {"enable_thinking": False, "enable_search": True},
        )

    def test_llm_json_parser_should_ignore_think_blocks(self):
        """Reasoning traces should not prevent structured JSON parsing."""
        from ai_services.services.llm_service import LLMService

        result = LLMService._parse_json_response(
            '<think>内部推理内容</think>{"summary": "最终答案"}'
        )

        self.assertEqual(result["summary"], "最终答案")


class LLMServiceRoutingTests(SimpleTestCase):
    """Guard against recursive agent routing in regular LLM calls."""

    @staticmethod
    def _build_service():
        from ai_services.services.llm_service import LLMService

        service = LLMService()
        service._api_key = "demo-key"
        return service

    def test_call_with_fallback_should_skip_agent_for_profile_analysis(self):
        """Profile analysis should go straight to the LLM client instead of the agent."""
        service = self._build_service()
        mock_llm = Mock()
        mock_llm.invoke.return_value = SimpleNamespace(content='{"summary": "直连LLM结果"}')
        service._get_llm = Mock(return_value=mock_llm)
        service._get_agent_service = Mock(
            return_value=Mock(is_available=True, invoke_json=Mock(return_value={"summary": "agent结果"}))
        )

        result = service.call_with_fallback(
            prompt="请生成画像摘要",
            call_type="profile_analysis",
            fallback_response={"summary": "fallback"},
        )

        service._get_agent_service.assert_not_called()
        mock_llm.invoke.assert_called_once()
        self.assertEqual(result["summary"], "直连LLM结果")

    def test_call_with_fallback_should_only_use_agent_for_explicit_agent_calls(self):
        """Only explicitly agent-scoped call types should enter the orchestration layer."""
        service = self._build_service()
        agent_service = Mock(is_available=True)
        agent_service.invoke_json.return_value = {"summary": "agent结果"}
        service._get_agent_service = Mock(return_value=agent_service)
        service._get_llm = Mock()

        result = service.call_with_fallback(
            prompt="请规划多工具任务",
            call_type="agent_orchestration",
            fallback_response={"summary": "fallback"},
        )

        service._get_agent_service.assert_called_once()
        service._get_llm.assert_not_called()
        self.assertEqual(result["summary"], "agent结果")


class LLMServiceLatencyPolicyTests(SimpleTestCase):
    """Ensure latency-sensitive AI routes fail fast instead of hanging behind the gateway."""

    @staticmethod
    def _build_service():
        from ai_services.services.llm_service import LLMService

        service = LLMService()
        service._api_key = "demo-key"
        return service

    def test_call_with_fallback_should_fast_fail_graph_rag_calls_without_repair(self):
        """GraphRAG answers should use a single attempt and skip JSON repair to stay within gateway budgets."""
        service = self._build_service()
        mock_llm = Mock()
        mock_llm.invoke.return_value = SimpleNamespace(content="这不是 JSON")
        service._get_llm_for_policy = Mock(return_value=mock_llm)
        service._repair_json_response = Mock(return_value={"answer": "修复结果"})

        fallback = {"answer": "fallback answer"}
        oversized_prompt = "图谱证据\n" + ("上下文片段-" * 2000)
        result = service.call_with_fallback(
            prompt=oversized_prompt,
            call_type="graph_rag_answer",
            fallback_response=fallback,
        )

        self.assertEqual(result, fallback)
        self.assertEqual(mock_llm.invoke.call_count, 1)
        service._repair_json_response.assert_not_called()
        messages = mock_llm.invoke.call_args.args[0]
        human_prompt = messages[1].content
        self.assertLessEqual(
            len(human_prompt),
            service._resolve_execution_policy("graph_rag_answer").max_prompt_chars,
        )

    def test_call_with_fallback_should_keep_repair_for_profile_analysis(self):
        """Non-latency-sensitive calls should retain JSON repair to preserve richer AI output."""
        service = self._build_service()
        mock_llm = Mock()
        mock_llm.invoke.return_value = SimpleNamespace(content="这不是 JSON")
        service._get_llm_for_policy = Mock(return_value=mock_llm)
        service._repair_json_response = Mock(return_value={"summary": "修复后的画像"})

        result = service.call_with_fallback(
            prompt="请生成学习画像",
            call_type="profile_analysis",
            fallback_response={"summary": "fallback"},
        )

        service._repair_json_response.assert_called_once()
        self.assertEqual(result["summary"], "修复后的画像")

    def test_chat_policy_should_fast_fail_like_other_interactive_routes(self):
        """Chat fallback should stay inside the gateway-safe timeout budget."""
        service = self._build_service()

        policy = service._resolve_execution_policy("chat")

        self.assertEqual(policy.request_timeout_seconds, service.GATEWAY_SAFE_TIMEOUT_SECONDS)
        self.assertEqual(policy.max_retries, 0)
        self.assertEqual(policy.max_attempts, 1)
        self.assertFalse(policy.allow_repair)


class LangChainAgentProxyTests(SimpleTestCase):
    """Ensure the thin agent wrapper reuses the same proxy settings as LLMService."""

    @override_settings(
        LLM_PROVIDER="deepseek",
        LLM_MODEL="deepseek-chat",
        DEEPSEEK_API_KEY="deepseek-demo-key",
        DEEPSEEK_BASE_URL="https://api.deepseek.com",
        LLM_HTTP_PROXY="http://127.0.0.1:8080",
        LLM_HTTPS_PROXY="http://127.0.0.1:8443",
        HTTP_PROXY="http://127.0.0.1:8080",
        HTTPS_PROXY="http://127.0.0.1:8443",
    )
    @patch("langchain_openai.ChatOpenAI")
    def test_agent_service_should_forward_proxy_to_chat_openai(self, mock_chat_openai):
        """Agent ChatOpenAI client should receive the resolved gateway proxy."""
        from platform_ai.llm.agent import get_default_agent_service

        service = get_default_agent_service()
        service._get_model()

        self.assertEqual(
            mock_chat_openai.call_args.kwargs["openai_proxy"],
            "http://127.0.0.1:8443",
        )

    def test_agent_graphrag_tool_should_call_public_payload_builder(self):
        """GraphRAG tool wiring should not reference the old private helper name."""
        from platform_ai.llm.agent import LangChainAgentService

        service = LangChainAgentService(
            model_name="deepseek-chat",
            api_key="demo-key",
            base_url="https://api.deepseek.com",
        )

        with (
            patch("langchain.tools.tool", side_effect=lambda func: func),
            patch(
                "platform_ai.llm.agent.build_course_graphrag_payload",
                return_value={"mode": "graph_rag", "matched_point_ids": [3]},
            ) as mock_payload_builder,
        ):
            tools = service._get_tools()
            payload = json.loads(tools[1](course_id=7, query="解释先修关系", point_id=3, limit=5))

        self.assertEqual(payload["mode"], "graph_rag")
        mock_payload_builder.assert_called_once_with(
            course_id=7,
            query="解释先修关系",
            point_id=3,
            limit=5,
        )


class FacadeGraphRAGLLMTests(SimpleTestCase):
    """Verify the custom GraphRAG adapter now targets the V2 LLM interface."""

    def test_facade_graphrag_llm_should_instantiate_without_legacy_warning(self):
        """Instantiation should no longer trigger the deprecated LLMInterface warning."""
        from neo4j_graphrag.llm import LLMInterfaceV2
        from platform_ai.rag.runtime import FacadeGraphRAGLLM

        with patch("neo4j_graphrag.llm.base.logger.warning") as mock_warning:
            llm = FacadeGraphRAGLLM()

        self.assertIsInstance(llm, LLMInterfaceV2)
        mock_warning.assert_not_called()

    def test_facade_graphrag_llm_should_accept_v2_message_lists(self):
        """The adapter should support V2-style message arrays in addition to legacy string prompts."""
        from platform_ai.rag.runtime import FacadeGraphRAGLLM

        call_with_fallback = Mock(return_value={"content": "MATCH (n) RETURN n LIMIT 5"})
        mocked_facade = SimpleNamespace(
            is_available=True,
            service=SimpleNamespace(model_name="qwen-plus"),
            call_with_fallback=call_with_fallback,
        )

        with patch("platform_ai.rag.runtime.llm_facade", new=mocked_facade):
            llm = FacadeGraphRAGLLM()
            response = llm.invoke(
                [{"role": "user", "content": "请根据课程图谱生成 Cypher"}],
                response_format={"type": "json_object"},
            )

        self.assertEqual(response.content, "MATCH (n) RETURN n LIMIT 5")
        self.assertEqual(
            call_with_fallback.call_args.kwargs["call_type"],
            "graph_rag_text2cypher",
        )
