from slack_bolt import Ack

def execute(ack: Ack):
    """
    ただ ack() だけを実行する関数
    lazy に指定された関数は別の AWS Lambda 実行として非同期で実行されます
    """
    ack()
