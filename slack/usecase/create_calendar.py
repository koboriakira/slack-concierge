from datetime import date as DateObject
from datetime import datetime as DatetimeObject
from datetime import time as TimeObject
from domain_service.block.block_builder import BlockBuilder
from domain_service.view.view_builder import ViewBuilder
from domain.notion.notion_page import NotionPage, RecipePage
from domain.infrastructure.api.google_calendar_api import GoogleCalendarApi
from domain.schedule.enum import Wakeup, Breakfast, GoToKindergarten, MorningHousework, Lunch, Pickup, Bathtime, Bedtime, Resttime, Dinner, WeeklyReview, CookDinner, DriveProject
from util.datetime import is_holiday
from domain.schedule.schedule import Schedule
from domain.infrastructure.api.notion_api import NotionApi


CATEGORY_MORNING = "朝の予定"
CATEGORY_LUNCH = "昼休み"
CATEGORY_EVENING = "夜の予定"
CATEGORY_PRIVATE = "プライベート"


class CreateCalendar:
    def __init__(self,
                 is_morning_childcare: bool,
                 is_evening_childcare: bool,
                 is_weekly_review: bool,
                 is_cook_dinner: bool,
                 wakeup_time: TimeObject,
                 lunch_time: TimeObject,
                 dinner_time: TimeObject,
                 breakfast_detail: str,
                 lunch_detail: str,
                 dinner_recipe_ids: list[str],
                 date: DateObject,
                 google_calendar_api: GoogleCalendarApi,
                 notion_api: NotionApi,
                 ):
        self.is_morning_childcare = is_morning_childcare
        self.is_evening_childcare = is_evening_childcare
        self.is_weekly_review = is_weekly_review
        self.is_cook_dinner = is_cook_dinner
        self.wakeup_time = wakeup_time
        self.lunch_time = lunch_time
        self.dinner_time = dinner_time
        self.breakfast_detail = breakfast_detail
        self.lunch_detail = lunch_detail
        self.dinner_recipe_ids = dinner_recipe_ids
        self.date = date
        self.google_calendar_api = google_calendar_api
        self.notion_api = notion_api
        self.latest_end = None

    def handle(self) -> str:
        """
        カレンダーを作成する
        """
        # レシピページを取得する
        dinner_recipe_pages = self.notion_api.list_recipes()
        dinner_recipe_pages = [r for r in dinner_recipe_pages if r.id in self.dinner_recipe_ids]

        # primaryステータスのプロジェクトを取得
        primary_projects: list[NotionPage] = self.notion_api.list_projects(status="Primary")

        text_list: list[str] = []

        # 完了メッセージ
        url = f"https://calendar.google.com/calendar/u/0/r/day/{self.date.strftime('%Y/%m/%d')}"
        text_list.append(f"<{url}|カレンダー>を作成しました。")

        # 起床
        wakeup_start = DatetimeObject.combine(self.date, self.wakeup_time)
        schedule = Wakeup.create(start_datetime=wakeup_start)
        self._post_gas_calendar(schedule=schedule)

        # 朝食
        schedule = Breakfast.create(
            start=self.latest_end, breakfast_detail=self.breakfast_detail)
        self._post_gas_calendar(schedule=schedule)

        # 登園
        if not is_holiday(self.date) and self.is_morning_childcare:
            schedule = GoToKindergarten.create(start=self.latest_end)
            self._post_gas_calendar(schedule=schedule)

        # 朝の家事
        schedule = MorningHousework.create(start=self.latest_end)
        self._post_gas_calendar(schedule=schedule)

        # 昼食
        lunch_start = DatetimeObject.combine(self.date, self.lunch_time)
        schedule = Lunch.create(start=lunch_start,
                                lunch_detail=self.lunch_detail)
        self._post_gas_calendar(schedule=schedule)

        # 週次レビュー
        if self.is_weekly_review:
            schedule = WeeklyReview.create(start=self.latest_end)
            self._post_gas_calendar(schedule=schedule)

        # 夕食の準備
        if self.is_cook_dinner:
            schedule = CookDinner.create(
                start=self.latest_end, dinner_recipe_pages=dinner_recipe_pages)
            self._post_gas_calendar(schedule=schedule)

        # 夜の子育て(おむかえ)
        if not is_holiday(self.date) and self.is_evening_childcare:
            pickup_start = DatetimeObject.combine(
                self.date, TimeObject(17, 45))
            schedule = Pickup.create(start=pickup_start)
            self._post_gas_calendar(schedule=schedule)

        # 夕食
        dinner_start = DatetimeObject.combine(self.date, self.dinner_time)
        schedule = Dinner.create(start=dinner_start,
                                 dinner_recipe_pages=dinner_recipe_pages)
        self._post_gas_calendar(schedule=schedule)

        if self.is_evening_childcare:
            # お風呂
            schedule = Bathtime.create(start=self.latest_end)
            self._post_gas_calendar(schedule=schedule)
            # 寝かしつけ
            bedtime_start = DatetimeObject.combine(
                self.date, TimeObject(20, 30))
            schedule = Bedtime.create(start=bedtime_start)
            self._post_gas_calendar(schedule=schedule)
        else:
            # 子育てがなければお風呂のみ
            bathtime_start = DatetimeObject.combine(
                self.date, TimeObject(21, 0))
            schedule = Bathtime.create(start=bathtime_start)
            self._post_gas_calendar(schedule=schedule)

        # 休息
        rest_start = DatetimeObject.combine(self.date, TimeObject(22, 0))
        schedule = Resttime.create(start=rest_start)
        self._post_gas_calendar(schedule=schedule)

        # 余った時間にプロジェクトを進める時間を入れる
        free_time_list = self._calculate_free_time()
        create_project_calendar = CreateProjectCalendar(
            date=self.date,
            free_time_list=free_time_list,
            project_id_list=[project.id for project in primary_projects],
            google_calendar_api=self.google_calendar_api,
            notion_api=self.notion_api)
        create_project_calendar.handle()

        return "\n".join(text_list)

    def _calculate_free_time(self) -> list[dict[str, str]]:
        """ 余った時間を計算する """
        calendar = self.google_calendar_api.get_gas_calendar(date=self.date)
        time_range_list = [{
            "start": DatetimeObject.fromisoformat(schedule["start"]),
            "end": DatetimeObject.fromisoformat(schedule["end"]),
        } for schedule in calendar]
        if not is_holiday(date=self.date):
            # 平日は仕事だと仮定して、9:30〜17:00の時間帯を追加する
            time_range_list.append({
                "start": DatetimeObject.combine(self.date, TimeObject(9, 30)),
                "end": DatetimeObject.combine(self.date, TimeObject(17, 00)),
            })
        time_range_list.sort(key=lambda range: range["start"].timestamp())

        # 起床時刻から23:00の間で、空いている時間帯を計算する
        tmp_free_time: list[dict[str, str]] = []
        base_start = DatetimeObject.combine(self.date, self.wakeup_time)
        base_end = DatetimeObject.combine(self.date, TimeObject(23, 0))
        for schedule in time_range_list:
            if schedule["start"].timestamp() > base_start.timestamp():
                # 1時間以上空いている場合は、空いている時間帯を追加する
                if schedule["start"].timestamp() - base_start.timestamp() > 60 * 60:
                    tmp_free_time.append({
                        "start": base_start.time().strftime("%H:%M"),
                        "end": schedule["start"].time().strftime("%H:%M")
                    })
            base_start = schedule["end"]
        if base_end.timestamp() > base_start.timestamp():
            # 1時間以上空いている場合は、空いている時間帯を追加する
            if base_end.timestamp() - base_start.timestamp() > 60 * 60:
                tmp_free_time.append({
                    "start": base_start.time().strftime("%H:%M"),
                    "end": base_end.time().strftime("%H:%M")
                })
        # 2時間以上ある場合は、1時間単位に分ける
        free_time_list: list[dict[str, str]] = []
        for time_range in tmp_free_time:
            start = TimeObject.fromisoformat(time_range["start"])
            end = TimeObject.fromisoformat(time_range["end"])
            range_num = ((end.hour * 60 + end.minute) -
                         (start.hour * 60 + start.minute)) // 60
            if range_num > 0:
                for hour_idx in range(range_num):
                    new_start = TimeObject(start.hour + hour_idx, start.minute)
                    new_end = TimeObject(
                        new_start.hour + 1, new_start.minute) if hour_idx < range_num - 1 else end
                    free_time_list.append({
                        "start": new_start.strftime("%H:%M"),
                        "end": new_end.strftime("%H:%M")
                    })
            else:
                free_time_list.append(time_range)
        return free_time_list


    def _post_gas_calendar(self, schedule: Schedule) -> DatetimeObject:
        self.google_calendar_api.post_schedule(schedule=schedule)
        self.latest_end = schedule.end
        return schedule.end


