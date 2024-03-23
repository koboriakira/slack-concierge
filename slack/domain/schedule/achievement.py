from dataclasses import dataclass, field
from datetime import datetime, timedelta

import yaml


@dataclass(frozen=True)
class Achievement:
    title: str
    start: datetime
    end: datetime
    frontmatter: dict = field(default_factory=dict)
    text: str = ""

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

    @staticmethod
    def five_minutes(title: str, start: datetime) -> "Achievement":
        return Achievement(title=title, start=start, end=start + timedelta(minutes=5))


    @staticmethod
    def wakeup(wakeup_at: datetime) -> "Achievement":
        return Achievement.five_minutes(title="起床", start=wakeup_at)

    @staticmethod
    def sleep(sleep_at: datetime) -> "Achievement":
        return Achievement.five_minutes(title="就寝", start=sleep_at)

    @staticmethod
    def go_out(go_out_at: datetime) -> "Achievement":
        return Achievement.five_minutes(title="外出", start=go_out_at)

    @staticmethod
    def come_home(come_home_at: datetime) -> "Achievement":
        return Achievement.five_minutes(title="帰宅", start=come_home_at)


    def description(self) -> str:
        if self.frontmatter != {}:
            frontmatter_text = "\n".join([f"{k}: {v}" for k, v in self.frontmatter.items()])
            return f"---\n{frontmatter_text}\n---\n\n{self.text}"
        return ""

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
