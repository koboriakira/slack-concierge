from datetime import datetime

from domain.infrastructure.api.google_calendar_api import GoogleCalendarApi
from domain.schedule.achievement import Achievement
from domain.schedule.achievement_repository import AchievementRepository
from util.datetime import JST


class AchievementRepositoryImpl(AchievementRepository):
    def __init__(
            self,
            google_cal_api: GoogleCalendarApi|None=None) -> None:
        from infrastructure.api.lambda_google_calendar_api import LambdaGoogleCalendarApi
        self.google_cal_api = google_cal_api or LambdaGoogleCalendarApi()

    def search(self, start: datetime, end: datetime) -> list[Achievement]:
        params = {
            "start_date": start.date().isoformat(),
            "end_date": end.date().isoformat(),
            "achievement": True,
        }
        response = self.google_cal_api.get(path="list", params=params)
        achievements = [Achievement.generate(
            title=el["title"],
            start=datetime.fromisoformat(el["start"]),
            end=datetime.fromisoformat(el["end"]),
            text=el["description"],
        ) for el in response]
        return [achievement for achievement in achievements if achievement.in_range(start, end)]

    def save(self, achivement: Achievement) -> None:
        self.google_cal_api.post_gas_calendar(
            category="実績",
            title=achivement.title,
            start=achivement.start,
            end=achivement.end,
            detail=achivement.description(),
        )



if __name__ == "__main__":
    # python -m slack.infrastructure.schedule.achievement_repository_impl
    repository = AchievementRepositoryImpl()
    response = repository.search(
        start=datetime(2024, 3, 15, 16, 15, tzinfo=JST),
        end=datetime(2024, 3, 15, 17, 15, tzinfo=JST))
    for el in response:
        print(el.title, el.start.isoformat())
