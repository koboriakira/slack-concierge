from enum import Enum


class UserKind(Enum):
    KOBORI_AKIRA = "U04PQMBCFNE"
    BOT_ARIKA = "U057ACF9ERL"
    UNKNOWN = "UNKNOWN"

    def mention(self) -> str:
        return f"<@{self.value}>"
