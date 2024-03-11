
import json
from pathlib import Path

from util.environment import Environment
from util.s3_utils import S3Utils

FILE_NAME = "current_tasks.json"
FILE_PATH = f"/tmp/{FILE_NAME}"

class CurrentTasksS3Repository:

    def save(self, data: list) -> bool:
        # 一時ディレクトリにファイルを保存
        with Path.open(FILE_PATH, "w") as f:
            json.dump(data, f, indent=4)
        return S3Utils.save(data, FILE_NAME) if not Environment.is_dev() else True

    def load(self) -> list | None:
        # 一時ディレクトリにファイルがあればそれを返す
        if Path(FILE_PATH).exists():
            with Path.open(FILE_PATH, "r") as f:
                return json.load(f)
        return S3Utils.load(FILE_NAME) if not Environment.is_dev() else None
