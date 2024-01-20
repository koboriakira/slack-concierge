from dataclasses import dataclass
from datetime import date as DateObject
from typing import Optional
import json


@dataclass(frozen=True)
class Context:
    context: dict[str, dict]

    @staticmethod
    def of(params: dict = {}, channel_id: Optional[str] = None, thread_ts: Optional[str] = None, date: Optional[DateObject] = None) -> 'Context':
        context = {}
        if channel_id is not None:
            context["channel_id"] = channel_id
        if thread_ts is not None:
            context["thread_ts"] = thread_ts
        if date is not None:
            context["date"] = date.isoformat()
        context.update(params)
        return Context(context=context)

    @staticmethod
    def load(json_str: str) -> 'Context':
        return Context(context=json.loads(json_str))

    def get_string(self, key: str) -> Optional[str]:
        return self.context.get(key)

    @property
    def channel_id(self) -> Optional[str]:
        return self.context.get("channel_id")

    @property
    def thread_ts(self) -> Optional[str]:
        return self.context.get("thread_ts")

    @property
    def date(self) -> Optional[DateObject]:
        if "date" not in self.context:
            return None
        return DateObject.fromisoformat(self.context["date"])
