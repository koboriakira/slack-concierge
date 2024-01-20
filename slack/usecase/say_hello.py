import logging

def execute(message, say):
    logging.info(message)
    user = message['user']
    say(f"Hi there, <@{user}>!")
