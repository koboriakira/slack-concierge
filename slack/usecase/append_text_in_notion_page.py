from domain.infrastructure.api.notion_api import NotionApi
from usecase.upload_files_to_s3 import UploadFilesToS3


class AppendTextInNotionPage:
    def __init__(self, notion_api: NotionApi, upload_files_to_s3: UploadFilesToS3):
        self.notion_api = notion_api
        self.upload_files_to_s3 = upload_files_to_s3

    def handle(
        self, page_id: str, text: str, files: list[dict], channel: str, thread_ts: str
    ):
        self.notion_api.append_text_block(block_id=page_id, value=text)
        if len(files) > 0:
            upload_response = self.upload_files_to_s3.execute(
                channel=channel, files=files, thread_ts=thread_ts
            )
            for image_url in upload_response.image_urls:
                self.notion_api.post(
                    path=f"/page/{page_id}/image/",
                    data={
                        "image_url": image_url.thumbnail_url,
                    },
                )
