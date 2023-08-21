from flask import Flask, request
import requests
from twilio.twiml.messaging_response import MessagingResponse
import random
import os
import openai
import redis
import json
from settings import OPENAI_API_KEY, OPENWEATHER_API_KEY

openai.api_key = OPENAI_API_KEY

app = Flask(__name__)

# Initiate redis connection
r = redis.Redis(host="localhost", port=6379, decode_responses=True)

# Wipe previous conversation data and start a new one with assistant prompt
conversation_key = "main"
r.delete(conversation_key)
prompt = {
    "role": "system",
    "content": "You are a helpful assistant named Diane."
}
init_payload = json.dumps(prompt)
r.rpush(conversation_key, init_payload)


@app.route("/", methods=["POST"])
def main():
    # Get user input
    input_text = request.values.get("Body", "")

    # Add to payload for OpenAI API
    input_message = {
        "role": "user",
        "content": input_text
    }

    # Twilio API. We will put text content in `msg` attributes and return a string representation of `response``
    response = MessagingResponse()
    msg = response.message()

    # Retrieve conversation from redis in format ready to post to OpenAI. Update redis db with new input
    conversation = r.lrange(conversation_key, 0, -1)
    messages = [eval(message) for message in conversation]
    messages.append(input_message)
    input_payload = json.dumps(input_message)
    r.rpush(conversation_key, input_payload)

    # Call OpenAI API
    openai_res = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=256,
        temperature=0.6
    )

    # Update redis db with OpenAI response
    output_text = openai_res.choices[0].message.content
    output_message = {
        "role": "assistant",
        "content": output_text
    }
    output_payload = json.dumps(output_message)
    r.rpush(conversation_key, output_payload)

    # Return OpenAI message
    msg.body(output_text)
    return str(response)

if __name__ == "__main__":
    app.run()