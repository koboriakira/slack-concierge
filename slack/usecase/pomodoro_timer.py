import random
from slack_sdk.web import WebClient
from domain_service.block.block_builder import BlockBuilder
from domain.user import UserKind
from util.datetime import now


class PomodoroTimer:
    def __init__(self, client: WebClient):
        self.client = client

    def handle(self, notion_page_block_id: str, channel: str, thread_ts: str):
        """ ポモドーロの終了を通達する """
        user_mention = UserKind.KOBORI_AKIRA.mention()

        block_builder = BlockBuilder()
        block_builder = block_builder.add_section(
            text=f"{user_mention}\n25分が経過しました！\n進捗や気持ちをメモして休憩してください。"
        )
        video_5minutes = _suggest_rest_action()
        block_builder = block_builder.add_section(
            text=f"休憩時にオススメ！\n{video_5minutes}"
        )
        block_builder = block_builder.add_button_action(
            action_id="start-pomodoro",
            text="再開",
            value=notion_page_block_id,
            style="primary",
        )
        block_builder = block_builder.add_button_action(
            action_id="complete-task",
            text="終了",
            value=notion_page_block_id,
            style="danger",
        )
        block_builder = block_builder.add_context({
            "channel_id": channel,
            "thread_ts": thread_ts,
            })
        blocks = block_builder.build()

        self.client.chat_postMessage(text="", blocks=blocks, channel=channel, thread_ts=thread_ts)

def _suggest_rest_action() -> str:
    hour = now().time().hour
    action = random.choice(["家事の確認", "ストレッチ"])
    if hour < 12:
        # 朝活、ヨガ系の動画
        url = random.choice([
            "https://youtube.com/watch?v=8FX9ZwDvf_0&si=Bw3P_R-ki7I3RnUo" # 5分ヨガ
        ])
        return f"休憩時のオススメ！\n{url}"
    elif 12 <= hour < 18:
        if action == "家事の確認":
            housework = random.choice(["洗濯",
                                       "トイレ掃除",
                                       "リビング掃除",
                                       "食器洗い"])
            return f"休憩時のオススメ！\n{housework}はやりましたか？"
        elif action == "ストレッチ":
            url = random.choice([
                "https://youtube.com/watch?v=8FX9ZwDvf_0&si=Bw3P_R-ki7I3RnUo" # FIXME: あとで差し替える
            ])
            return f"休憩時のオススメ！\n{url}"
        else:
            raise ValueError(f"Unexpected action: {action}")
    else:
        if action == "家事の確認":
            housework = random.choice(["洗濯",
                                       "リビング掃除",
                                       "食器洗い"])
            return f"休憩時のオススメ！\n{housework}はやりましたか？"
        elif action == "ストレッチ":
            url = random.choice([
                "https://youtube.com/watch?v=8FX9ZwDvf_0&si=Bw3P_R-ki7I3RnUo" # FIXME: あとで差し替える
            ])
            return f"休憩時のオススメ！\n{url}"
        else:
            raise ValueError(f"Unexpected action: {action}")

if __name__ == "__main__":
    # python -m usecase.pomodoro_timer
    import os

    suite = PomodoroTimer(
        client=WebClient(token=os.environ["SLACK_BOT_TOKEN"]),
    )
    suite.handle(
        notion_page_block_id="62273ee7-be18-4b75-9b52-ca118214c8b5",
        channel="C05F6AASERZ",
        thread_ts="1706668465.883669")
