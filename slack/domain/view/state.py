from dataclasses import dataclass
import logging
from datetime import date as DateObject
from datetime import time as TimeObject
from typing import Optional


@dataclass(frozen=True)
class State:
    action_map: dict[str, dict]

    @staticmethod
    def from_values(values: dict[str, dict[str, dict]]) -> 'State':
        action_map = {}
        for value in values.values():
            for action_id, action in value.items():
                action_map[action_id] = action
        logging.debug(f"action_map: {action_map}")
        return State(action_map=action_map)

    def is_checked(self, action_id: str, value: str) -> bool:
        """ チェックボックスの結果を取得する """
        if action_id not in self.action_map:
            return False
        selected_options = self.action_map[action_id]["selected_options"]
        for option in selected_options:
            if option["value"] == value:
                return True
        return False

    def get_text_input_value(self, action_id: str) -> str:
        """ テキスト入力結果を取得する """
        return self.action_map[action_id]["value"]

    def get_multi_selected(self, action_id: str) -> list[dict[str, str]]:
        """ 複数選択の結果を取得する """
        if action_id not in self.action_map:
            return []
        selected_options = self.action_map[action_id]["selected_options"]
        return [{
            "text": option["text"]["text"],
            "value": option["value"]
        } for option in selected_options]

    def get_selected(self, action_id: str) -> dict[str, str]:
        """ 単一選択の結果を取得する """
        selected_option = self.action_map[action_id]["selected_option"]
        return {
            "text": selected_option["text"]["text"],
            "value": selected_option["value"]
        }

    def get_datepicker(self, action_id: str) -> DateObject:
        """ 日付選択の結果を取得する """
        selected_date = self.action_map[action_id]["selected_date"]
        return DateObject.fromisoformat(selected_date)

    def get_timepicker(self, action_id: str) -> TimeObject:
        """ 日付選択の結果を取得する """
        try:
            selected_time = self.action_map[action_id]["selected_time"]
            return TimeObject.fromisoformat(selected_time)
        except KeyError as e:
            logging.error(self.action_map)
            raise e

    def get_checked_options(self, action_id: str) -> list[dict[str, str]]:
        """ チェック済の要素を取得する """
        if action_id not in self.action_map:
            return []
        if "selected_options" not in self.action_map[action_id]:
            return []
        selected_options = self.action_map[action_id]["selected_options"]
        return [{"text": option["text"]["text"], "value": option["value"]} for option in selected_options]

    def get_static_select(self, action_id: str) -> Optional[tuple[str, str]]:
        """ 静的セレクトの結果を取得する。text, value の順で返す """
        selected_option = self.action_map[action_id]["selected_option"]
        if selected_option is None:
            return None
        return selected_option["text"]["text"], selected_option["value"]
