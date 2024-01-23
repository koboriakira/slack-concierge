from datetime import date as Date
from slack_sdk import WebClient
from domain.infrastructure.api.notion_api import NotionApi
from domain.infrastructure.api.spotify_api import SpotifyApi
import logging

class LoveSpotifyTrack:
    def __init__(self, client: WebClient, notion_api: NotionApi, spotify_api: SpotifyApi) -> None:
        self.client = client
        self.notion_api = notion_api
        self.spotify_api = spotify_api

    def handle(self, track_id: str, channel_id: str, thread_ts: str):
        track_info = self.spotify_api.find_track(track_id=track_id)
        track_id = track_info["id"]
        track_name = track_info["name"]
        artists = track_info["artists"]
        spotify_url = track_info["spotify_url"]
        cover_url = track_info["cover_url"]
        release_date = Date.fromisoformat(track_info["release_date"]) if track_info["release_date"] else None

        # Reactionのスタンプをつける
        self.client.reactions_add(
            channel=channel_id,
            name="heart",
            timestamp=thread_ts,
        )

        # Spotify上で「いいね」する
        self.spotify_api.love_track(track_id=track_id)

        # Notion APIにページ作成する
        page = self.notion_api.create_track_page(
            track_name=track_name,
            artists=artists,
            spotify_url=spotify_url,
            cover_url=cover_url,
            release_date=release_date,
        )
        page_url = page["url"]

        # Slackにメッセージを送信する
        self.client.chat_postMessage(
            channel=channel_id,
            thread_ts=thread_ts,
            text=f"いいねしました！\n{page_url}",
        )

if __name__ == "__main__":
    # python -m usecase.love_spotify_track
    import os
    from infrastructure.api.lambda_notion_api import LambdaNotionApi
    from infrastructure.api.lambda_spotify_api import LambdaSpotifyApi
    logging.basicConfig(level=logging.DEBUG)
    love_spotify_track = LoveSpotifyTrack(
        original_client=WebClient(token=os.environ["SLACK_BOT_TOKEN"]),
        notion_api=LambdaNotionApi(),
        spotify_api=LambdaSpotifyApi(),
    )
    love_spotify_track.handle(track_id="2qxTmEfGbBGMSJrwu4Ez1v")
