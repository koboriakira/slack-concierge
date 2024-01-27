from domain.infrastructure.api.google_calendar_api import GoogleCalendarApi
from domain.schedule.schedule import Schedule
import logging
import requests
from datetime import date as DateObject
from datetime import datetime as DatetimeObject
from typing import Optional
import os
import yaml
import json

class LambdaGoogleCalendarApi(GoogleCalendarApi):
    def __init__(self):
        self.domain = os.environ["LAMBDA_GOOGLE_CALENDAR_API_DOMAIN"]
        self.access_token = "Bearer " + os.environ["GAS_DEPLOY_ID"]

    def get_gas_calendar(self,
                         date: DateObject) -> list[dict]:
        url = self.domain + "list"
        params = {
            "start_date": date.isoformat(),
            "end_date": date.isoformat(),
        }
        headers = {
            "Accept": "application/json",
            "access-token": self.access_token,
        }
        response = requests.get(url=url, params=params, headers=headers)
        logging.debug(f"get_gas_calendar: status_code={response.status_code}")
        return response.json()

    def get_current_schedules(self) -> list[dict]:
        """ 直近のスケジュールを取得する。デフォルトで5分先 """
        url = self.domain + "next_schedules"
        headers = {
            "Accept": "application/json",
            "access-token": self.access_token,
        }
        response = requests.get(url=url, headers=headers)
        logging.debug(f"post_gas_calendar: status_code={response.status_code}")
        response_json = response.json()
        if isinstance(response_json, str):
            response_json = json.loads(response_json)
        logging.debug(f"post_gas_calendar: response={response_json}")
        return response_json

    def get_gas_calendar_achievements(self,
                                      date: DateObject) -> list[dict]:
        raise NotImplementedError
        # params = {
        #     "start_date": date.isoformat(),
        #     "end_date": date.isoformat(),
        #     "achievement": True,
        # }
        # response = requests.get(url=self.domain, params=params)
        # logging.debug(f"get_gas_calendar_achievements: status_code={response.status_code}")
        # return response.json()

    def post_schedule(self, schedule: Schedule) -> bool:
        return self.post_gas_calendar(
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

    def post_gas_calendar(self,
                          start: DatetimeObject,
                          end: DatetimeObject,
                          category: str,
                          title: str,
                          detail: Optional[str] = None) -> bool:
        """ カレンダーを追加する """
        url = self.domain + "schedule"
        data = {
            "category": category,
            "title": title,
            "start": start.isoformat(),
            "end": end.isoformat(),
            "detail": detail,
        }
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "access-token": self.access_token,
        }
        logging.debug(f"post_gas_calendar: {data}")
        response = requests.post(url=url, json=data, headers=headers)
        logging.debug(f"post_gas_calendar: status_code={response.status_code}")
        response_json = response.json()
        if isinstance(response_json, str):
            response_json = json.loads(response_json)
        logging.debug(f"post_gas_calendar: response={response_json}")
        return "status" in response_json and response_json["status"] == "success"

def dump_yaml(value: dict) -> str:
    return yaml.dump(value, allow_unicode=True)

if __name__ == "__main__":
    # python -m infrastructure.api.lambda_google_calendar_api
    logging.basicConfig(level=logging.DEBUG)
    api = LambdaGoogleCalendarApi()
    # logging.info(api.get_gas_calendar(date=DateObject(2024, 1, 12)))
    # logging.info(api.post_gas_calendar(
    #     start=DatetimeObject(2024, 1, 12, 10, 0),
    #     end=DatetimeObject(2024, 1, 12, 11, 0),
    #     category="プライベート",
    #     title="test",
    #     detail=""
    # ))
    print(api.get_current_schedules())
