#!/user/bin/env python
# -*- coding: UTF-8 -*-
'''
student1 桌面 HTML 快照解析工具。
@Project : wisdom-edu
@File : demo_student1_snapshot_parse.py
@Author : Qintsg
@Date : 2026-05-13 13:36
'''

from __future__ import annotations

from html import unescape
from html.parser import HTMLParser
from pathlib import Path
import re

from django.utils.html import strip_tags

from tools.demo_student1_snapshot_types import (
    DESKTOP_HTML_NAMES,
    DesktopAsset,
    DesktopSnapshot,
    QuestionSnapshot,
)


class VisibleTextParser(HTMLParser):
    """提取 HTML 可见文本，跳过脚本、样式和 SVG 路径内容。"""

    def __init__(self) -> None:
        """初始化解析器状态。"""
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """进入需要跳过的标签时增加深度。"""
        if tag.lower() in {"script", "style", "svg"}:
            self._skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        """离开需要跳过的标签时减少深度。"""
        if tag.lower() in {"script", "style", "svg"} and self._skip_depth:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        """收集非空可见文本片段。"""
        if self._skip_depth:
            return
        cleaned = normalize_space(data)
        if cleaned:
            self.parts.append(cleaned)

    def visible_text(self) -> str:
        """返回合并后的可见文本。"""
        return "\n".join(self.parts)


def load_desktop_snapshot(desktop_root: str | Path | None = None) -> DesktopSnapshot:
    """
    读取桌面三份 HTML 与资源目录并解析成业务快照。
    :param desktop_root: 桌面路径。
    :return: 归一化快照。
    """
    root = Path(desktop_root) if desktop_root else Path.home() / "Desktop"
    html_map = {key: read_required_html(root / name) for key, name in DESKTOP_HTML_NAMES.items()}
    report_text = visible_text(html_map["report"])
    profile_text = visible_text(html_map["profile"])
    path_text = visible_text(html_map["path"])
    correct_count, total_count = extract_correct_count(report_text)

    return DesktopSnapshot(
        score=extract_score(report_text),
        correct_count=correct_count,
        total_count=total_count,
        question_details=extract_questions(html_map["report"]),
        report_mastery=extract_report_mastery(html_map["report"]),
        profile_summary=extract_between(profile_text, "画像总结", "薄弱环节"),
        profile_weakness=extract_between(profile_text, "薄弱环节", "AI 学习建议"),
        profile_suggestion=extract_profile_suggestion(profile_text),
        ability_scores=extract_ability_scores(profile_text),
        learner_tags=extract_learner_tags(profile_text),
        path_titles=extract_path_titles(html_map["path"]),
        selected_path_title=extract_selected_path_title(path_text),
        selected_minutes=extract_selected_minutes(path_text),
        selected_goal=extract_selected_goal(path_text),
        selected_suggestion=extract_selected_suggestion(path_text),
        assets=collect_desktop_assets(root),
    )


def read_required_html(path: Path) -> str:
    """读取必需 HTML 文件。"""
    if not path.exists():
        raise FileNotFoundError(f"缺少桌面快照文件: {path}")
    return path.read_text(encoding="utf-8")


def visible_text(html: str) -> str:
    """提取 HTML 可见文本。"""
    parser = VisibleTextParser()
    parser.feed(html)
    return parser.visible_text()


def normalize_space(value: object) -> str:
    """压缩空白并解码 HTML 实体。"""
    return re.sub(r"\s+", " ", unescape(str(value or ""))).strip()


def clean_html_text(value: str) -> str:
    """移除 HTML 标签并清理空白。"""
    return normalize_space(strip_tags(value))


def extract_score(text: str) -> float:
    """从报告文本提取得分。"""
    match = re.search(r"(\d+(?:\.\d+)?)\s*/\s*100", text)
    return float(match.group(1)) if match else 80.0


def extract_correct_count(text: str) -> tuple[int, int]:
    """从报告文本提取答对题数和总题数。"""
    match = re.search(r"答对\s*(\d+)\s*/\s*(\d+)\s*题", text)
    if not match:
        return 40, 50
    return int(match.group(1)), int(match.group(2))


def extract_questions(html: str) -> list[QuestionSnapshot]:
    """从报告 HTML 抽取题干、答案与解析。"""
    pattern = re.compile(
        r"第\s*(?P<order>\d+)\s*题.*?"
        r"el-tag__content\">(?P<status>正确|错误)</span>.*?"
        r"question-content\">(?P<content>.*?)</p>.*?"
        r"你的答案：</span><span[^>]*>(?P<student>.*?)</span>.*?"
        r"正确答案：</span><span[^>]*>(?P<correct>.*?)</span>"
        r"(?P<trailer>.*?)(?=<div data-v-fba69e73=\"\" class=\"el-collapse-item\"|</div></div><!--v-if-->|$)",
        re.S,
    )
    questions: list[QuestionSnapshot] = []
    for match in pattern.finditer(html):
        trailer = match.group("trailer")
        analysis_match = re.search(r"解析：</span>(.*?)</p>", trailer, re.S)
        questions.append(
            QuestionSnapshot(
                order=int(match.group("order")),
                content=clean_html_text(match.group("content")),
                student_answer=parse_boolish_answer(match.group("student")),
                correct_answer=parse_boolish_answer(match.group("correct")),
                is_correct=match.group("status") == "正确",
                analysis=clean_html_text(analysis_match.group(1)) if analysis_match else "",
            )
        )
    return questions


