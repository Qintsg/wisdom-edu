#!/user/bin/env python
# -*- coding: UTF-8 -*-
"""
LLM 异常详情测试。
@Project : wisdom-edu
@File : test_error_details.py
@Author : Qintsg
@Date : 2026-05-14
"""

from __future__ import annotations

from django.test import SimpleTestCase

from ai_services.services.llm.error_details import summarize_exception_chain


class LLMErrorDetailsTests(SimpleTestCase):
    """验证 LLM 异常链摘要能保留底层连接失败原因。"""

    def test_summarize_exception_chain_should_include_nested_causes(self) -> None:
        """
        OpenAI SDK 的 Connection error 应展开底层 cause，便于定位网络根因。

        :return: None。
        """
        try:
            try:
                raise OSError("connect timed out")
            except OSError as network_error:
                raise RuntimeError("Connection error.") from network_error
        except RuntimeError as wrapped_error:
            summary = summarize_exception_chain(wrapped_error)

        self.assertIn("builtins.RuntimeError: Connection error.", summary)
        self.assertIn("builtins.OSError: connect timed out", summary)
