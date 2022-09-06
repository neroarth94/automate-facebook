
# importing all required libraries
import telebot
from telethon.sync import TelegramClient
from telethon.tl.types import InputPeerUser, InputPeerChannel
from telethon import TelegramClient, sync, events
import constant
import requests

def telegram_bot_send_message(message):
    for chat_id in constant.CHAT_ID:
        send_text = 'https://api.telegram.org/bot' + constant.TELEGRAM_BOT_TOKEN + '/sendMessage?chat_id=' + chat_id + '&parse_mode=Markdown&text=' + message

    response = requests.get(send_text)
    if ("200" not in str(response)):
        print("failed to send telegram bot message")
        print(send_text)
        print(response)
        return False
    return True