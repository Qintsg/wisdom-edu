"""管理员接口共享辅助函数。"""

import codecs
from collections.abc import Mapping


UTF8_BOM = codecs.BOM_UTF8.decode('utf-8')


def _parse_pagination(
    query_params: Mapping[str, str],
    size_key: str = 'page_size',
    default_size: int = 20,
    max_size: int = 100,
) -> tuple[int, int]:
    """统一解析分页参数并兜底非法输入。"""
    try:
        page = max(1, int(query_params.get('page', 1)))
        page_size = min(max(1, int(query_params.get(size_key, default_size))), max_size)
    except (ValueError, TypeError):
        page = 1
        page_size = default_size
    return page, page_size
