from dataclasses import dataclass, field
import logging
from typing import Optional
import json



@dataclass(frozen=True)
class ViewBuilder:
    callback_id: Optional[str] = None
    title: Optional[str] = None
    submit_label: Optional[str] = None
    blocks: Optional[list[dict]] = None

    def add_callback_id(self, callback_id: str) -> 'ViewBuilder':
        return ViewBuilder(callback_id=self.callback_id, title=self.title, submit_label=self.submit_label, blocks=self.blocks)

    def add_title(self, title: str) -> 'ViewBuilder':
        return ViewBuilder(callback_id=self.callback_id, title=title, submit_label=self.submit_label, blocks=self.blocks)

    def add_submit_label(self, submit_label: str) -> 'ViewBuilder':
        return ViewBuilder(callback_id=self.callback_id, title=self.title, submit_label=submit_label, blocks=self.blocks)

    def add_blocks(self, blocks: list[dict]) -> 'ViewBuilder':
        return ViewBuilder(callback_id=self.callback_id, title=self.title, submit_label=self.submit_label, blocks=blocks)

    def build(self) -> dict:
        return {
            "type": "modal",
            "callback_id": self.callback_id,
            "title": {
                "type": "plain_text",
                "text": self.title if self.title is not None else "タイトル",
            },
            "submit": {
                "type": "plain_text",
                "text": self.submit_label if self.submit_label is not None else "Submit",
            },
            "blocks": self.blocks,
        }
