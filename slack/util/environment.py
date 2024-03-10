import os


class Environment:
    @staticmethod
    def is_dev() -> bool:
        return os.environ.get("ENVIRONMENT") == "dev"

    @staticmethod
    def is_demo() -> bool:
        return os.environ.get("IS_DEMO") == "true"
