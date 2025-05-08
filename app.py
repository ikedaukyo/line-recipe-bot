import os
from flask import Flask, request
from linebot import LineBotApi, WebhookHandler
from linebot.models import TextSendMessage
import openai

app = Flask(__name__)

# 環境変数の取得
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)
openai.api_key = OPENAI_API_KEY

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except Exception as e:
        print(f"Error: {e}")

    return 'OK'

@handler.add('message')
def handle_message(event):
    user_input = event.message.text

    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=f"ユーザーが入力した食材: {user_input}\nおすすめのレシピを3つ提案してください。",
            max_tokens=150,
            temperature=0.7
        )
        reply_text = response.choices[0].text.strip()
    except Exception as e:
        reply_text = "レシピの取得に失敗しました。"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

if __name__ == "__main__":
    app.run()
