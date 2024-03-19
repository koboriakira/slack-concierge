import json
import logging
import os
from datetime import date as Date
from datetime import datetime as Datetime

import requests

from domain.infrastructure.api.notion_api import NotionApi
from domain.notion.notion_page import NotionPage, RecipePage, TaskPage
from util.custom_logging import get_logger

NOTION_SECRET = os.getenv("NOTION_SECRET")

class LambdaNotionApi(NotionApi):
    def __init__(self, logger: logging.Logger | None = None):
        self.domain = os.environ["LAMBDA_NOTION_API_DOMAIN"]
        self.logger = logger or get_logger(__name__)

    def list_recipes(self) -> list[RecipePage]:
        response = self._get(path="recipes")
        data = response["data"]
        return [RecipePage.from_dict(page) for page in data]

    def list_projects(self, status: str | None = None) -> list[NotionPage]:
        params = {}
        if status:
            params["status"] = status
        response = self._get(path="projects", params=params)
        data = response["data"]
        return [NotionPage.from_dict(page) for page in data]

    def find_project(self, project_id: str) -> NotionPage:
        response = self._get(path=f"projects/{project_id}")
        logging.debug(response)
        data = response["data"]
        return NotionPage.from_dict(data)

    def list_tasks(self,
                   start_date: Date | None = None,
                   status: str | None = None,
                   ) -> list[TaskPage]:
        params = {}
        if start_date:
            params["start_date"] = start_date
        if status:
            params["status"] = status
        response = self._get(path="tasks", params=params)
        data = response["data"]
        return [TaskPage.from_dict(page) for page in data]

    def list_current_tasks(self) -> list[TaskPage]:
        response = self._get(path="tasks/current")
        data = response["data"]
        return [TaskPage.from_dict(page) for page in data]


    def find_task(self, task_id: str) -> TaskPage:
        response = self._get(path=f"task/{task_id}")
        data = response["data"]
        return TaskPage.from_dict(data)

    def create_track_page(self, track_name: str,
                                artists: list[str],
                                spotify_url: str | None = None,
                                cover_url: str | None = None,
                                release_date: Date | None = None) -> dict:
        url = f"{self.domain}music"
        data = {
            "track_name": track_name,
            "artists": artists,
        }
        if spotify_url:
            data["spotify_url"] = spotify_url
        if cover_url:
            data["cover_url"] = cover_url
        if release_date:
            data["release_date"] = release_date.strftime("%Y-%m-%d")
        return self._post(url=url, data=data)

    def create_webclip_page(self,
                            url: str,
                            title: str,
                            cover: str | None = None,
                            ) -> dict:
        api_url = f"{self.domain}webclip"
        data = {
            "url": url,
            "title": title,
        }
        if cover:
            data["cover"] = cover
        return self._post(url=api_url, data=data)

    def create_video_page(self,
                            url: str,
                            title: str,
                            tags: list[str],
                            cover: str | None = None,
                            ) -> dict:
        api_url = f"{self.domain}video"
        data = {
            "url": url,
            "title": title,
            "tags": tags,
        }
        if cover:
            data["cover"] = cover
        return self._post(url=api_url, data=data)

    def add_book(
        self,
        google_book_id: str | None = None,
        title: str | None = None) -> dict:
        api_url = f"{self.domain}books/regist"
        data = {}
        if google_book_id:
            data["google_book_id"] = google_book_id
        if title:
            data["title"] = title
        return self._post(url=api_url, data=data)

    def create_prowrestling_page(self,
                                 url: str,
                                 title: str,
                                 date: Date,
                                 promotion: str,
                                 text: str,
                                 tags: list[str],
                                 cover: str | None = None,
                                ) -> dict:
        api_url = f"{self.domain}prowrestling"
        data = {
            "url": url,
            "title": title,
            "date": date.strftime("%Y-%m-%d"),
            "promotion": promotion,
            "tags": tags,
        }
        if cover:
            data["cover"] = cover
        return self._post(url=api_url, data=data)

    def append_feeling(self,
                       page_id: str,
                       feeling: str,
                       ) -> dict:
        api_url = f"{self.domain}page/feeling"
        data = {
            "page_id": page_id,
            "value": feeling,
        }
        return self._post(url=api_url, data=data)

    def update_pomodoro_count(self,
                              page_id: str,
                              count: int | None = None,
                              ) -> dict:
        api_url = f"{self.domain}page/pomodoro-count"
        data = {
            "page_id": page_id,
        }
        self.logger.debug(f"url: {api_url} data: {json.dumps(data, ensure_ascii=False)}")
        return self._post(url=api_url, data=data)

    def update_status(self,
                      page_id: str,
                      value: str,
                      ) -> dict:
        api_url = f"{self.domain}page/status"
        data = {
            "page_id": page_id,
            "value": value,
        }
        return self._post(url=api_url, data=data)

    def create_task(self,
                    title: str | None = None,
                    mentioned_page_id: str | None = None,
                    start_date: Date | Datetime | None = None,
                    end_date: Date | Datetime | None = None,
                    ) -> dict:
        api_url = f"{self.domain}task"
        data = {}
        if title:
            data["title"] = title
        if mentioned_page_id:
            data["mentioned_page_id"] = mentioned_page_id
        if start_date:
            data["start_date"] = start_date.isoformat()
        if end_date:
            data["end_date"] = end_date.isoformat()
        return self._post(url=api_url, data=data)

    def append_text_block(self,
                          block_id: str,
                          value: str,
                          ) -> dict:
        api_url = f"{self.domain}page/block/text"
        data = {
            "page_id": block_id,
            "value": value,
        }
        return self._post(url=api_url, data=data)


    def get(self, path: str, params: dict | None = None) -> dict:
        """ 任意のパスに対してGETリクエストを送る。共通化のために作成 """
        debug_message = f"GET to url: {path}"
        self.logger.debug(debug_message)

        url = f"{self.domain}{path}"
        headers = {
            "access-token": NOTION_SECRET,
        }
        response = requests.get(url, params=params, headers=headers, timeout=10)

        if response.status_code != 200:
            error_message = f"status_code: {response.status_code}, message: {response.text}"
            raise Exception(error_message)
        return response.json()

    def _get(self, path: str, params: dict = {}) -> dict:
        """ 任意のパスに対してPOSTリクエストを送る """
        url = f"{self.domain}{path}"
        headers = {
            "access-token": NOTION_SECRET,
        }
        response = requests.get(url, params=params, headers=headers)
        logging.debug(response)
        if response.status_code != 200:
            raise Exception(f"status_code: {response.status_code}, message: {response.text}")
        return response.json()

    def post(self, path: str, data: dict) -> dict:
        """ NotionAPIにPOSTリクエストを送る。共通化のために作成 """
        headers = {
            "access-token": NOTION_SECRET,
        }
        debug_message = f"POST to url: {path}"
        self.logger.debug(debug_message)

        respone = requests.post(url=f"{self.domain}{path}",
                                headers=headers,
                                json=data,
                                timeout=60)
        if respone.status_code != 200:
            exception_message = f"statusCode:{respone.status_code}, msg: {respone.text}, data: {json.dumps(data, ensure_ascii=False)}"
            raise Exception(exception_message)
        response_json = respone.json()
        return response_json["data"]


    # 非推奨
    def _post(self, url: str, data: dict) -> dict:
        """非推奨"""
        headers = {
            "access-token": NOTION_SECRET,
        }
        self.logger.debug(f"url: {url} data: {json.dumps(data, ensure_ascii=False)}")
        respone = requests.post(url=url, headers=headers, json=data)
        if respone.status_code != 200:
            exception_message = f"{respone.status_code}: {respone.text}"
            raise Exception(exception_message)
        response_json = respone.json()
        self.logger.debug(json.dumps(response_json, ensure_ascii=False))
        return response_json["data"]



