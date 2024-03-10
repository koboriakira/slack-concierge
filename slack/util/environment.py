import os

ENVIRONMENT = os.environ.get("ENVIRONMENT")
IS_DEMO = os.environ.get("IS_DEMO")

class Environment:
    @staticmethod
    def is_dev() -> bool:
        return ENVIRONMENT == "dev"

    @staticmethod
    def is_demo() -> bool:
        return IS_DEMO == "true"
