from datetime import date as Date
from domain.infrastructure.api.google_calendar_api import GoogleCalendarApi
from domain.infrastructure.api.notion_api import NotionApi

class DailyPlanning:
    def __init__(self,
                 google_calendar_api: GoogleCalendarApi,
                 notion_api: NotionApi,
                 ):
        self.google_calendar_api = google_calendar_api
        self.notion_api = notion_api

    def handle(self, date: Date):
        pass