class CreateProjectCalendar:
    """ サブクラスのような立ち位置。プロジェクトのカレンダーをつくる """

    def __init__(self,
                 date: DateObject,
                 free_time_list: list[dict[str, str]],
                 project_id_list: list[str],
                 google_calendar_api: GoogleCalendarApi,
                 notion_api: NotionApi):
        self.date = date
        self.free_time_list = free_time_list
        # startの降順にソートする
        self.free_time_list.sort(
            key=lambda time_range: time_range["start"], reverse=True)
        self.projects = [notion_api.find_project(project_id) for project_id in project_id_list]
        self.google_calendar_api = google_calendar_api

    def handle(self) -> list:
        """ プロジェクトを埋める """
        while len(self.free_time_list) > 0 and len(self.projects) > 0:
            self._regist_project_to_calendar()
        return self.projects

    def _regist_project_to_calendar(self) -> None:
        project = self.projects.pop()
        range = self.free_time_list.pop()

        title = project.title
        start = DatetimeObject.combine(
            self.date, TimeObject.fromisoformat(range["start"]))
        drive_project = DriveProject.create(start=start,
                                            title=title,
                                            notion_url=project.url,
                                            tasks=[], # TODO: タスクもいずれ入れる
                                            )
        self.google_calendar_api.post_schedule(schedule=drive_project)
