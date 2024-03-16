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
        fromtmatter, freetext = _partition(text)
        return Achievement(
            title=title,
            start=start,
            end=end,
            frontmatter=fromtmatter,
            text=freetext,
        )

    def get_notion_url(self) -> str|None:
        return self.frontmatter.get("notion_url")

    def in_range(self, start: datetime, end: datetime) -> bool:
        if self.end.timestamp() < start.timestamp():
            return False
        if self.start.timestamp() > end.timestamp():
            return False
        return True


def _partition(text: str) -> tuple[dict, str]:
    # frontmatterだけの場合
    if text.strip().endswith("---"):
        frontmatter = _text_to_yaml_dict(text)
        return frontmatter, ""

    frontmatter_text, _, freetext = text.partition("\n---\n")

    # frontmatterがない場合
    if not freetext:
        return {}, text.strip()

    # frontmatterとテキストどちらもある場合
    frontmatter = _text_to_yaml_dict(frontmatter_text)
    return frontmatter, freetext.strip()

def _text_to_yaml_dict(text: str) -> dict:
    frontmatter_text = text.replace("---", "").strip()
    frontmatter_text = f"---\n{frontmatter_text}\n..."
    fromtmatter = yaml.safe_load(frontmatter_text)
    return fromtmatter if isinstance(fromtmatter, dict) else {}