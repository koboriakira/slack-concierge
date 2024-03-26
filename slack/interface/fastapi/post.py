import os

from fastapi import APIRouter
from pydantic import BaseModel
from slack_sdk import WebClient

from interface.fastapi.base_response import BaseResponse
from usecase.slack.post_image_use_case import PostImageUseCase

router = APIRouter()

class PostImageRequest(BaseModel):
    image_url: str|list[str]

@router.post("/image/{channel}/{thread_ts}")
def post_to_channel_thread(
        request: PostImageRequest,
        channel: str,
        thread_ts: str) -> BaseResponse:
    slack_bot_client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
    usecase = PostImageUseCase(slack_bot_client=slack_bot_client)
    usecase.execute(
        image_url=request.image_url,
        channel=channel,
        thread_ts=thread_ts)
    return BaseResponse()

@router.post("/image/{channel}")
def post_to_channel(
        request: PostImageRequest,
        channel: str) -> BaseResponse:
    slack_bot_client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
    usecase = PostImageUseCase(slack_bot_client=slack_bot_client)
    usecase.execute(
        image_url=request.image_url,
        channel=channel)
    return BaseResponse()
