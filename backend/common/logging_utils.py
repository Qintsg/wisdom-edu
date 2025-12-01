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


def _humanize_event(event: str) -> str:
    """Translate machine-friendly event codes into readable Chinese labels."""
    parts = [part for part in re.split(r'[._-]+', event or '') if part]
    if not parts:
        return '未命名事件'
    return ''.join(EVENT_TOKEN_MAP.get(part.lower(), part) for part in parts)


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


def log_event(logger: logging.Logger, level: int, event: str, **fields: Any) -> None:
    """Emit a formatted event line through the provided logger instance."""
    logger.log(level, build_log_message(event, **fields))
