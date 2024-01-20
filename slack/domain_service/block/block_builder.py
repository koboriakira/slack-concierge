from dataclasses import dataclass, field
from typing import Optional
import json
import logging



@dataclass(frozen=True)
class BlockBuilder:
    blocks: list[dict] = field(default_factory=list)

    def add_checkboxes(self, action_id: str, header: str, options: list[dict[str, str]]) -> 'BlockBuilder':
        """チェックボックスを追加する

        Args:
            action_id (str):
            header (str):
            options (list[dict[str, str]]): text, valueをキーにすること

        Returns:
            BlockBuilder:
        """
        accessory_options = [{
            "text": {
                "type": "mrkdwn",
                "text": option["text"]
            },
            "value": option["value"]
        } for option in options]

        block = {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": header
            },
            "accessory": {
                "type": "checkboxes",
                "options": accessory_options,
                "action_id": action_id
            }
        }
        return BlockBuilder(blocks=self.blocks + [block])

    def add_checkboxes_action(self, action_id: str, options: list[dict[str, str]]) -> 'BlockBuilder':
        """チェックボックスを追加する (アクション用)

        Args:
            action_id (str):
            header (str):
            options (list[dict[str, str]]): text, description, valueをキーにすること

        Returns:
            BlockBuilder:
        """
        element_options = []
        for option in options:
            element_option = {
                "text": {
                    "type": "plain_text",
                    "text": option["text"]
                },
                "value": option["value"]
            }
            if "description" in option:
                element_option["description"] = {
                    "type": "mrkdwn",
                    "text": option["description"]
                }
            element_options.append(element_option)

        block = {
            "type": "actions",
            "elements": [
                {
                    "type": "checkboxes",
                    "options": element_options,
                    "action_id": action_id
                }
            ],
        }
        return BlockBuilder(blocks=self.blocks + [block])

    def add_plain_text_input(self, action_id: str, label: str, multiline: bool = False, optional=False) -> 'BlockBuilder':
        block = {
            "type": "input",
            "element": {
                "type": "plain_text_input",
                "multiline": multiline,
                "action_id": action_id
            },
            "label": {
                "type": "plain_text",
                "text": label,
            },
            "optional": optional
        }
        return BlockBuilder(blocks=self.blocks + [block])

    def add_multi_static_select(self, action_id: str, options: list[dict[str, str]], label: str = "選択", placeholder: str = "選択してください", optional: bool = False) -> 'BlockBuilder':
        return self.add_static_select(action_id=action_id, options=options, label=label, placeholder=placeholder, is_multi=True, optional=optional)

    def add_static_select(self, action_id: str, options: list[dict[str, str]], label: str = "選択", placeholder: str = "選択してください", is_multi: bool = False, optional: bool = False) -> 'BlockBuilder':
        element_options = [{
            "text": {
                "type": "plain_text",
                "text": option["text"]
            },
            "value": option["value"]
        } for option in options]
        block = {
            "type": "input",
            "element": {
                "type": "multi_static_select" if is_multi else "static_select",
                "placeholder": {
                    "type": "plain_text",
                    "text": placeholder
                },
                "options": element_options,
                "action_id": action_id
            },
            "label": {
                "type": "plain_text",
                "text": label
            },
            "optional": optional
        }
        return BlockBuilder(blocks=self.blocks + [block])

    def add_datepicker(self, action_id: str, header: str, placeholder: str, initial_date: Optional[str] = None) -> 'BlockBuilder':
        accessory = {
            "type": "datepicker",
            "action_id": action_id,
            "initial_date": initial_date,
            "placeholder": {
                "type": "plain_text",
                "text": placeholder
            }
        }
        block = {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": header
            },
            "accessory": accessory
        }
        return BlockBuilder(blocks=self.blocks + [block])

    def add_timepicker(self, action_id: str, placeholder: str, initial_time: Optional[str] = None, label: Optional[str] = None) -> 'BlockBuilder':
        element = {
            "type": "timepicker",
            "initial_time": initial_time,
            "placeholder": {
                "type": "plain_text",
                "text": placeholder,
            },
            "action_id": action_id
        }
        block = {
            "type": "input",
            "element": element,
        }
        if label is not None:
            block["label"] = {
                "type": "plain_text",
                "text": label,
            }
        return BlockBuilder(blocks=self.blocks + [block])

    def add_mrkdwn_section(self, text: str) -> 'BlockBuilder':
        block = {
            "type": "section",
            "block_id": "mrkdwn-section",
            "text": {
                "type": "mrkdwn",
                "text": text
            }
        }
        return BlockBuilder(blocks=self.blocks + [block])

    def add_divider(self) -> 'BlockBuilder':
        block = {
            "type": "divider"
        }
        return BlockBuilder(blocks=self.blocks + [block])

    def add_button_action(self, action_id: str, text: str, value: str, style: str = "default") -> 'BlockBuilder':
        element = {
            "type": "button",
            "text": {
                "type": "plain_text",
                "text": text
            },
            "style": style,
            "value": value,
            "action_id": action_id,
        }

        block = {
            "type": "actions",
            "elements": [element]
        }
        return BlockBuilder(blocks=self.blocks + [block])

    # 以下、ちょっと勘違いして作ったメソッドかも。

    def add_section(self, text: str) -> 'BlockBuilder':
        section_block = {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": text
            },
        }
        return BlockBuilder(blocks=self.blocks + [section_block])

    # def add_blocks_for_append_comment(self, page_id: str, page_title: str) -> 'BlockBuilder':
    #     """ Notionのコメント追加のブロックを作成する """
    #     builder = self.add_section(text=page_title)
    #     return builder.add_action_button(
    #         action_type=InteractiveActionType.APPEND_COMMENT,
    #         title="コメントを追加",
    #         value=page_id
    #     )

    # def add_action_button(self, action_type: InteractiveActionType, title: str, value: str, style: str = "primary") -> 'BlockBuilder':
    #     element = {
    #         "type": "button",
    #         "text": {
    #             "type": "plain_text",
    #             "text": title
    #         },
    #         "style": style,
    #         "value": value
    #     }

    #     blocks = self.blocks
    #     action_blocks = [
    #         block for block in blocks if block["type"] == "actions"]
    #     if len(action_blocks) > 0:
    #         action_blocks[0]["elements"].append(element)
    #         return BlockBuilder(blocks=blocks)
    #     action_block = {
    #         "type": "actions",
    #         "block_id": action_type.value,
    #         "elements": [
    #             {
    #                 "type": "button",
    #                 "text": {
    #                     "type": "plain_text",
    #                     "text": title
    #                 },
    #                 "style": style,
    #                 "value": value
    #             },
    #         ]
    #     }
    #     return BlockBuilder(blocks=self.blocks + [action_block])

    def add_context(self, text: str | dict) -> 'BlockBuilder':
        context_block = {
            "type": "context",
            "elements": [
                {
                    "type": "plain_text",
                    "text": json.dumps(text, ensure_ascii=False) if isinstance(text, dict) else text
                }
            ]
        }
        return BlockBuilder(blocks=self.blocks + [context_block])

    def build(self) -> list[dict]:
        return self.blocks
