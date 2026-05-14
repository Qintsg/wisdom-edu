#!/user/bin/env python
# -*- coding: UTF-8 -*-
"""
LLM 异常详情格式化工具。
@Project : wisdom-edu
@File : error_details.py
@Author : Qintsg
@Date : 2026-05-14
"""

from __future__ import annotations


def summarize_exception_chain(error: BaseException, max_depth: int = 4) -> str:
    """
    汇总异常及其 cause/context 链，避免 OpenAI SDK 的通用错误遮蔽底层原因。

    :param error: 捕获到的异常对象。
    :param max_depth: 最多展开的异常层级。
    :return: 单行异常链摘要。
    """
    if max_depth <= 0:
        return ""

    chain_parts: list[str] = []
    seen_ids: set[int] = set()
    current_error: BaseException | None = error

    while current_error is not None and len(chain_parts) < max_depth:
        current_id = id(current_error)
        if current_id in seen_ids:
            chain_parts.append("<cycle>")
            break
        seen_ids.add(current_id)

        message = str(current_error).strip() or repr(current_error)
        error_type = f"{type(current_error).__module__}.{type(current_error).__name__}"
        chain_parts.append(f"{error_type}: {message}")
        current_error = current_error.__cause__ or current_error.__context__

    return " <- ".join(chain_parts)
