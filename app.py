import os
from flask import Flask, request, abort
from linebot.v3.webhook import WebhookHandler
from linebot.v3.messaging import MessagingApi, ReplyMessageRequest, TextMessage
import openai

app = Flask(__name__)

LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

line_bot_api = MessagingApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)
openai.api_key = OPENAI_API_KEY

@app.route("/", methods=["GET"])
def home():
    return "LINE Recipe Bot is running!", 200

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature")
    body = request.get_data(as_text=True)

    print("===== Received POST request to /callback =====")
    print(f"Signature: {signature}")
    print(f"Body: {body}")

    try:
        handler.handle(body, signature)
        print("Webhook handled successfully")
    except Exception as e:
        print(f"Error in callback: {e}")
        abort(500)

    return "OK", 200

@handler.add(TextMessage)
def handle_message(event):
    print("===== handle_message triggered =====")
    user_input = event.message.text
    print(f"User input: {user_input}")

    try:
        print("Requesting OpenAI...")
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=f"ユーザーが入力した食材: {user_input}\nおすすめのレシピを3つ提案してください。",
            max_tokens=150,
            temperature=0.7
        )

        reply_text = response.choices[0].text.strip()
        print(f"OpenAI Response: {reply_text}")

    except Exception as e:
        print(f"OpenAI Error: {e}")
        reply_text = "申し訳ございませんが、レシピの取得に失敗しました。"

    reply_message = ReplyMessageRequest(
        reply_token=event.reply_token,
        messages=[TextMessage(text=reply_text)]
    )

    try:
        print("Sending reply to LINE...")
        line_bot_api.reply_message(reply_message)
        print("Reply sent successfully!")
        except Exception as e:

