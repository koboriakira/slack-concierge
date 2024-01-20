from domain.schedule.schedule import Schedule, Detail
from datetime import timedelta
from datetime import datetime as DatetimeObject
from typing import Optional
from domain.notion.notion_page import RecipePage


class CookDinner:
    CATEGORY = "夜の予定"
    TITLE = "夕食の準備"
    MARGIN = 45

    @classmethod
    def create(cls, start: DatetimeObject, dinner_recipe_pages: list[RecipePage] = []) -> Schedule:
        detail = None
        if dinner_recipe_pages is not None:
            memo = []
            for dinner_recipe_page in dinner_recipe_pages:
                memo.append(dinner_recipe_page.link_text)
            detail = Detail(memo=memo)

        cook_start = start.replace(hour=17, minute=0) if start.hour < 17 else start  # startが17:00より前の場合は、17:00開始に変更

        return Schedule(
            category=cls.CATEGORY,
            title=cls.TITLE,
            start=cook_start,
            end=cook_start + timedelta(minutes=cls.MARGIN),
            detail=detail,
        )
