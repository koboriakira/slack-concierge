import logging
from typing import Optional
from usecase.service.openai_executer import OpenaiExecuter

def analyze_tags(args: dict) -> list[str]:
    tags: Optional[str] = args.get("tags")
    if tags is None:
        return []
    return [tag.strip() for tag in tags.split(",")]

class TagAnalyzer:
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.client = OpenaiExecuter(model="gpt-3.5-turbo-1106", logger=logger)

    def handle(self, text: str) -> list[str]:
        user_content = f"次の文章を解析して、タグをつけてください。\n\n{text}"
        analyze_tags_parameters = {
            "type": "object",
            "properties": {
                "tags": {
                    "type": "string",
                    "description": "タグのリスト。カンマ区切りで複数指定可能\n例) 文章術, プロレス, 資産運用",
                },
            },
            "required": ["tags"],
        }
        tags:list[str] = self.client.simple_function_calling(
            user_content=user_content,
            func=analyze_tags,
            func_description="タグをつける",
            parameters=analyze_tags_parameters,
        )
        return tags

    def handle_for_prowrestling(self, text: str) -> list[str]:
        user_content = f"次の試合情報を分析して、出場選手およびタイトルマッチをタグとして抜き出してください。\n\n{text}"
        analyze_tags_parameters = {
            "type": "object",
            "properties": {
                "tags": {
                    "type": "string",
                    "description": "タグのリスト。カンマ区切りで複数指定可能\n例) 山下実優, ハイパーミサヲ, インターナショナル・プリンセス選手権試合",
                },
            },
            "required": ["tags"],
        }
        tags:list[str] = self.client.simple_function_calling(
            user_content=user_content,
            func=analyze_tags,
            func_description="タグをつける",
            parameters=analyze_tags_parameters,
        )
        return tags

if __name__ == "__main__":
    # python -m usecase.service.tag_analyzer
    logging.basicConfig(level=logging.DEBUG)
    tag_analyzer = TagAnalyzer()
    print(tag_analyzer.handle_for_prowrestling(text="第4回“ふたりはプリンセス”Max Heartトーナメント\n試合開始は11:30を予定\n\n■対戦カード\n○オープニングマッチ　6人タッグマッチ\n山下実優＆鳥喰かや＆凍雅　vs　愛野ユキ＆上福ゆき＆桐生真弥\n\n○第2試合　3WAYマッチ\n宮本もか　vs　HIMAWARI　vs　風城ハル\n\n○第3試合　トーナメント2回戦　時間無制限一本勝負\nらく＆原宿ぽむ　vs　鈴芽＆遠藤有栖\n\n○セミファイナル　トーナメント2回戦　時間無制限一本勝負\n荒井優希＆上原わかな　vs　瑞希＆鈴木志乃\n\n○メインイベント　トーナメント2回戦　時間無制限一本勝負\n辰巳リカ＆渡辺未詩　vs　中島翔子＆ハイパーミサヲ"))
