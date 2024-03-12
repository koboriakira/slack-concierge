import os

import requests
from slack.domain.music.spotify_api import SpotifyApi

from domain.music.track import Track
from util.custom_logging import get_logger

logger = get_logger(__name__)

BASE_URL = "https://5e2lmuxy04.execute-api.ap-northeast-1.amazonaws.com/v1/"

class LambdaSpotifyApi(SpotifyApi):
    def __init__(self):
        self.access_token = os.environ["SPOTIFY_CLIENT_SECRET"]

    def find_track(self, track_id: str) -> Track:
        """ Spotifyのトラックの情報を取得する """
        url = BASE_URL + f"track/{track_id}"
        headers = {
            "access-token": self.access_token,
        }
        logger.debug(f"url={url}, headers={headers}")
        response = requests.get(url=url, headers=headers)
        logger.debug(f"love_track: status_code={response.status_code}")
        if response.status_code != 200:
            raise Exception(f"status_code={response.status_code}, data={response.text}")
        response_json = response.json()
        logger.debug(response_json)
        track_info = response_json["data"]
        return Track.from_spotify_track_info(track_info)

    def love_track(self, track_id: str) -> bool:
        """ Spotifyのトラックを「お気に入りの曲」ライブラリに追加する """
        url = BASE_URL + f"track/{track_id}/love"
        headers = {
            "access-token": self.access_token,
        }
        logger.debug(f"url={url}, headers={headers}")
        response = requests.post(url=url, headers=headers)
        logger.debug(f"love_track: status_code={response.status_code}")
        if response.status_code != 200:
            raise Exception(f"status_code={response.status_code}, data={response.text}")
        response_json = response.json()
        logger.debug(response_json)
        return response_json["status"] == "SUCCESS"

if __name__ == "__main__":
    # python -m infrastructure.api.lambda_spotify_api
    print(LambdaSpotifyApi().love_track(track_id="4dbZObCjUs95HtmEHfKbnU"))
    # print(LambdaSpotifyApi().find_track(track_id="5Ee2RlDLl8JctEb7iUzdHk"))
