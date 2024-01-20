from domain.channel.channel_type import ChannelType
from datetime import datetime as DatetimeObject
from datetime import timedelta
from datetime import date as DateObject
from typing import Optional
from dataclasses import dataclass, field
import yaml
import json
import os
from pathlib import Path
from collections.abc import Mapping


CALENDAR_CATEGORY = {
    "private": "プライベート",
    "morning": "朝の予定",
    "lunch": "昼休み",
    "evening": "夜の予定",
    "rest": "休息",
    "business": "仕事",
}

CHANNEL_CATEGORY = {
    "プライベート": ChannelType.DIARY.value,
    "朝の予定": ChannelType.DIARY.value,
    "昼休み": ChannelType.DIARY.value,
    "夜の予定": ChannelType.DIARY.value,
    "休息": ChannelType.DIARY.value,
    "仕事": ChannelType.BUSINESS.value,
}

# 逆引き用
REVERSED_CALENDAR_CATEGORY = dict(
    zip(CALENDAR_CATEGORY.values(), CALENDAR_CATEGORY.keys()))


@ dataclass(frozen=True)
class SubTask(Mapping):
    name: str
    memo: list[str] | str = field(default_factory=list)

    @ staticmethod
    def from_entity(entity: dict) -> "SubTask":
        memo = entity["memo"] if "memo" in entity else []
        if isinstance(memo, str):
            memo = [memo]
        return SubTask(
            name=entity["name"],
            memo=memo,
        )

    def get_memo(self) -> list[str]:
        if isinstance(self.memo, str):
            return [self.memo]
        return self.memo

    def to_dict(self) -> dict:
        data = {
            "name": self.name,
        }
        if len(self.memo) > 0:
            data["memo"] = self.memo
        return data

    def __getitem__(self, key):
        return self.__dict__[key]

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        return len(self.__dict__)


@ dataclass(frozen=True)
class Detail(Mapping):
    # FIXME: listにそろえる
    memo: list[str] | str = field(default_factory=list)
    sub_tasks: list[SubTask] = field(default_factory=list)

    @ staticmethod
    def from_entity(entity: dict) -> "Detail":
        memo = entity["memo"] if "memo" in entity else []
        if isinstance(memo, str):
            memo = [memo]
        sub_task_entities = entity["sub_tasks"] if "sub_tasks" in entity else [
        ]
        sub_tasks = list(map(SubTask.from_entity, sub_task_entities))
        return Detail(
            memo=memo,
            sub_tasks=sub_tasks,
        )

    def to_yaml_str(self) -> str:
        data = self.to_dict()
        if data == {}:
            return ""
        result = yaml.dump(data, allow_unicode=True)
        return result

    def to_dict(self) -> dict:
        """ 辞書データに変換。バリューが空の場合はキーを持たない特徴がある """
        data = {}
        if len(self.memo) > 0:
            data["memo"] = self.memo
        if len(self.sub_tasks) > 0:
            data["sub_tasks"] = list(
                map(lambda sub_task: sub_task.to_dict(), self.sub_tasks))
        return data

    def __getitem__(self, key):
        return self.__dict__[key]

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        return len(self.__dict__)


@ dataclass(frozen=True)
class Schedule(Mapping):
    category: str
    title: str
    start: DatetimeObject
    end: DatetimeObject
    detail: Optional[Detail] = None

    @ staticmethod
    def from_entity(entity: dict) -> "Schedule":
        detail = Detail.from_entity(
            entity["detail"]) if "detail" in entity and entity["detail"] else None
        return Schedule(
            category=entity["category"],
            title=entity["title"],
            start=DatetimeObject.fromisoformat(entity["start"]),
            end=DatetimeObject.fromisoformat(entity["end"]),
            detail=detail,
        )

    def get_memo(self) -> list[str]:
        if self.detail is None:
            return []
        if isinstance(self.detail.memo, str):
            return [self.detail.memo]
        return self.detail.memo

    def to_dict(self) -> dict:
        result = {
            "category": self.category,
            "title": self.title,
            "start": self.start.isoformat(),
            "end": self.end.isoformat(),
        }
        if self.detail is not None:
            result["detail"] = self.detail.to_dict()
        return result

    def to_arguments_for_append_calendar(self) -> dict:
        result = {
            "category": REVERSED_CALENDAR_CATEGORY[self.category],
            "title": self.title,
            "start": self.start.isoformat(),
            "end": self.end.isoformat(),
        }
        if self.detail is not None:
            result["detail"] = yaml.dump(self.detail, allow_unicode=True)
        return result

    def get_post_channel_id(self) -> str:
        return CHANNEL_CATEGORY[self.category]

    def is_in_now(self, now: DatetimeObject) -> bool:
        # 現在時刻を取得
        before_5_minutes = now - timedelta(minutes=5)

        # 直近5分以内かを判定する
        return before_5_minutes.timestamp() <= self.start.timestamp() <= now.timestamp()

    def get_first_sub_task(self) -> Optional[SubTask]:
        if len(self.sub_tasks) == 0:
            return None
        return self.sub_tasks[0]

    def to_range_text(self) -> str:
        return f"{self.formated_start}から{self.formated_end}まで"

    @ property
    def sub_tasks(self) -> list[SubTask]:
        if self.detail is None:
            return []
        return self.detail.sub_tasks

    @property
    def sub_task_names(self) -> list[str]:
        return list(map(lambda sub_task: sub_task.name, self.sub_tasks))

    @ property
    def formated_start(self) -> str:
        return self.start.strftime("%H:%M")

    @ property
    def formated_end(self) -> str:
        return self.end.strftime("%H:%M")

    def __getitem__(self, key):
        return self.__dict__[key]

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        return len(self.__dict__)


def get_schedule(date: DateObject) -> list[Schedule]:
    date_str = date.isoformat()
    directory = Path(__file__).parent.parent.parent.parent
    json_file_path = directory / f"schedule_{date_str}.json"
    if not os.path.exists(json_file_path):
        raise Exception("ファイルが存在しません")
    with open(json_file_path, "r") as f:
        entities = json.load(f)
        return list(map(Schedule.from_entity, entities))
