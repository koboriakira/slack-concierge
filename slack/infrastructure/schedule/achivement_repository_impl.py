from datetime import datetime

from domain.infrastructure.api.google_calendar_api import GoogleCalendarApi
from domain.schedule.achivement import Achievement
from domain.schedule.achivement_repository import AchivementRepository


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
            # "achievement": True,
        }
        response = self.google_cal_api.get(path="list", params=params)
        for el in response:
            print(el)
        return []
