"""
公共工具函数和数据类

提供文件路径解析、JSON加载、课程获取等基础功能。
"""

import json
import math
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from django.contrib.auth import get_user_model

from courses.models import Course

User = get_user_model()

# 基础目录配置
BASE_DIR = Path(__file__).resolve().parent.parent
COURSE_RESOURCES_DIR = BASE_DIR / "tools" / "自适应学习系统-课程资源"

# 正则表达式模式
SEMICOLON_SEPARATOR_PATTERN = re.compile(r"[;；]")
MULTI_SEPARATOR_PATTERN = re.compile(r"[;；,，、|\s]+")


# 维护意图：课程资源包数据类
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@dataclass
class CourseAssetBundle:
    """课程资源包数据类"""

    course_name: str
    knowledge_file: Optional[Path] = None
    initial_assessment_file: Optional[Path] = None
    homework_files: List[Path] = field(default_factory=list)
    resources_file: Optional[Path] = None
    ppt_files: List[Path] = field(default_factory=list)
    video_files: List[Path] = field(default_factory=list)
    textbook_files: List[Path] = field(default_factory=list)


# 维护意图：分割多值字符串（分号、逗号、顿号、竖线、空格等）
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def split_multi_values(value: str) -> List[str]:
    """分割多值字符串（分号、逗号、顿号、竖线、空格等）"""
    values = MULTI_SEPARATOR_PATTERN.split(value or "")
    return [v.strip() for v in values if v and v.strip()]


# 维护意图：在指定目录中查找第一个匹配模式的文件
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def find_first_file(base_dir: Path, patterns: List[str]) -> Optional[Path]:
    """在指定目录中查找第一个匹配模式的文件"""
    for pattern in patterns:
        matched = sorted(base_dir.glob(pattern))
        if matched:
            return matched[0]
    return None


# 维护意图：解析文件路径，相对路径转为基于BASE_DIR的绝对路径
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def resolve_path(file_path: str) -> Path:
    """解析文件路径，相对路径转为基于BASE_DIR的绝对路径"""
    p = Path(file_path)
    return p if p.is_absolute() else BASE_DIR / p


# 维护意图：加载JSON文件
# 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
# 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
def load_json(file_path: str) -> dict:
    """加载JSON文件"""
    path = resolve_path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {path}")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


# 维护意图：根据ID获取课程对象
# 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
# 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
def get_course(course_id: int) -> Course:
    """根据ID获取课程对象"""
    try:
        return Course.objects.get(id=course_id)
    except Course.DoesNotExist as e:
        raise ValueError(f"课程不存在: {course_id}") from e


# 维护意图：清理NaN和None值，返回干净的字符串
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def clean_nan(value) -> str:
    """清理NaN和None值，返回干净的字符串"""
    if value is None:
        return ""
    if isinstance(value, float) and math.isnan(value):
        return ""
    s = str(value).strip()
    if s.lower() in ("nan", "none", "null"):
        return ""
    return s


# 维护意图：安全转换为浮点数，处理NaN
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def safe_float(value, default: float = 0.0) -> float:
    """安全转换为浮点数，处理NaN"""
    if value is None:
        return default
    try:
        f = float(value)
        if math.isnan(f) or math.isinf(f):
            return default
        return f
    except (ValueError, TypeError):
        return default


# 维护意图：构建课程资源包，自动查找并关联资源文件
# 边界说明：构造逻辑集中在这里，调用方只消费稳定载荷结构。
# 风险说明：调整返回结构时，需同步序列化契约和调用方断言。
def build_course_asset_bundle(
    course_name: str, base_dir: Optional[Path] = None
) -> CourseAssetBundle:
    """构建课程资源包，自动查找并关联资源文件"""
    name = course_name.strip()

    # 课程使用课程资源目录
    root = Path(base_dir) if base_dir else COURSE_RESOURCES_DIR

    knowledge_file = find_first_file(
        root,
        [
            f"*{name}*图谱*.xlsx",
            f"*{name}*图谱*.xls",
            f"*{name}*knowledge*.json",
            "knowledge-map.xlsx",
            "knowledge-map.xls",
            "knowledge-map.json",
            "knowledge.json",
            "*图谱构建.xlsx",
            "*图谱构建.xls",
            "大数据图谱构建.xlsx",
        ],
    )

    initial_assessment_file = find_first_file(
        root,
        [
            f"*{name}*初始评测*.xlsx",
            f"*{name}*初始评测*.xls",
            "initial-assessment.xlsx",
            "initial-assessment.xls",
            "*知识初始评测.xlsx",
            "*知识初始评测.xls",
            "大数据知识初始评测.xls",
        ],
    )

    homework_files = []
    # 兼容两种目录名：“作业库”和“作业库(excel)”
    for hw_name in ["作业库", "作业库(excel)", "homework", "homework(excel)", "homeworks"]:
        homework_dir = root / hw_name
        if homework_dir.exists():
            homework_files.extend(sorted(homework_dir.glob("*.xlsx")))
            homework_files.extend(sorted(homework_dir.glob("*.xls")))
            break

    ppt_files = []
    for ppt_dir_name in ["PPT", "slides"]:
        ppt_dir = root / ppt_dir_name
        if not ppt_dir.exists():
            continue
        for sub_dir in sorted(ppt_dir.iterdir()):
            if sub_dir.is_dir():
                ppt_files.extend(sorted(sub_dir.glob("*.ppt")))
                ppt_files.extend(sorted(sub_dir.glob("*.pptx")))
        ppt_files.extend(sorted(ppt_dir.glob("*.ppt")))
        ppt_files.extend(sorted(ppt_dir.glob("*.pptx")))
        break

    video_files = []
    for video_dir_name in ["教学视频", "videos"]:
        video_dir = root / video_dir_name
        if not video_dir.exists():
            continue
        for ext in ["*.mp4", "*.mov", "*.avi", "*.mkv", "*.flv", "*.wmv"]:
            video_files.extend(sorted(video_dir.glob(ext)))
        break

    textbook_files = []
    for textbook_dir_name in ["电子教材", "textbooks"]:
        textbook_dir = root / textbook_dir_name
        if not textbook_dir.exists():
            continue
        for ext in ["*.pdf", "*.epub", "*.doc", "*.docx"]:
            textbook_files.extend(sorted(textbook_dir.glob(ext)))
        break

    resources_file = find_first_file(
        root, [f"*{name}*resources*.json", f"*{name}*资源*.json"]
    )

    return CourseAssetBundle(
        course_name=name,
        knowledge_file=knowledge_file,
        initial_assessment_file=initial_assessment_file,
        homework_files=homework_files,
        ppt_files=ppt_files,
        video_files=video_files,
        textbook_files=textbook_files,
        resources_file=resources_file,
    )


# 维护意图：列出所有课程
# 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
# 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
def list_courses(show_all: bool = True):
    """列出所有课程"""
    queryset = Course.objects.all() if show_all else Course.objects.filter(is_public=True)
    courses = queryset.order_by("id")
    print("课程列表：" if show_all else "公开课程列表：")
    if not courses:
        print("(空)")
        return
    for c in courses:
        print(f"  id={c.pk}, name={c.name}, public={c.is_public}")