def parse_boolish_answer(value: str) -> object:
    """将真假题显示值转成布尔，无法识别时保留文本。"""
    cleaned = clean_html_text(value).lower()
    if cleaned in {"true", "正确", "对", "是"}:
        return True
    if cleaned in {"false", "错误", "错", "否"}:
        return False
    return cleaned


def extract_report_mastery(html: str) -> dict[str, float]:
    """从测评报告掌握度条提取知识点掌握度。"""
    pattern = re.compile(
        r"mastery-name\">(?P<name>.*?)</span>.*?mastery-value\">(?P<value>\d+)%</span>",
        re.S,
    )
    return {
        clean_html_text(match.group("name")): int(match.group("value")) / 100
        for match in pattern.finditer(html)
    }


def extract_between(text: str, start: str, end: str) -> str:
    """从可见文本中截取两个标题之间的正文。"""
    start_index = text.find(start)
    if start_index < 0:
        return ""
    end_index = text.find(end, start_index + len(start))
    if end_index < 0:
        end_index = len(text)
    return normalize_multiline(text[start_index + len(start) : end_index])


def extract_profile_suggestion(text: str) -> str:
    """提取画像页 AI 学习建议正文。"""
    segment = extract_between(text, "系统基于当前画像，推荐以下学习动作：", "退出登录")
    return segment or "建议围绕 Spark SQL、自然语言处理实践和综合实践进行阶段化强化。"


def extract_ability_scores(text: str) -> dict[str, int]:
    """从雷达图 tooltip 文本提取能力分。"""
    result = {
        key: int(value)
        for key, value in re.findall(r"(处理速度|工作记忆|知觉推理|言语理解):\s*(\d+)\s*/\s*100", text)
    }
    return result or {"处理速度": 60, "工作记忆": 60, "知觉推理": 60, "言语理解": 60}


def extract_learner_tags(text: str) -> list[str]:
    """提取画像页学习者标签。"""
    tags = [tag for tag in ["高效型学习者", "视觉型", "晚间学习", "自适应"] if tag in text]
    return tags or ["高效型学习者", "视觉型", "晚间学习", "自适应"]


def extract_path_titles(html: str) -> list[str]:
    """提取学习路径地铁站标题。"""
    titles = [clean_html_text(item) for item in re.findall(r"station-label[^>]*>(.*?)</div>", html, re.S)]
    return [title for title in titles if title]


def extract_selected_path_title(text: str) -> str:
    """提取路径详情面板标题。"""
    match = re.search(r"阶段测试：.*?\n(?P<title>Spark SQL原理与特征基础)", text, re.S)
    return match.group("title") if match else "Spark SQL原理与特征基础"


def extract_selected_minutes(text: str) -> int:
    """提取当前路径节点预计时长。"""
    match = re.search(r"预计\s*(\d+)\s*分钟", text)
    return int(match.group(1)) if match else 52


def extract_selected_goal(text: str) -> str:
    """提取当前路径节点学习目标。"""
    match = re.search(r"预计\s*\d+\s*分钟\s*(.*?)\s*重点学习", text, re.S)
    return normalize_multiline(match.group(1)) if match else "掌握Spark SQL原理与特征的核心概念及应用"


def extract_selected_suggestion(text: str) -> str:
    """提取当前路径节点学习建议。"""
    match = re.search(r"(重点学习Spark SQL原理与特征相关内容。)", text)
    return match.group(1) if match else "重点学习Spark SQL原理与特征相关内容。"


def collect_desktop_assets(root: Path) -> list[DesktopAsset]:
    """汇总三份 HTML 导出的资源目录。"""
    assets: list[DesktopAsset] = []
    for directory in sorted(root.glob("* - 自适应学习系统_files")):
        if not directory.is_dir():
            continue
        for file_path in sorted(path for path in directory.rglob("*") if path.is_file()):
            assets.append(
                DesktopAsset(
                    relative_path=str(file_path.relative_to(root)).replace("\\", "/"),
                    size=file_path.stat().st_size,
                )
            )
    return assets


def normalize_multiline(value: str) -> str:
    """将多行文本整理成适合入库展示的单段文本。"""
    lines = [normalize_space(line) for line in value.splitlines()]
    return " ".join(line for line in lines if line)
