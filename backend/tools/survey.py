"""
问卷导入模块

支持从Excel导入能力量表、学习习惯问卷等。
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Protocol

from django.db import transaction

from assessments.models import SurveyQuestion
from courses.models import Course
from tools.common import clean_nan, resolve_path


class DataFrameLike(Protocol):
    """问卷导入只依赖 DataFrame 的列名和按行迭代能力。"""

    columns: Iterable[object]

    def iterrows(self) -> Iterable[tuple[object, Mapping[object, object]]]:
        """逐行返回索引和值映射。"""


class PandasLike(Protocol):
    """延迟导入 pandas 时使用的最小接口。"""

    def read_excel(self, path: Path) -> DataFrameLike:
        """读取 Excel 文件并返回 DataFrame。"""


@dataclass(frozen=True)
class OptionColumnPair:
    """单个选项标签列和可选分值列。"""

    option_col: object
    score_col: object | None


@dataclass(frozen=True)
class SurveyColumnMap:
    """问卷 Excel 列映射。"""

    text_col: object
    dimension_col: object | None
    option_columns: dict[str, OptionColumnPair]


def import_survey_questions(
    file_path: str,
    survey_type: str,
    course_id: Optional[int] = None,
) -> None:
    """导入问卷题目（Excel格式）"""
    pandas_module = import_pandas()
    if pandas_module is None:
        return

    path = resolve_path(file_path)
    if not path.exists():
        print(f'错误：文件不存在 - {path}')
        return

    dataframe = pandas_module.read_excel(path)
    column_map = resolve_survey_columns(list(dataframe.columns))
    course = Course.objects.filter(id=course_id).first() if course_id else None
    count = persist_survey_questions(
        dataframe=dataframe,
        column_map=column_map,
        survey_type=survey_type,
        course=course,
    )
    print(f'导入问卷完成：{count} 题')


def import_pandas() -> PandasLike | None:
    """延迟导入 pandas，避免普通工具命令强制依赖 Excel 栈。"""
    try:
        import pandas as pd
    except ImportError:
        print('请先安装 pandas openpyxl')
        return None
    return pd


def resolve_survey_columns(columns: list[object]) -> SurveyColumnMap:
    """识别题干、维度、选项和分值列。"""
    return SurveyColumnMap(
        text_col=find_first_matching_column(columns, ['题目', 'question', 'text']) or columns[0],
        dimension_col=find_first_matching_column(columns, ['维度', 'dimension']),
        option_columns={
            label: pair
            for label in ['A', 'B', 'C', 'D', 'E']
            if (pair := resolve_option_columns(columns, label)) is not None
        },
    )


def find_first_matching_column(columns: Iterable[object], keywords: Iterable[str]) -> object | None:
    """按关键字查找第一个匹配列。"""
    normalized_keywords = [keyword.lower() for keyword in keywords]
    for column in columns:
        normalized_column = str(column).lower()
        if any(keyword in normalized_column for keyword in normalized_keywords):
            return column
    return None


def resolve_option_columns(columns: Iterable[object], label: str) -> OptionColumnPair | None:
    """解析单个选项标签和分值列。"""
    option_col = find_named_column(columns, [label, f'选项{label}'])
    if option_col is None:
        return None
    score_col = find_named_column(columns, [f'分值{label}', f'score{label}'])
    return OptionColumnPair(option_col=option_col, score_col=score_col)


def find_named_column(columns: Iterable[object], names: Iterable[str]) -> object | None:
    """按列名精确匹配 Excel 列。"""
    expected_names = set(names)
    for column in columns:
        if str(column).strip() in expected_names:
            return column
    return None


def persist_survey_questions(
    *,
    dataframe: DataFrameLike,
    column_map: SurveyColumnMap,
    survey_type: str,
    course: Course | None,
) -> int:
    """遍历 Excel 行并写入问卷题目。"""
    count = 0
    with transaction.atomic():
        for row_index, row in dataframe.iterrows():
            if create_question_from_row(
                row=row,
                row_index=row_index,
                column_map=column_map,
                survey_type=survey_type,
                course=course,
            ):
                count += 1
    return count


def create_question_from_row(
    *,
    row: Mapping[object, object],
    row_index: object,
    column_map: SurveyColumnMap,
    survey_type: str,
    course: Course | None,
) -> bool:
    """从单行 Excel 数据创建问卷题目，空题干或空选项会跳过。"""
    text = clean_nan(row.get(column_map.text_col, ''))
    if not text:
        return False

    options = build_survey_options(row, column_map.option_columns)
    if not options:
        return False

    SurveyQuestion.objects.create(
        survey_type=survey_type,
        course=course,
        text=text,
        question_type='single_select',
        dimension=resolve_dimension(row, column_map.dimension_col),
        options=options,
        order=row_index,
        is_global=course is None,
    )
    return True


def build_survey_options(
    row: Mapping[object, object],
    option_columns: Mapping[str, OptionColumnPair],
) -> list[dict[str, object]]:
    """从行数据中构造有效选项列表。"""
    options: list[dict[str, object]] = []
    for label, column_pair in option_columns.items():
        label_text = clean_nan(row.get(column_pair.option_col))
        if not label_text:
            continue
        options.append({
            'value': label,
            'label': label_text,
            'score': resolve_option_score(row, column_pair.score_col, len(options)),
        })
    return options


def resolve_option_score(
    row: Mapping[object, object],
    score_col: object | None,
    current_option_count: int,
) -> int:
    """解析选项分值，缺失时沿用原有倒序默认分。"""
    raw_score = clean_nan(row.get(score_col)) if score_col else None
    if raw_score in (None, ''):
        return 5 - current_option_count
    try:
        return int(float(raw_score))
    except (TypeError, ValueError, OverflowError):
        return 1


def resolve_dimension(row: Mapping[object, object], dimension_col: object | None) -> str | None:
    """解析维度列，空值返回 None。"""
    dimension_value = clean_nan(row.get(dimension_col, '')) if dimension_col else None
    return dimension_value or None


def import_ability_scale(file_path: str, course_id: Optional[int] = None) -> None:
    """导入能力量表（便捷方法）"""
    import_survey_questions(file_path, 'ability', course_id=course_id)
