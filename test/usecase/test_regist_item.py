from unittest import TestCase

import pytest

from infrastructure.api.lambda_notion_api import LambdaNotionApi
from usecase.regist_item import RegistRecipeUseCase


class TestRegistItem(TestCase):
    def setUp(self) -> None:
        return super().setUp()

    @pytest.mark.skip(reason="実際にAPI実行されるのでスキップ")
    def test_レシピの登録を実際にやる(self):
        # pipenv run python -m unittest test/usecase/test_regist_item.py -k test_レシピの登録を実際にやる
        suite = RegistRecipeUseCase(notion_api=LambdaNotionApi())

        # Given
        recipe_url = "https://www.youtube.com/watch?v=jjdLq6UeH_M"
        recipe_desc = """【脂肪燃焼豚汁】
ごぼう...150g
長ネギ...1本(120g)
お好きなきのこ...100～150g
(今回はしめじ、舞茸、エリンギを使います)
にんじん...150g
大根...200g
こんにゃく...200g
豚こま肉...220g
お塩控えめの・ほんだし...大さじ1
水...700cc
味噌...大さじ1
★お好みで味噌追加

水700cc、にんじん150g、こんにゃく200g、大根200g、ごぼう150g、お好きなきのこ100g、減塩ほんだし大さじ1を入れ柔らかくなるまで蓋をして煮て、豚こま肉220g、長ネギ1本120g入れ火をとおし、味噌大さじ1溶かして完成"""

        # When
        suite.regist_recipe(recipe_url=recipe_url, recipe_desc=recipe_desc)

        # Then
        self.fail("Notionにレシピが登録されたことを確認する")
