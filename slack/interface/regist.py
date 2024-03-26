import json
import logging

from slack_bolt import Ack, App
from slack_sdk.web import WebClient

from domain.view.view import View
from infrastructure.api.lambda_notion_api import LambdaNotionApi
from usecase.regist_item import RegistItemModalUseCase, RegistItemUseCase
from util.error_reporter import ErrorReporter

SHORTCUT_ID = "regist"
CALLBACK_ID = "regist-modal"
CALLBACK_BOOK_ID = "regist-book-modal"


def just_ack(ack: Ack) -> None:
    ack()

def handle_modal(ack: Ack) -> None:
    ack()

def start_modal_interaction(body: dict, client: WebClient) -> None:
    try:
        logging.debug(json.dumps(body, ensure_ascii=False))
        usecase = RegistItemModalUseCase(client=client)
        usecase.execute(
            trigger_id=body["trigger_id"],
            callback_id=CALLBACK_ID)
    except:  # noqa: E722
        ErrorReporter().execute()

def regist_modal_interaction(logger: logging.Logger, view: dict, client: WebClient) -> None:  # noqa: ARG001
    try:
        logging.debug(json.dumps(view, ensure_ascii=False))
        view_model = View(view)
        state = view_model.get_state()
        _, category = state.get_static_select("category")

        notion_api = LambdaNotionApi()
        usecase = RegistItemUseCase(notion_api=notion_api)

        match category:
            case "book":
                # 書籍の登録
                book_info = state.get_text_input_value("book-info")
                usecase.regist_book(book_info)
            case _:
                msg = f"category: {category} is not supported"
                raise ValueError(msg)
    except:  # noqa: E722
        ErrorReporter().execute()


def shortcut_regist(app: App) -> App:
    app.shortcut(SHORTCUT_ID)(
        ack=just_ack,
        lazy=[start_modal_interaction],
    )

    app.view(CALLBACK_ID)(
        ack=handle_modal,
        lazy=[regist_modal_interaction],
    )

    return app
