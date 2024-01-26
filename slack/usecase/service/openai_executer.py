from openai import OpenAI
from typing import Optional
import logging

OPENAI_MODEL_DEFAULT = "gpt-3.5-turbo-1106"

class OpenaiExecuter:
    def __init__(self, model: str = OPENAI_MODEL_DEFAULT, logger: Optional[logging.Logger] = None):
        self.model = model
        self.logger = logger or logging.getLogger(__name__)
        self.client = OpenAI()

    def simple_chat(self, user_content: str) -> str:
        """ メッセージをOpenAIに送信して、返答を受け取る """
        messages = [{"role": "user", "content": user_content}]
        response_message = self._chat_completions_create(messages=messages)
        self.logger.debug(response_message)
        return response_message.content

    def _chat_completions_create(self, messages: list[dict], tools: Optional[list[dict]] = None, tool_choice: Optional[str] = None):
        """ OpenAIのchat_completions.createを呼び出す """
        if tools is None or tool_choice is None:
            response = self.client.chat.completions.create(
              model=self.model,
              messages=messages,
            )
            self.logger.debug(response)
            response_message = response.choices[0].message
            return response_message
        else:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice="auto",
            )
            self.logger.debug(response)
            response_message = response.choices[0].message
            return response_message
