"""
问卷导入模块

支持从Excel导入能力量表、学习习惯问卷等。
"""

from typing import Optional

from django.db import transaction

from assessments.models import SurveyQuestion
from courses.models import Course

from tools.common import clean_nan, resolve_path


def import_survey_questions(
    file_path: str,
    survey_type: str,
    course_id: Optional[int] = None,
):
    """导入问卷题目（Excel格式）"""
    try:
        import pandas as pd
    except ImportError:
        print('请先安装 pandas openpyxl')
        return

    path = resolve_path(file_path)
    if not path.exists():
        print(f'错误：文件不存在 - {path}')
        return

    course = Course.objects.filter(id=course_id).first() if course_id else None

    df = pd.read_excel(path)
    columns = list(df.columns)

    text_col = next(
        (
            column
            for column in columns
            if any(keyword in str(column).lower() for keyword in ['题目', 'question', 'text'])
        ),
        columns[0],
    )
    dim_col = next(
        (
            column
            for column in columns
            if any(keyword in str(column).lower() for keyword in ['维度', 'dimension'])
        ),
        None,
    )

    count = 0
    with transaction.atomic():
        for idx, row in df.iterrows():
            text = clean_nan(row.get(text_col, ''))
            if not text:
                continue

            options = []
            for label in ['A', 'B', 'C', 'D', 'E']:
                option_col = next(
                    (
                        column
                        for column in columns
                        if str(column).strip() in [label, f'选项{label}']
                    ),
                    None,
                )
                score_col = next(
                    (
                        column
                        for column in columns
                        if str(column).strip() in [f'分值{label}', f'score{label}']
                    ),
                    None,
                )
                if option_col is None:
                    continue

                val = row.get(option_col)
                if val is None:
                    continue
                v = clean_nan(val)
                if not v:
                    continue

                try:
                    raw_score = clean_nan(row.get(score_col)) if score_col else None
                    if raw_score in (None, ''):
                        score = 5 - len(options)
                    else:
                        score = int(float(raw_score))
                except (TypeError, ValueError, OverflowError):
                    score = 1

                options.append({'value': label, 'label': v, 'score': score})

            if not options:
                continue

            dim_val = clean_nan(row.get(dim_col, '')) if dim_col else None

            SurveyQuestion.objects.create(
                survey_type=survey_type,
                course=course,
                text=text,
                question_type='single_select',
                dimension=dim_val or None,
                options=options,
                order=idx,
                is_global=course is None,
            )
            count += 1

    print(f'导入问卷完成：{count} 题')


def import_ability_scale(file_path: str, course_id: Optional[int] = None):
    """导入能力量表（便捷方法）"""
    import_survey_questions(file_path, 'ability', course_id=course_id)
