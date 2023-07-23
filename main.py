from flask import Flask, request
import requests
from twilio.twiml.messaging_response import MessagingResponse
import random
import os
import openai
from settings import OPENAI_API_KEY, OPENWEATHER_API_KEY

openai.api_key = OPENAI_API_KEY

app = Flask(__name__)

@app.route("/", methods=["POST"])

def main():
    input_msg = request.values.get("Body", "")
    response = MessagingResponse()
    msg = response.message()

    openai_res = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant named Diane."
            },
            {
                "role": "user",
                "content": input_msg
            }
        ],
        max_tokens=256,
        temperature=0.6
    )

    msg.body(openai_res.choices[0].message.content)

    return str(response)

if __name__ == "__main__":
    app.run()