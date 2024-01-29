from dataclasses import dataclass
from typing import Optional
from util.custom_logging import get_logger
from domain.block.block import Block
from domain.view.context import Context

logger = get_logger(__name__)


@dataclass(frozen=True)
class Blocks:
    values: list[Block]

    def get_context(self) -> Optional[Context]:
        for block in self.values:
            if block.type == "context":
                return block.to_context()
        return None

    @staticmethod
    def from_values(values: list[dict]) -> 'Blocks':
        return Blocks(values=list(map(Block.from_dict, values)))
