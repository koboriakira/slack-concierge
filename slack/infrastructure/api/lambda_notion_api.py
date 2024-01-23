from typing import Optional
from datetime import date as Date
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
        data = response["data"]
        return [RecipePage.from_dict(page) for page in data]

    def list_projects(self, status: Optional[str] = None) -> list[NotionPage]:
        params = {}
        if status:
            params["status"] = status
        response = self._get(path="projects", params=params)
        data = response["data"]
        return [NotionPage.from_dict(page) for page in data]

    def find_project(self, project_id: str) -> NotionPage:
        response = self._get(path=f"projects/{project_id}")
        logging.debug(response)
        data = response["data"]
        return NotionPage.from_dict(data)

    def create_track_page(self, track_name: str,
                                artists: list[str],
                                spotify_url: Optional[str] = None,
                                cover_url: Optional[str] = None,
                                release_date: Optional[Date] = None,) -> dict:
        url = f"{self.domain}music"
        headers = {
            "access-token": NOTION_SECRET,
        }
        data = {
            "track_name": track_name,
            "artists": artists,
        }
        if spotify_url:
            data["spotify_url"] = spotify_url
        if cover_url:
            data["cover_url"] = cover_url
        if release_date:
            data["release_date"] = release_date.strftime("%Y-%m-%d")
        respone = requests.post(url=url, headers=headers, json=data)
        logging.debug(respone)
        if respone.status_code != 200:
            raise Exception(f"status_code: {respone.status_code}, message: {respone.text}")
        response_json = respone.json()
        return response_json["data"]

    def _get(self, path: str, params: dict = {}) -> dict:
        """ 任意のパスに対してPOSTリクエストを送る """
        url = f"{self.domain}{path}"
        headers = {
            "access-token": NOTION_SECRET,
        }
        response = requests.get(url, params=params, headers=headers)
        logging.debug(response)
        if response.status_code != 200:
            raise Exception(f"status_code: {response.status_code}, message: {response.text}")
        return response.json()


if __name__ == "__main__":
    # python -m infrastructure.api.lambda_notion_api
    logging.basicConfig(level=logging.DEBUG)
    notion_api = LambdaNotionApi()

    # print(notion_api.find_project(project_id="b95d7eb173f9436893c2240650323b30"))

    # print(notion_api.list_recipes())

    print(notion_api.create_track_page(
        track_name="Plastic Love",
        artists=["Friday Night Plans"],
        spotify_url="https://open.spotify.com/intl-ja/track/2qxTmEfGbBGMSJrwu4Ez1v?si=c4750c498ac14c7c",
        release_date=Date(2024, 1, 22)
    ))
