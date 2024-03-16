from dataclasses import dataclass
from datetime import datetime

import yaml


@dataclass(frozen=True)
class Achievement:
    title: str
    start: datetime
    end: datetime
    frontmatter: dict
    text: str

    @staticmethod
    def generate(title: str, start: datetime, end: datetime, text: str) -> "Achievement":
        frontmatter_text, _, freetext = text.partition("\n---\n")
        fromtmatter = yaml.safe_load(frontmatter_text)
        return Achievement(
            title=title,
            start=start,
            end=end,
            frontmatter=fromtmatter,
            text=freetext,
        )
