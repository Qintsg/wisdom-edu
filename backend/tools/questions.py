#!/user/bin/env python
# -*- coding: UTF-8 -*-
"""
题库导入模块。
支持 JSON 和 Excel 格式的题库导入，包含 NaN 清理、HTML 标签去除和知识点自动绑定。
@Project : wisdom-edu
@File : questions.py
@Author : Qintsg
@Date : 2026-03-23
"""

import re
from html import unescape as html_unescape
from typing import Optional

from django.db import transaction
from django.utils.html import strip_tags

from knowledge.models import KnowledgePoint
from assessments.models import Question
from courses.models import Course

from tools.common import (
    resolve_path,
    load_json,
    get_course,
    clean_nan,
    safe_float,
    split_multi_values,
)
from tools.knowledge import validate_json
from tools.testing import _status_flag


def _strip_html(value):
    """
    去除 HTML 标签并清理多余空白。
    :param value: 原始文本。
    :return: 清洗后的文本。
    """
    if not value:
        return value
    text = str(value)
    text = strip_tags(text)
    text = html_unescape(text)
    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _strip_html_answer(answer):
    """
    清洗答案字段中的 HTML。
    :param answer: 原始答案对象。
    :return: 清洗后的答案对象。
    """
    if isinstance(answer, str):
        return _strip_html(answer)
    if isinstance(answer, dict):
        return {
            k: (
                _strip_html(v)
                if isinstance(v, str)
                else [_strip_html(x) if isinstance(x, str) else x for x in v]
                if isinstance(v, list)
                else v
            )
            for k, v in answer.items()
        }
    return answer


# 题型映射
TYPE_MAP = {
    "单选题": "single_choice",
    "单选": "single_choice",
    "多选题": "multiple_choice",
    "多选": "multiple_choice",
    "判断题": "true_false",
    "判断": "true_false",
    "填空题": "fill_blank",
    "填空": "fill_blank",
    "简答题": "short_answer",
    "简答": "short_answer",
    "编程题": "code",
    "编程": "code",
}

# 难度映射
DIFFICULTY_MAP = {
    "易": "easy",
    "简单": "easy",
    "中": "medium",
    "中等": "medium",
    "难": "hard",
    "困难": "hard",
}


def _extract_question_content(row, columns: list[str]) -> str:
    """
    从 Excel 行数据中提取题干文本。
    :param row: pandas 行对象。
    :param columns: 当前 sheet 的列名列表。
    :return: 清洗后的题干文本。
    """
    if "大题题干" in columns:
        return clean_nan(row.get("小题题干")) or clean_nan(row.get("大题题干")) or ""
    if "题干" in columns:
        return clean_nan(row.get("题干") or "")
    for column_name in columns:
        if any(keyword in str(column_name) for keyword in ["题目", "content", "内容"]):
            return clean_nan(row.get(column_name) or "")
    return ""


def _clean_question_options(raw_options) -> list:
    """
    清洗 JSON 题目中的选项内容。
    :param raw_options: 原始选项列表。
    :return: 清洗后的选项列表。
    """
    cleaned_options = []
    for option in raw_options or []:
        if isinstance(option, dict):
            option = {
                key: (_strip_html(value) if isinstance(value, str) else value)
                for key, value in option.items()
            }
        elif isinstance(option, str):
            option = _strip_html(option)
        cleaned_options.append(option)
    return cleaned_options


def _link_question_knowledge_points(
    question,
    knowledge_point_names,
    kp_map: dict,
    all_kps: list,
    unmatched_names: set[str],
) -> bool:
    """
    按知识点名称为题目绑定知识点。
    :param question: 题目对象。
    :param knowledge_point_names: 待绑定的知识点名称列表。
    :param kp_map: 知识点名称映射。
    :param all_kps: 当前课程全部知识点列表。
    :param unmatched_names: 未匹配知识点名称集合。
    :return: 是否至少绑定了一个知识点。
    """
    linked = False
    for knowledge_point_name in knowledge_point_names:
        kp = kp_map.get(knowledge_point_name)
        if not kp:
            kp = _match_kp_by_topic(knowledge_point_name, all_kps)
        if kp:
            question.knowledge_points.add(kp)
            linked = True
        else:
            unmatched_names.add(knowledge_point_name)
    return linked


