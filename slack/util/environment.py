import os

ENVIRONMENT = os.environ.get("ENVIRONMENT", "")
IS_DEMO = os.environ.get("IS_DEMO", "")

class Environment:
    @staticmethod
    def is_dev() -> bool:
        return ENVIRONMENT.lower() == "dev"

    @staticmethod
    def is_demo() -> bool:
        return IS_DEMO.lower() == "true"

    @staticmethod
    def get_slack_bot_token() -> str:
        return os.environ.get("SLACK_BOT_TOKEN")
