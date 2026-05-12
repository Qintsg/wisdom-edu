"""教师端课程管理共享 helper。"""
from __future__ import annotations

import tempfile
import zipfile
from pathlib import Path


COURSE_CONFIG_DEFAULTS = {
    "exam_pass_score": 60,
    "exam_duration": 90,
    "allow_retake": True,
    "max_retake_times": 3,
    "resource_approval": False,
    "auto_publish_exam": False,
    "show_answer_after_exam": True,
    "allow_late_submission": False,
    "initial_assessment_count": 10,
}


def extract_course_archive(archive_file) -> tempfile.TemporaryDirectory | None:
    """解压课程资源压缩包并返回临时目录句柄。"""
    if not archive_file:
        return None
    temp_dir = tempfile.TemporaryDirectory(prefix="course_archive_", ignore_cleanup_errors=True)
    archive_path = Path(temp_dir.name) / archive_file.name
    with archive_path.open("wb+") as destination:
        for chunk in archive_file.chunks():
            destination.write(chunk)
    with zipfile.ZipFile(archive_path, "r") as zip_file:
        zip_file.extractall(temp_dir.name)
    return temp_dir


def resolve_archive_root(temp_dir: tempfile.TemporaryDirectory) -> str:
    """定位压缩包导入根目录。"""
    root = Path(temp_dir.name)
    children = [item for item in root.iterdir() if item.name != "__MACOSX" and item.suffix.lower() != ".zip"]
    if len(children) == 1 and children[0].is_dir():
        return str(children[0])
    return str(root)