if __name__ == "__main__":
    # python -m infrastructure.api.lambda_notion_api
    logging.basicConfig(level=logging.DEBUG)
    notion_api = LambdaNotionApi(logger=logging.getLogger(__name__))

    # print(notion_api.find_project(project_id="b95d7eb173f9436893c2240650323b30"))

    # print(notion_api.list_recipes())

    # print(notion_api.create_track_page(
    #     track_name="Plastic Love",
    #     artists=["Friday Night Plans"],
    #     spotify_url="https://open.spotify.com/intl-ja/track/2qxTmEfGbBGMSJrwu4Ez1v?si=c4750c498ac14c7c",
    #     release_date=Date(2024, 1, 22)
    # ))


# {
#     "url": "https://note.com/koboriakira/n/ne14eaa1c50d2?sub_rt=share_pb",
#     "title": "東京女子プロレスのベストバウト29選 (2023)｜コボリアキラ",
#     "summary": "2023年にファンとなった筆者が、その年の東京女子プロレスのベストバウト29試合について熱く語る記事。筆者は東京女子プロレスの魔法にかけられたように熱中し、試合や選手への情熱的な愛情を語りつくす。多くの試合が印象的だったが、特に強調されるのは、選手たちのエネルギッシュなパフォーマンス、印象的なシーン、そしてファンの心を捉えるストーリーテリングである。筆者は、東京女子プロレスの独特の魅力を「東京女子プロレスだから好き」という言葉で表現し、彼らのプロレスへの深い愛情を読者に伝えている。",
#     "cover": "https://assets.st-note.com/production/uploads/images/126014735/rectangle_large_type_2_a12108f8a67248cc00e888924d6a08dc.jpeg?fit=bounds&quality=85&width=1280",
#     "tags": ["東京女子プロレス", "プロレス", "ベストバウト", "2023"],
#     "status": "Inbox",
#     "text": "テスト"
# }

    # print(notion_api.create_webclip_page(
    #     url= "https://6yhkmd3lcl.execute-api.ap-northeast-1.amazonaws.com/v1/webclip",
    #     title= "LangChain の新記法「LangChain Expression Language (LCEL)」入門",
    #     summary= "LangChainの新しいコード記述方式「LangChain Expression Language (LCEL)」について解説されており、2023年10月以降、LangChainでの実装標準となっています。LCELはプロンプトやLLMを\"|\"で繋ぐことで操作の連鎖を可能にし、直感的なコード記述を実現します。具体的な使用例としては、料理レシピの生成や、その結果をクラスのインスタンスに変換する流れが紹介されています。LCELの背後には「Runnableインタフェース」があり、これにより\"|”を用いた記法が可能となっています。このLCELを用いることで、従来より直感的に、また柔軟に連鎖的処理を実装できるようになります。また、2023年11月末からLangChainのコア機能が「langchain-core」として分離され、LCELを含む主要な抽象化がより安定したパッケージとして提供されるようになりました。",
    #     tags= [
    #         "LangChain",
    #         "LCEL",
    #         "コード記述",
    #         "プログラミング",
    #         "技術革新"
    #     ],
    #     text= "LangChain の新記法「LangChain Expression Language (LCEL)」入門\nLangChain Advent Calendar 2023 の 2 日目の記事です。\nLangChain Expression Language (LCEL) とは\nLangChain Expression Language (LCEL) は、LangChain でのコードの新しい記述方法です。\n公式ドキュメント: https://python.langchain.com/docs/expression_language/\nLCEL ではプロンプトや LLM を\n| で繋げて書き、処理の連鎖 (Chain) を実装します。\n2023 年 10 月後半頃から、LangChain では LCEL を使う実装が標準的となっています。\nこの記事では LCEL の基本的な使い方を紹介していきます。\nLCEL の基本的な使い方\nprompt と model をつなぐ\nまず、LCEL を使う最もシンプルな例として、prompt と model をつないでみます。\nはじめに、prompt (PromptTemplate) と model (ChatOpenAI) を準備します。\nfrom langchain.chat_models import ChatOpenAI\nfrom langchain.prompts import PromptTemplate\nprompt = PromptTemplate.from_template(\"\"\"料理のレシピを考えてください。\n料理名: {dish}\"\"\")\nmodel = ChatOpenAI(model_name=\"gpt-3.5-turbo-1106\", temperature=0)\nそして、これらをつないだ chain を作成します。\nchain = prompt | model\nこの chain を実行します。\nresult = chain.invoke({\"dish\": \"カレー\"})\nprint(result.content)\nすると、以下のように LLM の生成した応答が表示されます。\n材料:\n- 牛肉または鶏肉 300g\n- 玉ねぎ 1個\n<以下略>\nprompt (PromptTeamplte) の穴埋めと、model (ChatOpenAI) の呼び出しが連鎖的に実行された、ということです。\nLCEL では、\nchain = prompt | model のように、プロンプトや LLM を\n| で繋げて書き、処理の連鎖 (Chain) を実装します。\nLCEL 以前は\nchain = LLMChain(prompt=prompt, llm=llm) のように書いて Chain を実装していました。\nこれらを比較すると、LCEL のほうが直感的なコードに見えると思います。\noutput_parser も繋ぐ\n2 つ目の例として、prompt と model に加えて、output_parser も繋いでみます。\nLLM に料理のレシピを生成させて、その結果を Recipe クラスのインスタンスに変換する、という流れを実施してみます。\nまず、Recipe クラスを定義し、output_parser (PydanticOutputParser) を準備します。\nfrom dotenv import load_dotenv\nfrom langchain.chat_models import ChatOpenAI\nfrom langchain.output_parsers import PydanticOutputParser\nfrom langchain.prompts import PromptTemplate\nfrom pydantic import BaseModel, Field\nclass Recipe(BaseModel):\ningredients: list[str] = Field(description=\"ingredients of the dish\")\nsteps: list[str] = Field(description=\"steps to make the dish\")\noutput_parser = PydanticOutputParser(pydantic_object=Recipe)\n続いて、prompt (PromptTemplate) と model (ChatOpenAI) を準備します。\nprompt = PromptTemplate.from_template(\n\"\"\"料理のレシピを考えてください。\n{format_instructions}\n料理名: {dish}\"\"\",\npartial_variables={\"format_instructions\": output_parser.get_format_instructions()},\n)\nmodel = ChatOpenAI(model=\"gpt-3.5-turbo-1106\").bind(\nresponse_format={\"type\": \"json_object\"}\n)\nLCEL の記法で、prompt と model、output_parser を繋いだ chain を作成します。\nchain = prompt | model | output_parser\nchain を実行してみます。\nresult = chain.invoke({\"dish\": \"カレー\"})\nprint(type(result))\nprint(result)\nすると、最終的な出力として、Recipe クラスのインスタンスが得られました。\n<class '__main__.Recipe'>\ningredients=['カレールー', '肉（豚肉、鶏肉、牛肉など）', 'じゃがいも', 'にんじん', '玉ねぎ', 'にんにく', '生姜', 'トマト缶', '水', '塩', 'コショウ', 'サラダ油'] steps=['1. じゃがいもとにんじんを洗い、皮をむいて食べやすい大きさに切る。', '2. 玉ねぎ、にんにく、生姜をみじん切りにする。', '3. 鍋にサラダ油を熱し、にんにくと生姜を炒める。', '4. 肉を加えて炒め、色が変わったら玉ねぎを加える。', '5. じゃがいもとにんじんを加えて炒める。', '6. トマト缶を加え、水を注ぎ入れて煮込む。', '7. カレールーを加えて溶かし、塩とコショウで味を調える。', '8. ご飯の上にカレーをかけて完成。']\nLCEL のしくみ\nここで、LCEL の記法がどのように実現されているのかを少し解説します。\nLCEL は、LangChain の各種モジュールが継承している「Runnable インタフェース」などによって実現されています。\nLangChain (langchain-core) のソースコードで、Runnable は抽象基底クラス (ABC) として定義されています。\nclass Runnable(Generic[Input, Output], ABC):\n引用元: https://github.com/langchain-ai/langchain/blob/f4d520ccb5ea2bc648a88adf689eb866384b9ae1/libs/core/langchain_core/runnables/base.py#L83\nRunnable では\n__or__ と\n__ror__ が実装されています。\ndef __or__( self, other: Union[ Runnable[Any, Other], Callable[[Any], Other], Callable[[Iterator[Any]], Iterator[Other]], Mapping[str, Union[Runnable[Any, Other], Callable[[Any], Other], Any]], ], ) -> RunnableSerializable[Input, Other]: \"\"\"Compose this runnable with another object to create a RunnableSequence.\"\"\" return RunnableSequence(first=self, last=coerce_to_runnable(other)) def __ror__( self, other: Union[ Runnable[Other, Any], Callable[[Other], Any], Callable[[Iterator[Other]], Iterator[Any]], Mapping[str, Union[Runnable[Other, Any], Callable[[Other], Any], Any]], ], ) -> RunnableSerializable[Other, Output]: \"\"\"Compose this runnable with another object to create a RunnableSequence.\"\"\" return RunnableSequence(first=coerce_to_runnable(other), last=self)\n引用元: https://github.com/langchain-ai/langchain/blob/f4d520ccb5ea2bc648a88adf689eb866384b9ae1/libs/core/langchain_core/runnables/base.py#L354\nPython では、\n__or__ や\n__ror__ によって\n| を演算子オーバーロードすることができるため、\nchain = prompt | model のような記法ができるということです。\nもう少しだけ複雑な LCEL の例\nLCEL のしくみをなんとなく知ったところで、もう少しだけ複雑な LCEL の例もいくつか見てみます。\nルールベースの処理 (通常の関数) をはさむ\nLLM を使ったアプリケーションでは、LLM の応答に対してルールベースでさらに処理を加えたり、何らかの変換をかけたいことも多いです。\nLCEL では、Chain の連鎖に任意の処理 (関数) を加えることができます。\nたとえば、LLM の生成したテキストに対して、小文字を大文字に変換する処理を連鎖させたい場合は、以下のように実装できます。\nfrom langchain.schema.runnable import RunnableLambda\ndef upper(inp: str) -> str:\nreturn inp.upper()\nchain = prompt | model | output_parser | RunnableLambda(upper)\n独自の処理と LLM の呼び出しを連鎖させたい、というユースケースはかなり多いので、その流れを直感的に書けるのはとても嬉しいです。\nRAG (Retrieval-Augmented Generation)\n最後に、最近話題の RAG (Retrieval-Augmented Generation) の例です。\nRAG では下図のように、ユーザの入力に関係する文書を VectorStore から検索して、プロンプトに含めて使います。\n文書をベクトル検索したりしてプロンプトに含めることで、社内文書などの LLM が本来知らない情報をもとに回答させることができる、という手法です。\nRAG を LCEL で実装するため、まずは retriever (LangChain における文書を検索するインタフェース) を準備します。\nfrom langchain.chat_models import ChatOpenAI\nfrom langchain.embeddings import OpenAIEmbeddings\nfrom langchain.prompts import ChatPromptTemplate\nfrom langchain.schema.runnable import RunnablePassthrough\nfrom langchain.vectorstores.faiss import FAISS\ntexts = [\n\"私の趣味は読書です。\",\n\"私の好きな食べ物はカレーです。\",\n\"私の嫌いな食べ物は饅頭です。\",\n]\nvectorstore = FAISS.from_texts(texts, embedding=OpenAIEmbeddings())\nretriever = vectorstore.as_retriever(search_kwargs={\"k\": 1})\nprompt・model・output_parser を準備します。\nprompt = ChatPromptTemplate.from_template(\n\"\"\"以下のcontextだけに基づいて回答してください。\n{context}\n質問: {question}\n\"\"\"\n)\nmodel = ChatOpenAI(model=\"gpt-3.5-turbo-1106\", temperature=0)\noutput_parser = StrOutputParser()\nLCEL で chain を実装します。\nchain = (\n{\"context\": retriever, \"question\": RunnablePassthrough()}\n| prompt\n| model\n| output_parser\n)\nこの LCEL の chain では、最初に\n{\"context\": retriever, \"question\": RunnablePassthrough()} と書かれています。\nこれは、入力が retriever に渡されつつ、prompt にも渡される、というイメージです。\nこの chain を実行します。\nresult = chain.invoke(\"私の好きな食べ物はなんでしょう？\")\nprint(result)\nすると、検索した独自知識に基づいて回答してくれました。\n回答: カレーです。\nおわりに\nこの記事では、LangChain の新記法「LangChain Expression Language (LCEL)」を紹介しました。\nLLM を使ったアプリケーション開発において、連鎖的に処理を実行したいことは非常に多いです。\nそのような処理の流れを直感的に書けることはとても嬉しく、LCEL を知って以来、「LangChain を入れるのは重いけど、LCEL は使いたいなあ」と思うことも多かったです。\nそんな中、2023 年 11 月末から、LangChain のコア機能の「langchain-core」というパッケージへの分離が始まりました。\n「langchain-core」には、LangChain の主要な抽象化や LCEL が含まれ、今までよりも安定したパッケージにすることを意図しているそうです。\n「LangChain の抽象化や LCEL だけ使えればいいのに」と思うことも多かった自分には非常に嬉しい取り組みです。\n今後の LangChain のアップデートも楽しみです。\nDiscussion",
    #     cover= "https://res.cloudinary.com/zenn/image/upload/s--Zg_PKBou--/c_fit%2Cg_north_west%2Cl_text:notosansjp-medium.otf_55:LangChain%2520%25E3%2581%25AE%25E6%2596%25B0%25E8%25A8%2598%25E6%25B3%2595%25E3%2580%258CLangChain%2520Expression%2520Language%2520%2528LCEL%2529%25E3%2580%258D%25E5%2585%25A5%25E9%2596%2580%2Cw_1010%2Cx_90%2Cy_100/g_south_west%2Cl_text:notosansjp-medium.otf_37:oshima_123%2Cx_203%2Cy_121/g_south_west%2Ch_90%2Cl_fetch:aHR0cHM6Ly9zdG9yYWdlLmdvb2dsZWFwaXMuY29tL3plbm4tdXNlci11cGxvYWQvYXZhdGFyLzY1ZjAzMGZmOTcuanBlZw==%2Cr_max%2Cw_90%2Cx_87%2Cy_95/v1627283836/default/og-base-w1200-v2.png"
    # ))
    # print(notion_api.list_tasks(start_date=Date.today()))

    print(notion_api.add_book(title="大切なことだけをやりなさい"))
