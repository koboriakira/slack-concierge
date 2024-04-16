import json
from logging import Logger

import requests
from requests import Response


class RequestWrapper:
    DEFAULT_TIMEOUT = 10

    def __init__(self, timeout: int | None = None, logger: Logger | None = None) -> None:
        self._timeout = timeout
        self._logger = logger

    def post(self, url: str, headers: dict, data: dict, timeout: int | None = None) -> Response:
        debug_message = f"POST to url: {url} data: {json.dumps(data, ensure_ascii=False)}"
        self._logger.debug(debug_message)

        response = requests.post(
            url=url,
            headers=headers,
            json=data,
            timeout=timeout or self._timeout or self.DEFAULT_TIMEOUT,
        )
        response.raise_for_status()
        return response

    def get(self, url: str, headers: dict, params: dict | None = None, timeout: int | None = None) -> Response:
        debug_message = (
            f"GET to url: {url} params: {json.dumps(params, ensure_ascii=False)}" if params else f"GET to url: {url}"
        )
        self._logger.debug(debug_message)

        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=timeout or self._timeout or self.DEFAULT_TIMEOUT,
        )
        response.raise_for_status()
        return response