def import_questions_json(
    file: str, course_id: int, replace: bool = False, dry_run: bool = False
):
    """
    导入 JSON 格式题库。
    :param file: JSON 文件路径。
    :param course_id: 课程 ID。
    :param replace: 是否先清空课程题目。
    :param dry_run: 是否仅预览导入动作。
    :return: None。
    """
    validate_json(file, "questions")
    data = load_json(file)
    course = get_course(course_id)
    questions = data.get("questions", [])

    if not questions:
        print("未找到questions，跳过导入。")
        return

    if dry_run:
        print(
            f"[DRY-RUN] 将导入题库JSON: 课程={course.name}, "
            f"题目={len(questions)}, replace={replace}"
        )
        return

    kp_map = {p.name: p for p in KnowledgePoint.objects.filter(course=course)}
    all_kps = list(kp_map.values())
    created = 0
    kp_linked = 0
    kp_unmatched = set()

    with transaction.atomic():
        if replace:
            Question.objects.filter(course=course).delete()

        for q in questions:
            content = _strip_html(clean_nan(q.get("content", "")))
            if not content:
                continue

            if (
                not replace
                and Question.objects.filter(course=course, content=content).exists()
            ):
                continue

            cleaned_options = _clean_question_options(q.get("options") or [])

            obj = Question.objects.create(
                course=course,
                content=content,
                question_type=q.get("question_type") or "single_choice",
                options=cleaned_options,
                answer=_strip_html_answer(q.get("answer") or {}),
                analysis=_strip_html(clean_nan(q.get("analysis", ""))),
                difficulty=q.get("difficulty") or "medium",
                score=safe_float(q.get("score"), 1.0),
                chapter=clean_nan(q.get("chapter", "")),
                for_initial_assessment=bool(q.get("for_initial_assessment", False)),
                is_visible=bool(q.get("is_visible", True)),
            )

            linked = _link_question_knowledge_points(
                obj,
                q.get("knowledge_points", []),
                kp_map,
                all_kps,
                kp_unmatched,
            )
            if linked:
                kp_linked += 1
            created += 1

    result = f"题库JSON导入完成: 课程={course.name}, 新增题目={created}"
    if kp_linked:
        result += f", {kp_linked} 题已关联知识点"
    if kp_unmatched:
        result += f"\n  {_status_flag(False)} 未匹配的知识点: {', '.join(sorted(kp_unmatched))}"
    print(result)


def _match_kp_by_topic(topic: str, kp_list: list) -> Optional["KnowledgePoint"]:
    """
    尝试将一个话题名称匹配到知识点列表中的某个知识点。
    :param topic: 待匹配的话题名称。
    :param kp_list: 候选知识点列表。
    :return: 匹配到的知识点对象，未命中时返回 None。
    """
    if not topic or not kp_list:
        return None
    topic_lower = topic.lower().strip()
    for kp in kp_list:
        if kp.name.strip() == topic.strip():
            return kp
    best = None
    best_len = 0
    for kp in kp_list:
        name_lower = kp.name.lower().strip()
        if topic_lower in name_lower or name_lower in topic_lower:
            if len(kp.name) > best_len:
                best = kp
                best_len = len(kp.name)
    return best


