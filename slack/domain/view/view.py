from dataclasses import dataclass
from typing import Any, Optional
import json
import logging
from domain.view.state import State
from domain.view.context import Context


@dataclass
class View:
    view: dict[str, Any]

    def get_state(self) -> State:
        if "state" not in self.view:
            return State({})
        state = self.view["state"]
        if "values" not in state:
            return State({})
        return State.from_values(state["values"])

    def get_context(self) -> Context:
        for block in self.view["blocks"]:
            if block["type"] != "context":
                continue
            if "elements" not in block:
                continue
            try:
                elements = block["elements"]
                plain_text_elements = list(
                    filter(lambda element: element["type"] == "plain_text", elements))
                plain_text_element_value = plain_text_elements[0]["text"]
                return Context.load(plain_text_element_value)
            except Exception:
                logging.exception(f"Can't get context from {block}")
                continue
        return Context(context={})
