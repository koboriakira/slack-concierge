import os

class Environment:
    @staticmethod
    def is_dev():
        return os.environ.get("ENVIRONMENT") == "dev"
