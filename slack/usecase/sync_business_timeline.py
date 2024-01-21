import os
from typing import Optional
from slack_sdk import WebClient
from domain.message import Messages, BaseMessage
from util.datetime import get_current_day_and_tomorrow
from util.custom_logging import get_logger
import requests

TIMES_CHANNEL = "times-dev-小堀"
TIMES_CHANNEL_ID = "C02CVBZV0UB"

logger = get_logger(__name__)

class SyncBusinessTimeline:
    def __init__(self, original_client: WebClient):
        self.original_client: WebClient = original_client
        self.business_slack_user_bot: WebClient = WebClient(
            token=os.environ["BUSINESS_SLACK_USER_TOKEN"],
        )

    def execute(self, text: str, original_channel: str, original_thread_ts: str, file_id_list: list[str] = []) -> None:
        # 個人のつぶやきのスレッドの最初のメッセージを取得
        thread_message = self._find_thread_message(
            original_channel, original_thread_ts)
        print(thread_message)

        # 個人のスレッドの最初のメッセージと同じ内容のスレッドをtimesから探す
        # 見つけたスレッドがあれば、ぶらさげて投稿する
        thread_ts = self._find_business_thread_ts(thread_message)
        print(thread_ts)

        if len(file_id_list) > 0:
            # 画像つきでアップロード
            response = self._upload_file(
                file_id=file_id_list[0],
                text=text,
                thread_ts=thread_ts,
            )
            logger.debug(response)
            if len(file_id_list) > 1:
                thread_ts = response["ts"] if thread_ts is None else thread_ts
                for file_id in file_id_list[1:]:
                    self._upload_file(
                        file_id=file_id,
                        thread_ts=thread_ts,
                    )
        else:
            # メッセージだけ
            self.business_slack_user_bot.chat_postMessage(
                channel=TIMES_CHANNEL,
                text=text,
                thread_ts=thread_ts,
            )


    def _find_thread_message(self, channel_id: str, thread_ts: str) -> str:
        response = self.original_client.conversations_replies(
            channel=channel_id,
            ts=thread_ts,
        )
        messages = Messages([BaseMessage.from_dict(m) for m in response.get("messages", [])])
        message = messages.first()
        return message.text

    def _find_business_thread_ts(self, thread_message: str) -> Optional[str]:
        """ 個人のスレッドの最初のメッセージと同じ内容のスレッドをtimesに探す """
        (current_day, tomorrow) = get_current_day_and_tomorrow()
        response = self.business_slack_user_bot.conversations_history(
            channel=TIMES_CHANNEL_ID,
            oldest=str(current_day),
            latest=str(tomorrow),
        )

        for m in response["messages"]:
            # 全文一致しないパターンがありそうなので、先頭20文字で比較する
            if m["text"][0:20] == thread_message[0:20]:
                return m["ts"]

        logger.info("timesにスレッドが見つかりませんでした")
        return None

    def _upload_file(self, file_id: str, text: Optional[str] = None, thread_ts: Optional[str] = None) -> dict:
        response = self.original_client.files_info(
            file=file_id,
        )

        # ファイルをダウンロードして保存する
        download_response = requests.get(
            url=response['file']['url_private'],
            headers={
                'Authorization': f'Bearer {os.environ.get("SLACK_USER_TOKEN")}'})
        file_path = response['file']['name']
        with open(file_path, 'wb') as f:
            f.write(download_response.content)

        # アップロードする
        response = self.business_slack_user_bot.files_upload(
            file=response['file']['name'],
            channels=TIMES_CHANNEL,
            initial_comment=text,
            thread_ts=thread_ts,
        )

        # アップロードが完了したらファイルを削除する
        os.remove(file_path)
        return response


if __name__ == "__main__":
    # python -m usecase.sync_business_timeline
    # https://koboriakira.slack.com/archives//p1705850119369689
    usecase = SyncBusinessTimelineUseCase()
    usecase.execute(text="これはテスト",
                    original_channel="C05H3USHAJU",
                    original_thread_ts="1705850119.369689",
                    file_id_list=[])