def import_question_bank(
    file_path: str, course_id: int, for_initial_assessment: bool = False
):
    """
    导入 Excel 格式题库。
    :param file_path: Excel 文件路径。
    :param course_id: 课程 ID。
    :param for_initial_assessment: 是否标记为初始评测题目。
    :return: None。
    """
    try:
        import pandas as pd
    except ImportError:
        print("请先安装 pandas openpyxl")
        return

    course = get_course(course_id)
    path = resolve_path(file_path)
    if not path.exists():
        print(f"错误：文件不存在 - {path}")
        return

    all_kps = list(KnowledgePoint.objects.filter(course=course))
    kp_by_name = {kp.name: kp for kp in all_kps}

    stem = path.stem
    filename_topic = re.sub(r"^\d+", "", stem).strip()
    filename_kp = _match_kp_by_topic(filename_topic, all_kps) if filename_topic else None
    if filename_kp:
        print(f'  文件名匹配知识点: "{filename_topic}" → {filename_kp.name}')

    xls = pd.ExcelFile(path)
    total = 0
    kp_linked = 0
    kp_unmatched_names = set()

    for sheet in xls.sheet_names:
        df = pd.read_excel(path, sheet_name=sheet)
        if df.empty:
            continue

        cols = list(df.columns)

        for _, row in df.iterrows():
            content = _extract_question_content(row, cols)
            if not content:
                continue

            content = _strip_html(content)
            type_val = (
                clean_nan(row.get("小题题型"))
                or clean_nan(row.get("题型"))
                or clean_nan(row.get("题目类型"))
                or ""
            )
            question_type = TYPE_MAP.get(type_val, "single_choice")

            difficulty_val = clean_nan(row.get("难易度")) or clean_nan(row.get("难度")) or ""
            difficulty = DIFFICULTY_MAP.get(difficulty_val, "medium")
            chapter = clean_nan(row.get("目录")) or clean_nan(row.get("章节")) or ""

            options = []
            for index in range(26):
                label = chr(ord("A") + index)
                raw = row.get(f"选项{label}") if f"选项{label}" in cols else row.get(label)
                if raw is None:
                    continue

                text = _strip_html(clean_nan(raw))
                if text:
                    options.append({"label": label, "content": text})

            question_score = safe_float(
                clean_nan(row.get("分值"))
                or clean_nan(row.get("建议分数"))
                or clean_nan(row.get("得分"))
                or clean_nan(row.get("分数")),
                default=1.0,
            )

            ans_val = _strip_html(
                clean_nan(row.get("正确答案")) or clean_nan(row.get("答案")) or ""
            )
            if question_type == "multiple_choice":
                answers = [
                    value.strip()
                    for value in re.split(r"[,;，；\s]", ans_val)
                    if value.strip()
                ]
                if len(answers) == 1 and len(answers[0]) > 1:
                    # Excel 常把多选答案写成连续字符串，如 ABC。
                    answers = list(answers[0])
                answer = {"answers": answers}
            elif question_type == "true_false":
                if ans_val.upper() == "A" or ans_val in ("正确", "对", "True", "true", "T"):
                    answer = {"answer": "true"}
                elif ans_val.upper() == "B" or ans_val in (
                    "错误",
                    "错",
                    "False",
                    "false",
                    "F",
                ):
                    answer = {"answer": "false"}
                else:
                    answer = {"answer": ans_val}
            else:
                answer = {"answer": ans_val}

            analysis = _strip_html(
                clean_nan(row.get("答案解析")) or clean_nan(row.get("解析")) or ""
            )

            if question_type == "true_false" and options:
                tf_options = []
                for option in options:
                    text = option["content"].strip()
                    if text in ("正确", "对", "True", "true", "T"):
                        tf_options.append(
                            {"label": option["label"], "content": text, "value": "true"}
                        )
                    elif text in ("错误", "错", "False", "false", "F"):
                        tf_options.append(
                            {"label": option["label"], "content": text, "value": "false"}
                        )
                    else:
                        tf_options.append(option)
                options = tf_options

            question = Question.objects.create(
                course=course,
                content=content,
                question_type=question_type,
                options=options,
                answer=answer,
                analysis=analysis,
                difficulty=difficulty,
                score=question_score,
                chapter=chapter or None,
                for_initial_assessment=for_initial_assessment,
            )

            linked = False
            kp_cell = clean_nan(row.get("知识点") or "")
            if kp_cell:
                linked = _link_question_knowledge_points(
                    question,
                    [
                        kp_name.strip()
                        for kp_name in split_multi_values(kp_cell)
                        if kp_name.strip()
                    ],
                    kp_by_name,
                    all_kps,
                    kp_unmatched_names,
                )

            # Excel 未显式给出知识点时，回退到文件名匹配结果。
            if not linked and filename_kp:
                question.knowledge_points.add(filename_kp)
                linked = True

            if linked:
                kp_linked += 1
            total += 1

    result = f"题库导入完成：{total} 题"
    if kp_linked:
        result += f"，{kp_linked} 题已关联知识点"
    if total > kp_linked:
        result += f"，{total - kp_linked} 题未关联知识点"
    if kp_unmatched_names:
        result += f"\n  {_status_flag(False)} 未匹配的知识点名称: {', '.join(sorted(kp_unmatched_names))}"
    print(result)
