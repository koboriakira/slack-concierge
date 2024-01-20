from domain.schedule.schedule import Schedule, Detail
from datetime import timedelta
from datetime import datetime as DatetimeObject
from typing import Optional


class Dinner:
    CATEGORY = "夜の予定"
    TITLE = "夕食"
    MARGIN = 60

    @classmethod
    def create(cls, start: DatetimeObject, dinner_recipe_pages: list = []) -> Schedule:
        detail = None
        if dinner_recipe_pages is not None:
            memo = []
            for dinner_recipe_page in dinner_recipe_pages:
                memo.append(dinner_recipe_page.link_text)
            detail = Detail(memo=memo)

        end = start + timedelta(minutes=cls.MARGIN)

        return Schedule(
            category=cls.CATEGORY,
            title=cls.TITLE,
            start=start,
            end=end,
            detail=detail
        )
