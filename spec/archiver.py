import shutil
from datetime import datetime
from pathlib import Path


def current_timestamp():
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def archive(*, phase, tmp_path, test_name, artefacts_dir, timestamp):
    if phase != "call" or artefacts_dir is None or tmp_path is None:
        return
    shutil.copytree(tmp_path, Path(artefacts_dir) / f"{timestamp}-{test_name}")
