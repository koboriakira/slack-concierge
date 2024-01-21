from typing import Optional
import os
import logging
import requests
from domain.infrastructure.api.notion_api import NotionApi
from domain.notion.notion_page import RecipePage, NotionPage

NOTION_SECRET = os.getenv("NOTION_SECRET")

class LambdaNotionApi(NotionApi):
    def __init__(self):
        self.domain = os.environ["LAMBDA_NOTION_API_DOMAIN"]

    def list_recipes(self) -> list[RecipePage]:
        response = self._get(path="recipes")
        return [RecipePage.from_dict(page) for page in response]

    def list_projects(self, status: Optional[str] = None) -> list[NotionPage]:
        params = {}
        if status:
            params["status"] = status
        response = self._get(path="projects", params=params)
        logging.debug(response)
        return [NotionPage.from_dict(page) for page in response]

    def _get(self, path: str, params: dict = {}) -> dict:
        """ 任意のパスに対してPOSTリクエストを送る """
        url = f"{self.domain}{path}"
        logging.debug(f"get: {url} {params}")
        headers = {
            "access-token": NOTION_SECRET,
        }
        logging.debug(headers)
        response = requests.get(url, params=params, headers=headers)
        logging.debug(response)
        if response.status_code != 200:
            logging.error(f"response: {response}")
            return None
        try:
            return response.json()
        except Exception as e:
            logging.warning(e)
            return {"message": response.text}


if __name__ == "__main__":
    # python -m infrastructure.api.lambda_notion_api
    logging.basicConfig(level=logging.DEBUG)
    notion_api = LambdaNotionApi()
    response = notion_api.list_projects(status="Primary")
    print(response)
