import os
import sys
import traceback

from slack_sdk.web import WebClient

from domain.channel.thread import Thread


class ErrorReporter:
    def __init__(self, client: WebClient|None=None) -> None:
        self.client = client or WebClient(token=os.environ["SLACK_BOT_TOKEN"])

    def execute(
            self,
            slack_thread: Thread|None = None,
            message: str|None = None) -> None:

        message = message or "something error"
        slack_thread = slack_thread or Thread.empty()
        formatted_exception = _generate_formatted_exception()
        text=f"{message}\n```{formatted_exception}```"

        self.client.chat_postMessage(
            text=text,
            channel=slack_thread.channel_id,
            thread_ts=slack_thread.thread_ts)

def _generate_formatted_exception() -> str:
    exc_info = sys.exc_info()
    t, v, tb = exc_info
    return "\n".join(traceback.format_exception(t, v, tb))

if __name__ == "__main__":
    # python -m slack.util.error_reporter
    error_reporter = ErrorReporter()
    error_reporter.execute()
