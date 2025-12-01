"""学生端 AI 助手 WebSocket consumer。"""

from __future__ import annotations

import asyncio

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from .student_ai_views import build_chat_response


def _split_reply_chunks(reply_text: str, chunk_size: int = 90) -> list[str]:
    """将完整回复拆分为多个小块，便于前端逐步渲染。"""
    if not reply_text:
        return [""]
    return [
        reply_text[index : index + chunk_size]
        for index in range(0, len(reply_text), chunk_size)
    ]


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

        await self.send_json({"type": "start"})
        try:
            result = await database_sync_to_async(build_chat_response)(
                user=self.scope["user"],
                question=question,
                course_id=course_id,
                point_id=point_id,
                knowledge_point=knowledge_point,
                course_name=course_name,
            )

            reply_text = result.get("reply") or ""
            for chunk in _split_reply_chunks(reply_text):
                await self.send_json({"type": "chunk", "content": chunk})
                await asyncio.sleep(0.01)

            await self.send_json(
                {
                    "type": "done",
                    "mode": result.get("mode", "graph_rag"),
                    "sources": result.get("sources", []),
                    "matched_point": result.get("matched_point"),
                }
            )
        except Exception:  # noqa: BLE001
            await self.send_json(
                {"type": "error", "message": "AI 助手暂时无法回复，请稍后重试。"}
            )
