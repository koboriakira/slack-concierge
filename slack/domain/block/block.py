from dataclasses import dataclass
from typing import Optional
from domain.view.context import Context
from util.custom_logging import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class Block():
    type: str
    block_id: Optional[str]
    elements: list[str]

    def to_context(self) -> Context:
        try:
            plain_text_elements = list(
                filter(lambda element: element["type"] == "plain_text", self.elements))
            plain_text_element_value = plain_text_elements[0]["text"]
            return Context.load(plain_text_element_value)
        except Exception:
            raise Exception(f"Can't get context. elements: {self.elements}")

    @staticmethod
    def from_dict(block: dict) -> 'Block':
        type = block["type"]
        block_id = block.get("block_id")
        elements = block.get("elements", [])
        return Block(type=type, block_id=block_id, elements=elements)
