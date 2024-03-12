from unittest import TestCase
from unittest.mock import Mock

from slack.domain.music.music_repository import MusicRepository
from slack.domain.music.spotify_api import SpotifyApi
from slack.domain.music.track import Track
from slack.usecase.love_spotify_use_case import LoveSpotifyUseCase
from slack_sdk.web import WebClient

DEMO_TS = "1710086804.368969"
DEMO_TRACK_ID = "id"
DEMO_TRACK = Track(
  track_id=DEMO_TRACK_ID,
  track_name="name",
  artists=["artist"],
)
DEMO_CHANNEL_ID = "channel_id"
DEMO_THREAD_TS = "thread_ts"

class TestLoveSpotifyUseCase(TestCase):
    def setUp(self) -> None:
        # TaskRepositoryのモックを作成
        slack_bot_client = Mock(spec=WebClient)
        slack_user_client = Mock(spec=WebClient)
        music_repository = Mock(spec=MusicRepository)
        spotify_api = Mock(spec=SpotifyApi)

        self.suite = LoveSpotifyUseCase(
            slack_bot_client=slack_bot_client,
            slack_user_client=slack_user_client,
            music_repository=music_repository,
            spotify_api=spotify_api,
        )

        # Mock
        self.suite.spotify_api.find_track.return_value = DEMO_TRACK

        return super().setUp()

    def test_正常系(self) -> None:
        # When
        self.suite.execute(DEMO_TRACK_ID, DEMO_CHANNEL_ID, DEMO_THREAD_TS)

        # Then
        self.suite.spotify_api.find_track.assert_called_once_with(track_id=DEMO_TRACK_ID)
        self.suite.spotify_api.love_track.assert_called_once_with(track_id=DEMO_TRACK_ID)
        self.suite.music_repository.save.assert_called_once()
