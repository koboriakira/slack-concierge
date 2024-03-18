# FIXME: start_task_use_caseとstart_pomodoroで同じ処理があるので、うまく切り分けること

from datetime import datetime, timedelta

from domain.channel.thread import Thread
from domain.event_scheduler.pomodoro_timer_request import PomodoroTimerRequest
from domain.schedule.achievement import Achievement
from domain.schedule.achievement_repository import AchievementRepository
from domain.task import TaskRepository
from domain.task.task_button_service import TaskButtonSerivce
from usecase.service.event_bridge_scheduler_service import EventBridgeSchedulerService
from util.datetime import jst_now

POMODORO_ICON = "tomato"

class StartPomodoro:
    def __init__(
        self,
        task_button_service: TaskButtonSerivce,
        achievement_repository: AchievementRepository,
        task_repository: TaskRepository|None = None,
        scheduler_service: EventBridgeSchedulerService|None = None,
    )->None:
        from infrastructure.task.notion_task_repository import NotionTaskRepository
        self.task_button_service = task_button_service
        self.achievement_repository = achievement_repository
        self.task_repository = task_repository or NotionTaskRepository()
        self.scheduler_service = scheduler_service or EventBridgeSchedulerService()

    def handle(
            self,
            task_page_id: str,
            start: datetime|None = None,
            slack_thread: Thread|None = None) -> None:
        """ポモドーロの開始を通達する"""
        start = start or jst_now()
        task = self.task_repository.find_by_id(task_page_id)

        if slack_thread is None or slack_thread.thread_ts is None:
            slack_thread = self.task_button_service.print_task(task)

        # ポモドーロカウンターをインクリメント
        # FIXME: task.increment_pomodoro_count()を呼び出したあとに保存すればよい
        self.task_repository.update_pomodoro_count(task=task)
        # task.increment_pomodoro_count()

        # Googleカレンダーにイベントを登録する
        achivement = Achievement(
            title=task.title,
            start=start,
            end=start + timedelta(minutes=25),
            frontmatter={
                "notion_url": task.url,
            },
            text="",
        )
        self.achievement_repository.save(achivement)

        # 開始を連絡
        slack_thread = self.task_button_service.start_pomodoro(
            task=task,
            slack_thread=slack_thread)

        # 予約投稿を準備
        request = PomodoroTimerRequest(
            page_id=task.task_id,
            channel=slack_thread.channel_id,
            thread_ts=slack_thread.thread_ts,
            event_ts=slack_thread.event_ts,
        )
        self.scheduler_service.set_pomodoro_timer(request=request)
