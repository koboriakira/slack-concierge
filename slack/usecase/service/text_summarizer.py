from openai import OpenAI
import logging

TEMPLATE = """「仕様」に則って「入力」に記載した文章の要約をしてください。

\"\"\"仕様
・最大文字数は500文字です
・指示に対する返答や補足など、文章の要約結果以外の出力は不要です

\"\"\"入力
{context}"""

class TextSummarizer:
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.client = OpenAI()

    def handle(self, text: str) -> str:
        print("TextSummarizer: " + text)
        content = TEMPLATE.format(context=text)
        messages = [
            {"role": "user", "content": content}
        ]
        response = self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=messages,
        )
        print(response)
        response_message = response.choices[0].message
        print(response_message)
        return response_message.content

if __name__ == "__main__":
    # python -m usecase.service.text_summarizer
    logging.basicConfig(level=logging.DEBUG)
    usecase = TextSummarizer(logger=logging.getLogger(__name__))
    text = """うまみや栄養がぎゅっと凝縮された「切り干し大根」。お醤油味の煮物もいいですが、サラダにしたりかき揚げにしたりと実は自由に楽しめる食材です。味付けもピリ辛やエスニック風味でパンチを効かせてお酒のよき相棒に！ 水でもどす工程なしのレシピなので、思い立ったらすぐ作れます。 """
    summary = usecase.handle(text)
    print(type(summary))
    print(summary)
