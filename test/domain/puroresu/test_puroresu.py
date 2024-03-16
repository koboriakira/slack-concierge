from datetime import datetime

import pytest
from slack.domain.puroresu.puroresu import _get_api_url

DUMMY_TITLE = "ダミータイトル"
DUMMY_START_DATETIME = datetime(2024, 3, 16, 11, 0, 0)
DUMMY_END_DATETIME = datetime(2024, 3, 16, 13, 0, 0)



@pytest.mark.parametrize(
    [
        "input",
        "expected"
    ],
    [
        pytest.param(
            "https://www.wrestle-universe.com/ja/lives/jwm4emnTj8TmGvnUH57mDp",
            "https://api.wrestle-universe.com/v1/events/jwm4emnTj8TmGvnUH57mDp?al=ja",
            id="lives"
        ),
        pytest.param(
            "https://www.wrestle-universe.com/ja/videos/oEW1x7GoSZ5wFUqZnVoYzX",
            "https://api.wrestle-universe.com/v1/videoEpisodes/oEW1x7GoSZ5wFUqZnVoYzX?al=ja",
            id="videos"
        )
    ],
)
def test_get_api_url(input:str, expected: str) -> None:
    assert _get_api_url(input) == expected
