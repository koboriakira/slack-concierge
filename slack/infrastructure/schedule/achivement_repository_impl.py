from datetime import datetime

from domain.infrastructure.api.google_calendar_api import GoogleCalendarApi
from domain.schedule.achivement import Achievement
from domain.schedule.achivement_repository import AchivementRepository
from util.datetime import JST


class AchivementRepositoryImpl(AchivementRepository):
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
        for el in response:
            print(el)
        return [Achievement.generate(
            title=el["title"],
            start=datetime.fromisoformat(el["start"]),
            end=datetime.fromisoformat(el["end"]),
            text=el["description"],
        ) for el in response]

if __name__ == "__main__":
    # python -m slack.infrastructure.schedule.achivement_repository_impl
    repository = AchivementRepositoryImpl()
    response = repository.search(
        start=datetime(2024, 3, 15, tzinfo=JST),
        end=datetime(2024, 3, 16, tzinfo=JST))
    print(response)
