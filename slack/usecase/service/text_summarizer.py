from typing import Optional
import logging
from usecase.service.openai_executer import OpenaiExecuter

TEMPLATE = """「仕様」に則って「入力」に記載した文章の要約をしてください。

\"\"\"仕様
・最大文字数は500文字です
・指示に対する返答や補足など、文章の要約結果以外の出力は不要です

\"\"\"入力
{context}"""

class TextSummarizer:
    def __init__(self, logger: Optional[logging.Logger] = None, is_debug: bool = False):
        self.logger = logger or logging.getLogger(__name__)
        self.client = OpenaiExecuter(model="gpt-3.5-turbo-1106",
                                     logger=logger)
        self.is_debug = is_debug

    def handle(self, text: str) -> str:
        self.logger.debug("TextSummarizer: " + text)
        if self.is_debug:
            return "要約テスト"
        user_content = TEMPLATE.format(context=text)
        return self.client.simple_chat(user_content=user_content)

if __name__ == "__main__":
    # python -m usecase.service.text_summarizer
    logging.basicConfig(level=logging.DEBUG)
    usecase = TextSummarizer(logger=logging.getLogger(__name__))
    text = """うまみや栄養がぎゅっと凝縮された「切り干し大根」。お醤油味の煮物もいいですが、サラダにしたりかき揚げにしたりと実は自由に楽しめる食材です。味付けもピリ辛やエスニック風味でパンチを効かせてお酒のよき相棒に！ 水でもどす工程なしのレシピなので、思い立ったらすぐ作れます。 """
    summary = usecase.handle(text)
    print(type(summary))
    print(summary)
