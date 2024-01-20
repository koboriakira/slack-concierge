import json


class NotionPage:
    id: str
    url: str
    title: str

    def __init__(self, id: str, url: str, title: str):
        self.id = id
        self.url = url
        self.title = title

    def dump(self) -> str:
        return json.dumps({
            "id": self.id,
            "url": self.url,
            "title": self.title
        }, ensure_ascii=False)

    def load(json_str: str) -> "NotionPage":
        json_dict = json.loads(json_str)
        return NotionPage(
            id=json_dict["id"],
            url=json_dict["url"],
            title=json_dict["title"]
        )

    def from_dict(params: dict) -> "NotionPage":
        return NotionPage(
            id=params["id"],
            url=params["url"],
            title=params["title"]
        )

    @property
    def link_text(self) -> str:
        return f"<{self.url}|{self.title}>"


class ProjectPage(NotionPage):
    status: str

    def __init__(self, id: str, url: str, title: str, status: str):
        super().__init__(id, url, title)
        self.status = status

    def from_dict(params: dict) -> "ProjectPage":
        return ProjectPage(
            id=params["id"],
            url=params["url"],
            title=params["title"],
            status=params["status"]
        )


class RecipePage(NotionPage):
    status: str

    def __init__(self, id: str, url: str, title: str, ingredients: list[str], meal_categories: list[str], status: str):
        super().__init__(id, url, title)
        self.ingredients = ingredients
        self.meal_categories = meal_categories
        self.status = status

    def from_dict(params: dict) -> "RecipePage":
        return RecipePage(
            id=params["id"],
            url=params["url"],
            title=params["title"],
            ingredients=params["ingredients"],
            meal_categories=params["meal_categories"],
            status=params["status"],
        )
