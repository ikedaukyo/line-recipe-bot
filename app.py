import os
from flask import Flask, request, abort
from linebot.v3.webhook import WebhookHandler
from linebot.v3.messaging import MessagingApi, ReplyMessageRequest, TextMessage, TextMessageContent
import openai

app = Flask(__name__)

# 環境変数の取得
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# LINE Messaging API
line_bot_api = MessagingApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# OpenAIの設定
openai.api_key = OPENAI_API_KEY

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature')
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except Exception as e:
        print(f"Error in callback: {e}")
        abort(500)

    return 'OK', 200

@handler.add(TextMessage)
def handle_message(event):
    user_input = event.message.text

    try:
        # OpenAIでレシピ取得
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=f"ユーザーが入力した食材: {user_input}\nおすすめのレシピを3つ提案してください。",
            max_tokens=150,
            temperature=0.7
        )
        reply_text = response.choices[0].text.strip()

    except Exception as e:
        print(f"OpenAI Error: {e}")
        reply_text = "レシピの取得に失敗しました。"

    # 返信メッセージの作成
    reply_message = ReplyMessageRequest(
        reply_token=event.reply_token,
        messages=[TextMessage(text=reply_text)]
    )

    # メッセージの送信
    try:
        line_bot_api.reply_message(reply_message)
    except Exception as e:
        print(f"LINE Reply Error: {e}")

if __name__ == "__main__":
    app.run()
