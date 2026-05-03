"""
日志格式化工具。

用于统一服务层和基础设施层的事件日志输出风格。
"""
from __future__ import annotations

import json
import logging
import re
from typing import Any


EVENT_TOKEN_MAP = {
    'ai': 'AI',
    'analysis': '分析',
    'answer': '答案',
    'assessment': '测评',
    'auth': '认证',
    'batch': '批量',
    'browser': '浏览器',
    'call': '调用',
    'chat': '对话',
    'compare': '对比',
    'complete': '完成',
    'config': '配置',
    'course': '课程',
    'dashboard': '看板',
    'detected': '识别',
    'error': '错误',
    'exam': '考试',
    'external': '外部',
    'fail': '失败',
    'feedback': '反馈',
    'generate': '生成',
    'history': '历史',
    'internal': '内部',
    'kt': 'KT',
    'learning': '学习',
    'llm': 'LLM',
    'load': '加载',
    'mastery': '掌握度',
    'node': '节点',
    'path': '路径',
    'predict': '预测',
    'profile': '画像',
    'provider': '提供方',
    'ready': '就绪',
    'reason': '理由',
    'refresh': '刷新',
    'report': '报告',
    'resource': '资源',
    'result': '结果',
    'save': '保存',
    'search': '检索',
    'service': '服务',
    'stage': '阶段',
    'submit': '提交',
    'success': '成功',
    'sync': '同步',
    'test': '测试',
    'update': '更新',
    'warning': '告警',
}

FIELD_LABEL_MAP = {
    'answer_count': '作答数',
    'attempt': '尝试次数',
    'base_url': '基础地址',
    'class_id': '班级ID',
    'confidence': '置信度',
    'course_id': '课程ID',
    'detail': '详情',
    'duration_ms': '耗时毫秒',
    'error': '错误',
    'exam_id': '考试ID',
    'history_count': '历史数',
    'knowledge_point_id': '知识点ID',
    'model': '模型',
    'module': '模块',
    'node_id': '节点ID',
    'page': '页面',
    'prediction_count': '预测数',
    'provider': '提供方',
    'question_id': '题目ID',
    'report_id': '报告ID',
    'resource_id': '资源ID',
    'result_count': '结果数',
    'route': '路由',
    'score': '得分',
    'source': '来源',
    'status': '状态',
    'student_id': '学生ID',
    'submission_id': '提交ID',
    'teacher_id': '教师ID',
    'total_count': '总数',
    'url': '地址',
    'user_id': '用户ID',
}


# 维护意图：Convert structured field values into compact single-line log fragments
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def _normalize_log_value(value: Any, max_len: int = 240) -> str:
    """Convert structured field values into compact single-line log fragments."""
    if isinstance(value, (dict, list, tuple, set)):
        text = json.dumps(value, ensure_ascii=False)
    else:
        text = str(value)
    text = re.sub(r'\s+', ' ', text).strip()
    if len(text) > max_len:
        return f"{text[:max_len]}[截断]"
    return text


# 维护意图：Translate machine-friendly event codes into readable Chinese labels
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _humanize_event(event: str) -> str:
    """Translate machine-friendly event codes into readable Chinese labels."""
    parts = [part for part in re.split(r'[._-]+', event or '') if part]
    if not parts:
        return '未命名事件'
    return ''.join(EVENT_TOKEN_MAP.get(part.lower(), part) for part in parts)


# 维护意图：Build a consistent key-value log line for service and infra events
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_log_message(event: str, **fields: Any) -> str:
    """Build a consistent key-value log line for service and infra events."""
    parts = [f"事件={_humanize_event(event)}", f"事件码={event}"]
    for key, value in fields.items():
        if value is None or value == '':
            continue
        # Preserve raw field keys as a fallback so new call sites stay debuggable.
        label = FIELD_LABEL_MAP.get(key, key)
        parts.append(f"{label}={_normalize_log_value(value)}")
    return " | ".join(parts)


# 维护意图：Emit a formatted event line through the provided logger instance
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def log_event(logger: logging.Logger, level: int, event: str, **fields: Any) -> None:
    """Emit a formatted event line through the provided logger instance."""
    logger.log(level, build_log_message(event, **fields))
