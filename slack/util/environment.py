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

    @staticmethod
    def get_slack_bot_token() -> str:
        return os.environ.get("SLACK_BOT_TOKEN")
