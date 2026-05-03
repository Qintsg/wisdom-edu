"""轻量分页与安全数值解析工具。"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TypeVar


Item = TypeVar("Item")


# 维护意图：安全地将值转换为整数，失败时返回默认值。
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def safe_int(value: object, default: int | None = None) -> int | None:
    """
    安全地将值转换为整数，失败时返回默认值。

    :param value: 待转换值。
    :param default: 转换失败时的返回值。
    :return: 整数或默认值。
    """
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default


# 维护意图：从 QueryDict 或 dict 中解析分页参数。
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def parse_pagination(
    query_params: object,
    size_key: str = "page_size",
    default_size: int = 20,
    max_size: int = 100,
) -> tuple[int, int]:
    """
    从 QueryDict 或 dict 中解析分页参数。

    :param query_params: 请求查询参数。
    :param size_key: 每页大小参数名。
    :param default_size: 默认每页大小。
    :param max_size: 最大每页大小。
    :return: `(page, page_size)`。
    """
    getter = getattr(query_params, "get", None)
    page_value = getter("page", 1) if callable(getter) else 1
    size_value = getter(size_key, default_size) if callable(getter) else default_size
    page = max(1, safe_int(page_value, 1) or 1)
    page_size = safe_int(size_value, default_size) or default_size
    return page, min(max(1, page_size), max_size)


# 维护意图：对列表进行分页。
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def paginate_list(
    items: Sequence[Item], page: int | str = 1, page_size: int | str = 20
) -> tuple[Sequence[Item], int]:
    """
    对列表进行分页。

    :param items: 列表数据。
    :param page: 页码，从 1 开始。
    :param page_size: 每页大小。
    :return: `(paginated_items, total)`。
    """
    parsed_page = max(1, safe_int(page, 1) or 1)
    parsed_size = safe_int(page_size, 20) or 20
    bounded_size = max(1, min(100, parsed_size))
    total = len(items)
    start = (parsed_page - 1) * bounded_size
    end = start + bounded_size
    return items[start:end], total


__all__ = ["safe_int", "parse_pagination", "paginate_list"]
