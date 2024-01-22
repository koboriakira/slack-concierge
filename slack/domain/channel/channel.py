from dataclasses import dataclass, field

@dataclass(frozen=True)
class Channel:
    id: str
    name: str

    @staticmethod
    def from_entity(entity: dict) -> "Channel":
        return Channel(
            id=entity["id"],
            name=entity["name"],
        )
