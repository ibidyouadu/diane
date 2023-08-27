from fastapi import FastAPI, Form, Depends
from twilio.rest import Client
import openai
import redis
import json
from settings import OPENAI_API_KEY, OPENWEATHER_API_KEY, TO_NUMBER
from utils import send_message, logger

openai.api_key = OPENAI_API_KEY

app = FastAPI()

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


@app.post("/")
async def reply(Body: str=Form()):
    # Add to payload for OpenAI API
    input_message = {
        "role": "user",
        "content": Body
    }

    # Retrieve conversation from redis in format ready to post to OpenAI. Update redis db with new input
    conversation = r.lrange(conversation_key, 0, -1)
    messages = [eval(message) for message in conversation]
    messages.append(input_message)
    input_payload = json.dumps(input_message)
    r.rpush(conversation_key, input_payload)
    logger.info("Stored the user request in the database.")

    # Call OpenAI API and extract GPT response
    openai_res = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=256,
        temperature=0.6
    )
    output_body = openai_res.choices[0].message.content

    # Update redis db with OpenAI response
    output_message = {
        "role": "assistant",
        "content": output_body
    }
    output_payload = json.dumps(output_message)
    r.rpush(conversation_key, output_payload)
    logger.info("Stored the response in the database.")

    # Send response to user
    send_message(TO_NUMBER, output_body)

    return True