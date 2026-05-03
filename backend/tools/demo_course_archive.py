#!/user/bin/env python
# -*- coding: UTF-8 -*-
"""
答辩演示课程压缩包生成工具。
@Project : wisdom-edu
@File : demo_course_archive.py
@Author : Qintsg
@Date : 2026-03-27
"""

from __future__ import annotations

import shutil
import tempfile
import zipfile
from pathlib import Path

from tools.common import build_course_asset_bundle, resolve_path


# 维护意图：将单个文件复制到目标目录。
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def _copy_file_to_dir(source_file: Path, target_dir: Path, target_name: str | None = None) -> None:
    """
    将单个文件复制到目标目录。
    :param source_file: 源文件路径。
    :param target_dir: 目标目录路径。
    :return: None。
    """

    target_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_file, target_dir / (target_name or source_file.name))


# 维护意图：解析输出压缩包路径。
# 边界说明：输入兼容性在这里收敛，避免上层重复处理旧字段。
# 风险说明：调整兼容字段或校验规则时，需同步前端表单和导入样例。
def _resolve_output_path(output_path: str | None) -> Path:
    """
    解析输出压缩包路径。
    :param output_path: 用户传入的输出路径。
    :return: 带 `.zip` 后缀的绝对路径。
    """

    raw_output_path = output_path or "../output/答辩演示课程导入包.zip"
    resolved_output_path = resolve_path(raw_output_path)
    if resolved_output_path.suffix.lower() != ".zip":
        resolved_output_path = resolved_output_path.with_suffix(".zip")
    resolved_output_path.parent.mkdir(parents=True, exist_ok=True)
    return resolved_output_path


# 维护意图：生成教师端演示用课程导入压缩包。
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def generate_demo_course_archive(
    course_name: str = "大数据技术与应用",
    output_path: str | None = None,
) -> Path:
    """
    生成教师端演示用课程导入压缩包。
    :param course_name: 资源来源课程名称。
    :param output_path: 输出压缩包路径。
    :return: 生成完成后的压缩包路径。
    """

    bundle = build_course_asset_bundle(course_name=course_name)
    if not bundle.knowledge_file or not bundle.initial_assessment_file:
        raise FileNotFoundError("未找到课程图谱或初始评测文件，无法生成答辩演示压缩包。")
    if not bundle.homework_files:
        raise FileNotFoundError("未找到作业库 Excel 文件，无法生成答辩演示压缩包。")

    archive_output_path = _resolve_output_path(output_path)
    staging_dir = Path(tempfile.mkdtemp(prefix="defense_demo_archive_"))
    archive_root = staging_dir / "答辩演示课程导入包"

    try:
        # 保留后端当前识别逻辑依赖的标准文件名和目录名，确保教师端上传后可直接导入。
        _copy_file_to_dir(bundle.knowledge_file, archive_root, target_name="knowledge-map.xlsx")
        _copy_file_to_dir(bundle.initial_assessment_file, archive_root, target_name="initial-assessment.xls")

        for homework_file in bundle.homework_files[:3]:
            _copy_file_to_dir(homework_file, archive_root / "homework")

        if bundle.resources_file:
            _copy_file_to_dir(bundle.resources_file, archive_root, target_name="resources.json")

        for ppt_file in bundle.ppt_files[:3]:
            _copy_file_to_dir(ppt_file, archive_root / "slides" / "defense-demo")

        for video_file in bundle.video_files[:1]:
            _copy_file_to_dir(video_file, archive_root / "videos")

        for textbook_file in bundle.textbook_files[:1]:
            _copy_file_to_dir(textbook_file, archive_root / "textbooks")

        with zipfile.ZipFile(archive_output_path, "w", compression=zipfile.ZIP_DEFLATED) as zip_file:
            for staged_file in archive_root.rglob("*"):
                if staged_file.is_file():
                    zip_file.write(staged_file, staged_file.relative_to(staging_dir))
    finally:
        shutil.rmtree(staging_dir, ignore_errors=True)

    print(f"答辩演示课程压缩包已生成: {archive_output_path}")
    return archive_output_path
