# FIXME: start_task_use_caseとstart_pomodoroで同じ処理があるので、うまく切り分けること

from slack_sdk.web import WebClient

from domain.channel.thread import Thread
from domain.event_scheduler.pomodoro_timer_request import PomodoroTimerRequest
from domain.infrastructure.api.google_calendar_api import GoogleCalendarApi
from domain.infrastructure.api.notion_api import NotionApi
from domain.task import TaskRepository
from domain.task.task_button_service import TaskButtonSerivce
from usecase.service.event_bridge_scheduler_service import EventBridgeSchedulerService

POMODORO_ICON = "tomato"

class StartPomodoro:
    def __init__(
        self,
        notion_api: NotionApi,
        google_api: GoogleCalendarApi,
        client: WebClient,
        task_button_service: TaskButtonSerivce,
        task_repository: TaskRepository|None = None,
    ):
        from infrastructure.task.notion_task_repository import NotionTaskRepository
        self.notion_api = notion_api
        self.google_api = google_api
        self.client = client
        self.task_button_service = task_button_service
        self.scheduler_service = EventBridgeSchedulerService()
        self.task_repository = task_repository or NotionTaskRepository()

    def handle(
            self,
            task_page_id: str,
            slack_thread: Thread|None = None) -> None:
        """ポモドーロの開始を通達する"""
        task = self.task_repository.find_by_id(task_page_id)

        if slack_thread is None or slack_thread.thread_ts is None:
            slack_thread = self.task_button_service.print_task(task)

        # 開始を連絡
        slack_thread = self.task_button_service.start_pomodoro(
            task=task,
            slack_thread=slack_thread)

        # ポモドーロカウンターをインクリメント
        # FIXME: task.increment_pomodoro_count()を呼び出したあとに保存すればよい
        self.task_repository.update_pomodoro_count(task)
        task.increment_pomodoro_count()

        # Googleカレンダーにイベントを登録する
        self._record_google_calendar_achivement(task_title=task.title, task_url=task.url)

        # 予約投稿を準備
        request = PomodoroTimerRequest(
            page_id=task.task_id,
            channel=slack_thread.channel_id,
            thread_ts=slack_thread.thread_ts,
        )
        self.scheduler_service.set_pomodoro_timer(request=request)

        # ポモドーロ開始を示すリアクションをつける
        self.client.reactions_add(
            channel=request.channel,
            timestamp=slack_thread.event_ts,
            name=POMODORO_ICON,
        )
