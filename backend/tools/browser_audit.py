"""浏览器巡检脚本包装器。"""

from __future__ import annotations

import subprocess
from pathlib import Path


# 维护意图：Run the frontend Playwright audit script from the backend tooling entrypoint
# 边界说明：调用契约在这里保持稳定，避免业务分支扩散到调用方。
# 风险说明：调整调用契约时，需同步调用方、文档和回归测试。
def browser_audit(
    frontend_url: str = 'http://127.0.0.1:3000',
    api_base_url: str = 'http://127.0.0.1:8000',
    output_dir: str | None = None,
    scenario: str = 'audit',
    headed: bool = False,
) -> None:
    """Run the frontend Playwright audit script from the backend tooling entrypoint."""
    root_dir = Path(__file__).resolve().parents[2]
    script_path = root_dir / 'frontend' / 'scripts' / 'browser-audit.mjs'
    if not script_path.exists():
        raise FileNotFoundError(f'未找到浏览器巡检脚本: {script_path}')

    args = [
        'node',
        str(script_path),
        '--frontend-url',
        frontend_url,
        '--api-base-url',
        api_base_url,
        '--scenario',
        scenario,
    ]
    if output_dir:
        args.extend(['--output-dir', output_dir])
    if headed:
        args.append('--headed')

    # Run from the frontend workspace so Node resolves local dependencies exactly
    # as it does in developer and CI environments.
    result = subprocess.run(args, cwd=root_dir / 'frontend', check=False)
    if result.returncode != 0:
        raise RuntimeError(f'浏览器巡检失败，退出码: {result.returncode}')
