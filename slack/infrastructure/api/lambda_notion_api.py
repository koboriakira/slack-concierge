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
        return self._post(url=url, data=data)

    def create_webclip_page(self,
                            url: str,
                            title: str,
                            summary: str,
                            tags: list[str],
                            text: str,
                            status: Optional[str] = None,
                            cover: Optional[str] = None,
                            ) -> dict:
        url = f"{self.domain}webclip"
        data = {
            "url": url,
            "title": title,
            "summary": summary,
            "tags": tags,
            "text": text,
        }
        if status:
            data["status"] = status
        if cover:
            data["cover"] = cover
        return self._post(url=url, data=data)


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

    def _post(self, url: str, data: dict) -> dict:
        headers = {
            "access-token": NOTION_SECRET,
        }
        respone = requests.post(url=url, headers=headers, json=data)
        logging.debug(respone)
        if respone.status_code != 200:
            raise Exception(f"status_code: {respone.status_code}, message: {respone.text}")
        response_json = respone.json()
        return response_json["data"]


if __name__ == "__main__":
    # python -m infrastructure.api.lambda_notion_api
    logging.basicConfig(level=logging.DEBUG)
    notion_api = LambdaNotionApi()

    # print(notion_api.find_project(project_id="b95d7eb173f9436893c2240650323b30"))

    # print(notion_api.list_recipes())

    # print(notion_api.create_track_page(
    #     track_name="Plastic Love",
    #     artists=["Friday Night Plans"],
    #     spotify_url="https://open.spotify.com/intl-ja/track/2qxTmEfGbBGMSJrwu4Ez1v?si=c4750c498ac14c7c",
    #     release_date=Date(2024, 1, 22)
    # ))


# {
#     "url": "https://note.com/koboriakira/n/ne14eaa1c50d2?sub_rt=share_pb",
#     "title": "東京女子プロレスのベストバウト29選 (2023)｜コボリアキラ",
#     "summary": "2023年にファンとなった筆者が、その年の東京女子プロレスのベストバウト29試合について熱く語る記事。筆者は東京女子プロレスの魔法にかけられたように熱中し、試合や選手への情熱的な愛情を語りつくす。多くの試合が印象的だったが、特に強調されるのは、選手たちのエネルギッシュなパフォーマンス、印象的なシーン、そしてファンの心を捉えるストーリーテリングである。筆者は、東京女子プロレスの独特の魅力を「東京女子プロレスだから好き」という言葉で表現し、彼らのプロレスへの深い愛情を読者に伝えている。",
#     "cover": "https://assets.st-note.com/production/uploads/images/126014735/rectangle_large_type_2_a12108f8a67248cc00e888924d6a08dc.jpeg?fit=bounds&quality=85&width=1280",
#     "tags": ["東京女子プロレス", "プロレス", "ベストバウト", "2023"],
#     "status": "Inbox",
#     "text": "テスト"
# }

    # print(notion_api.create_webclip_page(
    #     url="https://note.com/koboriakira/n/ne14eaa1c50d2?sub_rt=share_pb",
    #     title="東京女子プロレスのベストバウト29選 (2023)｜コボリアキラ",
    #     summary="2023年にファンとなった筆者が、その年の東京女子プロレスのベストバウト29試合について熱く語る記事。筆者は東京女子プロレスの魔法にかけられたように熱中し、試合や選手への情熱的な愛情を語りつくす。多くの試合が印象的だったが、特に強調されるのは、選手たちのエネルギッシュなパフォーマンス、印象的なシーン、そしてファンの心を捉えるストーリーテリングである。筆者は、東京女子プロレスの独特の魅力を「東京女子プロレスだから好き」という言葉で表現し、彼らのプロレスへの深い愛情を読者に伝えている。",
    #     cover="https://assets.st-note.com/production/uploads/images/126014735/rectangle_large_type_2_a12108f8a67248cc00e888924d6a08dc.jpeg?fit=bounds&quality=85&width=1280",
    #     tags=["東京女子プロレス", "プロレス", "ベストバウト", "2023"],
    #     status="Inbox",
    #     text="テスト"
    # ))
