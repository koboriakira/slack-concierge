

# 独自の例外
class StartTaskError(Exception):
    @staticmethod
    def unspecified() -> "StartTaskError":
        return StartTaskError("タスクIDおよびタスクタイトルが未指定です")



class StartTaskUseCase:
    def __init__(self):
        pass

    def execute(self, task_id: str|None = None, task_title: str|None = None):
        raise StartTaskError.unspecified()
