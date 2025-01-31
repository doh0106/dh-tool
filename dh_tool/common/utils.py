# dh_tool/common/utils.py
from pathlib import Path
from datetime import datetime
from typing import Union


def create_daily_folder(base_dir: Union[str, Path] = Path("/workspace/result")) -> Path:
    if isinstance(base_dir, str):
        base_dir = Path(base_dir)
    if not base_dir.exists():
        Warning(f"Base directory {base_dir} does not exist. Creating it.")
    today = datetime.now().strftime("%Y-%m-%d")
    daily_dir = base_dir / today
    daily_dir.mkdir(exist_ok=True, parents=True)
    return daily_dir
