from dataclasses import dataclass
from typing import Optional
from domain.message.message import BaseMessage

@dataclass(frozen=True)
class Messages:
    values: list[BaseMessage]

    def first(self) -> Optional[BaseMessage]:
        if len(self.values) == 0:
            return None
        return self.values[0]
