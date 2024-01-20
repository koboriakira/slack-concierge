from domain.infrastructure.api.google_calendar_api import GoogleCalendarApi
from domain.schedule.schedule import Schedule
import logging
import requests
from datetime import date as DateObject
from datetime import datetime as DatetimeObject
from typing import Optional
import os
import yaml


class LambdaGoogleCalendarApi(GoogleCalendarApi):
    def __init__(self):
        self.domain = os.environ["LAMBDA_GOOGLE_CALENDAR_API_DOMAIN"]
        self.access_token = os.environ["GAS_DEPLOY_ID"]

    def get_gas_calendar(self,
                         date: DateObject) -> list[dict]:
        return []
        params = {
            "start_date": date.isoformat(),
            "end_date": date.isoformat(),
        }
        headers = {
            "access-token": self.access_token,
        }
        return requests.get(url=self.domain, params=params, headers=headers).json()

    def get_gas_calendar_achievements(self,
                                      date: DateObject) -> list[dict]:
        return []
        params = {
            "start_date": date.isoformat(),
            "end_date": date.isoformat(),
            "achievement": True,
        }
        return requests.get(url=self.domain, params=params).json()

    def post_schedule(self, schedule: Schedule) -> dict:
        return {}
        return self._post_gas_calendar(
            start=schedule.start,
            end=schedule.end,
            category=schedule.category,
            title=schedule.title,
            detail=schedule.detail.to_yaml_str() if schedule.detail is not None else None,
        )

    def delete_gas_calendar(self,
                            date: DateObject,
                            category: str,
                            title: str) -> dict:
        return {}
        params = {
            "date": date.isoformat(),
            "category": category,
            "title": title,
        }
        return requests.delete(url=self.domain, params=params).json()

    def _post_gas_calendar(self,
                          start: DatetimeObject,
                          end: DatetimeObject,
                          category: str,
                          title: str,
                          detail: Optional[str] = None) -> dict:
        """ カレンダーを追加する """
        data = {
            "category": category,
            "title": title,
            "start": start.isoformat(),
            "end": end.isoformat(),
            "detail": detail,
        }
        logging.debug(f"post_gas_calendar: {data}")
        response = requests.post(url=self.domain, json=data)
        logging.debug(f"post_gas_calendar: status_code={response.status_code}")
        logging.debug(response.json())
        return response.json()

def dump_yaml(value: dict) -> str:
    return yaml.dump(value, allow_unicode=True)
