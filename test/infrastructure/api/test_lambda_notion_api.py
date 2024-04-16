from unittest import TestCase
from unittest.mock import Mock

import requests

from domain.infrastructure.api.notion_api import NotionApiError
from infrastructure.api.lambda_notion_api import LambdaNotionApi
from infrastructure.api.request_wrapper import RequestWrapper


class TestLambdaNotionApi(TestCase):
    def setUp(self) -> None:
        self.suite = LambdaNotionApi(request_wrapper=Mock(spec=RequestWrapper))

    def test_post実行_ただしいJSONオブジェクトが返却されたときは正常に処理される(self):
        # Given
        # request_wrapperはjson型かつ"data"キーを持つレスポンスを返す
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": [{"foo": "bar"}]}
        self.suite._request_wrapper.post.return_value = mock_response

        # When
        actual = self.suite.post(path="dummy", data={"foo": "bar"})

        # Then
        self.assertEqual(actual, [{"foo": "bar"}])

    def test_post実行_400エラーが返却されたときNotionApiErrorがraiseされる(self):
        # Given
        # request_wrapperがstatus_code=400のHttpErrorをraiseする
        self.suite._request_wrapper.post.side_effect = requests.exceptions.HTTPError(
            response=Mock(status_code=400, text="Bad Request")
        )

        # When, Then
        # NotionApiErrorがraiseされること
        with self.assertRaises(NotionApiError) as _:
            self.suite.post(path="dummy", data={"foo": "bar"})
