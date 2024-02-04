import os
from dotenv import load_dotenv
import logging
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)

from linebot.exceptions import (
    InvalidSignatureError
)

from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, QuickReply, QuickReplyButton, MessageAction, PostbackAction, FollowEvent
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
load_dotenv()

app = Flask(__name__)

LINE_CHANNEL_SECRET=os.environ["LINE_CHANNEL_SECRET"]
LINE_CHANNEL_ACCESS_TOKEN=os.environ["LINE_CHANNEL_ACCESS_TOKEN"]

handler = WebhookHandler(LINE_CHANNEL_SECRET)
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(FollowEvent)
def follow_message(line_follow_event):
    profile = line_bot_api.get_profile(line_follow_event.source.user_id)
    logger.info(profile)
    line_bot_api.reply_message(line_follow_event.reply_token, TextSendMessage(text=f'{profile.display_name}さん、フォローありがとう!収支と入力すると選択肢が現れるよ！！\n'))
    
@handler.add(MessageEvent, message=TextMessage)
def handle_message(line_reply_event):
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    profile = line_bot_api.get_profile(line_reply_event.source.user_id)
    logger.info(profile)
    money = 0
    message = line_reply_event.message.text.lower()
    if message == '収支':
        line_bot_api.reply_message(line_reply_event.reply_token, TextSendMessage(text='いずれを選択してね', quick_reply=QuickReply(items=[
            QuickReplyButton(action=PostbackAction(label="現在の金額を設定する", data="現在の金額を設定する", text="現在の金額を設定する")), #金額を追加する
            QuickReplyButton(action=PostbackAction(label="金額を減増する", data="金額を減増する", text="金額を減増する")), #金額を下げる
            QuickReplyButton(action=PostbackAction(label="現在の金額を確認する", data="現在の金額を確認する", text="現在の金額を確認する")) #現在の金額を表示する
        ])))
        
    if message == "現在の金額を設定する":
        line_bot_api.reply_message(line_reply_event.reply_token, TextSendMessage(text='金額を入力してください'))
    if message.isdigit():
        money = int(message)
        line_bot_api.reply_message(line_reply_event.reply_token, TextSendMessage(text=f'現在の金額を {money} 円に設定しました。'))
    else:
        line_bot_api.reply_message(line_reply_event.reply_token, TextSendMessage(text='有効な金額を入力してください。'))
    
    if message == "金額を減増する":
        line_bot_api.reply_message(line_reply_event.reply_token, TextSendMessage(text='金額を減増させる方法を選んでください', quick_reply=QuickReply(items=[
            QuickReplyButton(action=MessageAction(label="金額を増やす", text="金額を増やす")),
            QuickReplyButton(action=MessageAction(label="金額を減らす", text="金額を減らす"))
        ])))
    if message == "金額を増やす":
        line_bot_api.reply_message(line_reply_event.reply_token, TextSendMessage(text='金額を入力してください'))
    if message == "金額を減らす":
        line_bot_api.reply_message(line_reply_event.reply_token, TextSendMessage(text='金額を入力してください'))
    if message == "現在の金額を確認する":
        line_bot_api.reply_message(line_reply_event.reply_token, TextSendMessage(text=f'現在の金額は {money} 円です。'))

    handler.handle(body, signature)

if __name__ == "__main__":
    app.run()