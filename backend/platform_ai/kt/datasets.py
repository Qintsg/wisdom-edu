"""
MEFKT 公开数据集适配。

当前优先支持仓库内已经存在的标准三行文本数据集，
并为 MEFKT 训练流水线提供统一的数据集发现与路径解析能力。
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
DATASET_ROOT = BASE_DIR / "models" / "MEFKT" / "public_datasets"
DEFAULT_PUBLIC_DATASET = "assist2017"


# 维护意图：描述公开 KT 数据集的路径与格式信息
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
@dataclass(frozen=True)
class PublicDatasetInfo:
    """描述公开 KT 数据集的路径与格式信息。"""

    name: str
    train_path: Path | None
    test_path: Path | None
    format: str

    # 维护意图：判断训练文件是否已在本地就绪
    # 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
    # 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
    @property
    def is_available(self) -> bool:
        """判断训练文件是否已在本地就绪。"""
        return bool(self.train_path and self.train_path.exists())


PUBLIC_DATASETS: dict[str, dict[str, str]] = {
    "assist2009": {
        "train": "assist2009/builder_train.csv",
        "test": "assist2009/builder_test.csv",
        "format": "csv",
    },
    "assist2015": {
        "train": "assist2015/assist2015_train.txt",
        "test": "assist2015/assist2015_test.txt",
        "format": "three_line_txt",
    },
    "assist2017": {
        "train": "assist2017/assist2017_train.txt",
        "test": "assist2017/assist2017_test.txt",
        "format": "three_line_txt",
    },
    "kddcup2010": {
        "train": "kddcup2010/kddcup2010_train.txt",
        "test": "kddcup2010/kddcup2010_test.txt",
        "format": "three_line_txt",
    },
    "statics2011": {
        "train": "statics2011/static2011_train.txt",
        "test": "statics2011/static2011_test.txt",
        "format": "three_line_txt",
    },
}


# 维护意图：返回指定公开数据集的标准路径描述
# 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
# 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
def get_public_dataset_info(dataset_name: str) -> PublicDatasetInfo:
    """返回指定公开数据集的标准路径描述。"""

    key = (dataset_name or "").strip().lower()
    if key not in PUBLIC_DATASETS:
        raise ValueError(f"不支持的数据集: {dataset_name}")

    config = PUBLIC_DATASETS[key]
    train_path = DATASET_ROOT / config["train"]
    test_path = DATASET_ROOT / config["test"]
    return PublicDatasetInfo(
        name=key,
        train_path=train_path,
        test_path=test_path,
        format=config["format"],
    )


# 维护意图：列出当前支持的公开数据集及其可用状态
# 边界说明：读取边界集中在这里，避免调用方绕过筛选与权限约束。
# 风险说明：调整筛选、权限或排序时，需同步接口契约和分页测试。
def list_public_datasets() -> list[dict[str, str | bool | None]]:
    """列出当前支持的公开数据集及其可用状态。"""

    datasets: list[dict[str, str | bool | None]] = []
    for dataset_name in PUBLIC_DATASETS:
        info = get_public_dataset_info(dataset_name)
        datasets.append(
            {
                "name": info.name,
                "train_path": str(info.train_path) if info.train_path else None,
                "test_path": str(info.test_path) if info.test_path else None,
                "format": info.format,
                "available": info.is_available,
            }
        )
    return datasets

