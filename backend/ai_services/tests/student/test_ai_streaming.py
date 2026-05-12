"""学生端 AI 流式问答服务测试。"""

from types import SimpleNamespace
from unittest.mock import patch

from asgiref.sync import async_to_sync
from channels.testing import WebsocketCommunicator
from django.test import SimpleTestCase

from ai_services.realtime.consumers import StudentAIChatConsumer
from ai_services.services.student.ai_streaming import (
    StudentAIStreamPlan,
    build_generic_stream_plan,
    build_stream_done_payload,
)


class StudentAIStreamingPlanTests(SimpleTestCase):
    """锁定学生端 AI 流式问答协议载荷。"""

    def test_done_payload_should_keep_stream_reply_and_metadata(self):
        """done 事件应保留完整回复、流式标记与 GraphRAG 元数据。"""
        plan = StudentAIStreamPlan(
            prompt="请基于证据回答",
            call_type="graph_rag_answer_stream",
            fallback_reply="fallback",
            metadata={
                "reply": "fallback",
                "sources": [{"title": "图谱证据", "kind": "graph_query"}],
                "mode": "neo4j_graphrag_tools",
                "query_modes": ["local", "graph_tools"],
                "key_points": ["课程A基础"],
                "matched_point": {"point_id": 3, "point_name": "共享知识点"},
            },
        )

        payload = build_stream_done_payload(plan=plan, reply="流式回答", streamed=True)

        self.assertEqual(payload["reply"], "流式回答")
        self.assertTrue(payload["streamed"])
        self.assertEqual(payload["mode"], "neo4j_graphrag_tools")
        self.assertEqual(payload["query_modes"], ["local", "graph_tools"])
        self.assertEqual(payload["key_points"], ["课程A基础"])
        self.assertEqual(payload["matched_point"]["point_id"], 3)

    def test_generic_stream_plan_should_include_fallback_reply(self):
        """无课程图谱证据时仍应产生可展示的降级计划。"""
        plan = build_generic_stream_plan(
            question="如何复习数组？",
            course_id=7,
            knowledge_point="数组基础",
            course_name="数据结构",
        )

        self.assertEqual(plan.call_type, "chat")
        self.assertIn("如何复习数组", plan.fallback_reply)
        self.assertEqual(plan.metadata["mode"], "llm_fallback")
        self.assertEqual(plan.metadata["sources"], [])

    def test_generic_stream_plan_should_include_recent_history_context(self):
        """学习节点抽屉传入的最近对话应进入流式 prompt。"""
        plan = build_generic_stream_plan(
            question="那这个怎么练习？",
            course_id=7,
            knowledge_point="数组基础",
            course_name="数据结构",
            history=[
                {"role": "user", "content": "数组下标为什么从 0 开始？"},
                {"role": "assistant", "content": "它和地址偏移计算有关。"},
            ],
        )

        self.assertIn("# 最近对话", plan.prompt)
        self.assertIn("学生：数组下标为什么从 0 开始？", plan.prompt)
        self.assertIn("助手：它和地址偏移计算有关。", plan.prompt)


class StudentAIStreamingConsumerTests(SimpleTestCase):
    """锁定学生端 AI WebSocket 的事件序列和降级语义。"""

    def _build_plan(self) -> StudentAIStreamPlan:
        """构造可复用的流式计划。"""
        return StudentAIStreamPlan(
            prompt="请回答数组问题",
            call_type="graph_rag_answer_stream",
            fallback_reply="fallback answer",
            metadata={
                "reply": "fallback answer",
                "sources": [{"title": "数组图谱", "kind": "graph_query"}],
                "mode": "neo4j_graphrag_tools",
                "query_modes": ["local", "graph_tools"],
                "key_points": ["数组"],
                "matched_point": {"point_id": 1, "point_name": "数组"},
            },
        )

    @staticmethod
    async def _connect_communicator() -> WebsocketCommunicator:
        """建立带已认证用户的 consumer 测试连接。"""
        communicator = WebsocketCommunicator(
            StudentAIChatConsumer.as_asgi(),
            "/ws/student/ai/chat",
        )
        communicator.scope["user"] = SimpleNamespace(is_authenticated=True)
        connected, _ = await communicator.connect()
        assert connected
        return communicator

    def test_websocket_should_emit_streaming_event_sequence(self):
        """真实流式路径应按 ready/start/stage/chunk/done 推送。"""
        plan = self._build_plan()

        async def run_case():
            communicator = await self._connect_communicator()
            try:
                ready_event = await communicator.receive_json_from()
                with (
                    patch(
                        "ai_services.realtime.consumers.build_student_ai_stream_plan",
                        return_value=plan,
                    ),
                    patch(
                        "ai_services.realtime.consumers.iter_student_ai_stream_chunks",
                        return_value=iter(["第一段", "第二段"]),
                    ),
                ):
                    await communicator.send_json_to(
                        {"question": "数组怎么学", "course_id": 7}
                    )
                    events = [await communicator.receive_json_from() for _ in range(6)]
            finally:
                await communicator.disconnect()
            return ready_event, events

        ready_event, events = async_to_sync(run_case)()

        self.assertEqual(ready_event["type"], "ready")
        self.assertEqual(
            [event["type"] for event in events],
            ["start", "stage", "stage", "chunk", "chunk", "done"],
        )
        self.assertEqual(events[1]["stage"], "retrieval")
        self.assertEqual(events[2]["stage"], "generation")
        self.assertEqual(events[3]["content"], "第一段")
        self.assertEqual(events[4]["content"], "第二段")
        self.assertEqual(events[5]["reply"], "第一段第二段")
        self.assertTrue(events[5]["streamed"])
        self.assertEqual(events[5]["matched_point"]["point_name"], "数组")

    def test_websocket_should_use_compatible_fallback_when_stream_has_no_chunks(self):
        """模型不可用或流式无输出时应复用旧完整回答链路。"""
        plan = self._build_plan()
        fallback_result = {
            "reply": "完整回答",
            "mode": "graph_rag",
            "sources": [{"title": "旧链路证据"}],
            "matched_point": {"point_id": 2, "point_name": "链表"},
            "query_modes": ["local"],
            "key_points": ["链表"],
        }

        async def run_case():
            communicator = await self._connect_communicator()
            try:
                ready_event = await communicator.receive_json_from()
                with (
                    patch(
                        "ai_services.realtime.consumers.build_student_ai_stream_plan",
                        return_value=plan,
                    ),
                    patch(
                        "ai_services.realtime.consumers.iter_student_ai_stream_chunks",
                        return_value=iter([]),
                    ),
                    patch(
                        "ai_services.realtime.consumers.build_chat_response",
                        return_value=fallback_result,
                    ),
                ):
                    await communicator.send_json_to(
                        {"question": "链表怎么学", "course_id": 7}
                    )
                    events = [await communicator.receive_json_from() for _ in range(5)]
            finally:
                await communicator.disconnect()
            return ready_event, events

        ready_event, events = async_to_sync(run_case)()

        self.assertEqual(ready_event["type"], "ready")
        self.assertEqual(
            [event["type"] for event in events],
            ["start", "stage", "stage", "chunk", "done"],
        )
        self.assertEqual(events[3]["content"], "完整回答")
        self.assertEqual(events[4]["reply"], "完整回答")
        self.assertFalse(events[4]["streamed"])
        self.assertEqual(events[4]["matched_point"]["point_name"], "链表")
