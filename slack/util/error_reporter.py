import os

from slack_sdk.web import WebClient


class ErrorReporter:
    def __init__(self, client: WebClient|None=None) -> None:
        self.client = client or WebClient(token=os.environ["SLACK_BOT_TOKEN"])

    def execute(
            self,
            slack_channel: str|None = None,
            slack_thread_ts: str|None = None) -> None:
        import sys
        import traceback
        exc_info = sys.exc_info()
        t, v, tb = exc_info
        formatted_exception = "\n".join(
            traceback.format_exception(t, v, tb))
        text=f"analyze_inbox: error ```{formatted_exception}```"
        self.client.chat_postMessage(
            text=text,
            channel=slack_channel or "C04Q3AV4TA5",
            thread_ts=slack_thread_ts)
