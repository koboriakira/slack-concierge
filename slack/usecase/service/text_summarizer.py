from openai import OpenAI


TEMPLATE = """「仕様」に則って「入力」に記載した文章の要約をしてください。

\"\"\"仕様
・最大文字数は500文字です
・指示に対する返答や補足など、文章の要約結果以外の出力は不要です

\"\"\"入力
{context}"""

class TextSummarizer:
    def __init__(self):
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
