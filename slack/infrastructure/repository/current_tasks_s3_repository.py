from util.s3_utils import S3Utils


class CurrentTasksS3Repository:
    FILE_NAME = "current_tasks.json"
    def save(self, data: list) -> bool:
        return S3Utils.save(data, self.FILE_NAME)

    def load(self) -> list | None:
        return S3Utils.load(self.FILE_NAME)
