
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
    print(response)