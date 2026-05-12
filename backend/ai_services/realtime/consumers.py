"""学生端 AI 助手 WebSocket consumer。"""

from __future__ import annotations

import asyncio
import logging

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from common.core.logging_utils import build_log_message
from ai_services.services.student.ai_streaming import (
    build_stream_done_payload,
    build_student_ai_stream_plan,
    iter_student_ai_stream_chunks,
)
from ai_services.api.student.chat import build_chat_response

logger = logging.getLogger(__name__)
_STREAM_END = object()


def _split_reply_chunks(reply_text: str, chunk_size: int = 90) -> list[str]:
    """将完整回复拆分为多个小块，便于前端逐步渲染。"""
    if not reply_text:
        return [""]
    return [
        reply_text[index : index + chunk_size]
        for index in range(0, len(reply_text), chunk_size)
    ]


def _next_stream_chunk(chunk_iterator):
    """读取下一个同步流式块，供异步 consumer 放入线程执行。"""
    return next(chunk_iterator, _STREAM_END)


class StudentAIChatConsumer(AsyncJsonWebsocketConsumer):
    """通过 WebSocket 向学生端输出 AI 助手回答。"""

    async def connect(self):
        """校验登录态并建立学生端聊天连接。"""
        user = self.scope.get("user")
        if not user or not getattr(user, "is_authenticated", False):
            await self.close(code=4401)
            return
        await self.accept()
        await self.send_json({"type": "ready"})

    async def receive_json(self, content, **kwargs):
        """处理学生端发来的问题并按块推送 AI 回复。"""
        question = str(content.get("question") or content.get("message") or "").strip()
        if not question:
            await self.send_json({"type": "error", "message": "请输入问题"})
            return

        course_id = content.get("course_id")
        point_id = content.get("point_id")
        knowledge_point = str(content.get("knowledge_point") or "").strip()
        course_name = str(content.get("course_name") or "").strip()
        history = content.get("history")
        history_items = history if isinstance(history, list) else []

        await self.send_json({"type": "start"})
        await self.send_json({"type": "stage", "stage": "retrieval", "message": "正在检索课程图谱证据"})
        try:
            plan = await database_sync_to_async(build_student_ai_stream_plan)(
                user=self.scope["user"],
                question=question,
                course_id=course_id,
                point_id=point_id,
                knowledge_point=knowledge_point,
                course_name=course_name,
                history=history_items,
            )
        except Exception as error:  # noqa: BLE001
            logger.error(build_log_message("student_ai.stream.plan_fail", error=error))
            await self._send_compatible_fallback(
                question=question,
                course_id=course_id,
                point_id=point_id,
                knowledge_point=knowledge_point,
                course_name=course_name,
            )
            return

        await self.send_json({"type": "stage", "stage": "generation", "message": "正在生成流式回答"})
        reply_parts: list[str] = []
        streamed = False
        try:
            chunk_iterator = iter_student_ai_stream_chunks(plan)
            while True:
                chunk = await asyncio.to_thread(_next_stream_chunk, chunk_iterator)
                if chunk is _STREAM_END:
                    break
                chunk_text = str(chunk)
                if not chunk_text:
                    continue
                streamed = True
                reply_parts.append(chunk_text)
                await self.send_json({"type": "chunk", "content": chunk_text})

            if not reply_parts:
                await self._send_compatible_fallback(
                    question=question,
                    course_id=course_id,
                    point_id=point_id,
                    knowledge_point=knowledge_point,
                    course_name=course_name,
                )
                return

            done_payload = build_stream_done_payload(
                plan=plan,
                reply="".join(reply_parts),
                streamed=streamed,
            )
            await self.send_json({"type": "done", **done_payload})
        except Exception:  # noqa: BLE001
            await self._send_compatible_fallback(
                question=question,
                course_id=course_id,
                point_id=point_id,
                knowledge_point=knowledge_point,
                course_name=course_name,
            )

    async def _send_compatible_fallback(
        self,
        *,
        question: str,
        course_id,
        point_id,
        knowledge_point: str,
        course_name: str,
    ) -> None:
        """流式链路失败时复用原完整回答链路并继续按块推送。"""
        try:
            result = await database_sync_to_async(build_chat_response)(
                user=self.scope["user"],
                question=question,
                course_id=course_id,
                point_id=point_id,
                knowledge_point=knowledge_point,
                course_name=course_name,
            )
            reply_text = str(result.get("reply") or "")
            for chunk in _split_reply_chunks(reply_text):
                await self.send_json({"type": "chunk", "content": chunk})
                await asyncio.sleep(0.01)
            await self.send_json(
                {
                    "type": "done",
                    "reply": reply_text,
                    "streamed": False,
                    "mode": result.get("mode", "graph_rag"),
                    "sources": result.get("sources", []),
                    "matched_point": result.get("matched_point"),
                    "query_modes": result.get("query_modes", []),
                    "key_points": result.get("key_points", []),
                }
            )
        except Exception as error:  # noqa: BLE001
            logger.error(build_log_message("student_ai.stream.fallback_fail", error=error))
            await self.send_json({"type": "error", "message": "AI 助手暂时无法回复，请稍后重试。"})
