"""Excel 导入模板生成。

生成能力量表、学习偏好问卷、题库等 Excel 导入模板文件。
从原 tests/templates.py 迁移而来。
"""

from pathlib import Path
from typing import Optional

from tools.common import BASE_DIR


# 维护意图：生成Excel导入模板文件。
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def generate_template(
    template_type: str,
    output_dir: Optional[str] = None
):
    """生成Excel导入模板文件。

    Args:
        template_type (str): 模板类型 ('ability' | 'habit' | 'questions')
        output_dir (Optional[str]): 输出目录路径，默认为项目根目录
    """
    try:
        import pandas as pd
    except ImportError:
        print('请先安装 pandas openpyxl')
        return

    output_path = Path(output_dir) if output_dir else BASE_DIR
    output_path.mkdir(parents=True, exist_ok=True)

    if template_type == 'ability':
        df = pd.DataFrame({
            '题目内容': ['当遇到复杂问题时，你倾向于如何思考？'],
            '题型': ['single_select'],
            '选项A': ['逐步分解问题'],
            '分值A': [4],
            '选项B': ['寻找类似方案'],
            '分值B': [3],
            '选项C': ['直觉判断'],
            '分值C': [2],
            '选项D': ['寻求帮助'],
            '分值D': [1],
            '能力维度': ['logical_reasoning'],
            '顺序': [1],
        })
        p = output_path / '能力量表导入模板.xlsx'
    elif template_type == 'habit':
        df = pd.DataFrame({
            '题目内容': ['你更喜欢通过哪种形式获取新知识？'],
            '题型': ['single_select'],
            '选项A': ['观看教学视频'],
            '分值A': [4],
            '选项B': ['阅读文字资料'],
            '分值B': [3],
            '选项C': ['通过练习题实践'],
            '分值C': [2],
            '选项D': ['小组讨论学习'],
            '分值D': [1],
            '顺序': [1],
        })
        p = output_path / '学习偏好问卷导入模板.xlsx'
    elif template_type == 'questions':
        df = pd.DataFrame({
            '目录': ['大数据技术基础'],
            '题目类型': ['单选题'],
            '大题题干': ['大数据的5V特征不包括以下哪一项？'],
            '正确答案': ['C'],
            '答案解析': ['5V: Volume/Velocity/Variety/Value/Veracity'],
            '难易度': ['易'],
            '知识点': ['大数据概述'],
            '选项A': ['Volume（大量）'],
            '选项B': ['Velocity（高速）'],
            '选项C': ['Visibility（可视）'],
            '选项D': ['Variety（多样）'],
        })
        p = output_path / '题库导入模板.xlsx'
    else:
        print('未知模板类型，支持: ability, habit, questions')
        return

    df.to_excel(p, index=False)
    print(f'模板已生成: {p}')
