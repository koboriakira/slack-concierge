# Slack Concierge

## 使用例

## 設定

https://pih7bw56og6yispto6bkltyase0sezem.lambda-url.ap-northeast-1.on.aws/slack/events をSlackAppのEvent SubscriptionとInteractivityそれぞれのRequest URLに設定する

※ https://9w3ln5q8e8.execute-api.ap-northeast-1.amazonaws.com/v1 はFastAPIのURL

## デプロイ

GitHub Actionsのdeployワークフローを利用。

## ローカル開発

ngrokは要インストール。

```shell
# localhostを公開
ngrok http 10121
# localhostでSlack Appを起動
pipenv run python slack/lazy_main.py
```

SlackAppのEvent SubscriptionとInteractivityそれぞれのRequest URLには `http://*****.ngrok-free.app/slack/events` を設定する。
