from flask import Flask, request
import requests
from twilio.twiml.messaging_response import MessagingResponse
import random
import os

state = "none"
OPENWEATHER_KEY = os.environ["OPENWEATHER_KEY"]

app = Flask(__name__)

@app.route("/", methods=["POST"])

def bot():
    global state
    incoming_message = request.values.get("Body", "").lower()

    response = MessagingResponse()
    msg = response.message()

    if state == "none":
        if incoming_message in ['hello', 'helo', 'hola', 'hi']:
            body = "Hello to you too !"
            msg.body(body)
        elif incoming_message == "play":
            body = \
                "Let's play ! \n" \
                "Rock paper scissors shoot !\n" \
                "1. Rock\n" \
                "2. Paper\n" \
                "3. Scissors"
            state = "play"
            msg.body(body)
        elif incoming_message == "weather":
            weather_report = weather()
            msg.body(weather_report)
        else:
            body = "I don't understand ! I will respond to these words:\n" \
                "play\n" \
                "weather"
            msg.body(body)

    elif state == "play":
        num = random.random()

        if incoming_message not in ['1', '2', '3', 'rock', 'paper', 'scissors']:
            body = "I don't understand ! Please say one of the options !"
            msg.body(body)

            return str(response)

        if num < 0.33:
            body = "rock!"
        elif num < 0.66:
            body = "paper!"
        else:
            body = "scissors!"

        result = RPS(incoming_message, body)

        msg.body(body + '\n' + result)

        state = "none"


    return str(response)

def wind_description(wind_speed):
    if wind_speed < 5.0:
        return "no breeze"
    elif wind_speed < 9.0:
        return "light breeze"
    elif wind_speed < 14.0: # TBD
        return "gentle breeze"
    else:
        return "lots of wind !"

def weather(): # TODO respond to location
    global OPENWEATHER_KEY

    location_param = "Washington+DC,US"
    geocode_api_url = f"https://api.openweathermap.org/geo/1.0/direct?" \
        f"q={location_param}&limit=1&appid={OPENWEATHER_KEY}"
    geocode_resp = requests.get(geocode_api_url)

    lat = geocode_resp.json()[0]['lat']
    lon = geocode_resp.json()[0]['lon']

    weather_api_url = f"https://api.openweathermap.org/data/3.0/onecall?" \
        f"lat={lat}&lon={lon}&appid={OPENWEATHER_KEY}&units=imperial"
    weather_resp = requests.get(weather_api_url)

    today_weather = weather_resp.json()['daily'][0]
    weather = today_weather['weather'][0]['description']
    wind = wind_description(today_weather['wind_speed'])
    temps = today_weather['temp']
    avg_temp = round((temps['morn'] + temps['day'] + temps['eve']) / 3)
    humidity = today_weather['humidity']

    report = \
        f"{weather} with {wind}.\n" \
        f"Around {avg_temp} degrees. Humidity {humidity}%."

    return report

def RPS(user_pick, bot_pick):
    win = "Aww you win !"
    loss = "Haha I win !"
    tie = "It's a tie !"

    if user_pick in ['1', 'rock']:
        if bot_pick == 'rock!':
            return tie
        elif bot_pick == 'paper!':
            return loss
        else:
            return win
    elif user_pick in ['2', 'paper']:
        if bot_pick == 'rock!':
            return win
        elif bot_pick == 'paper!':
            return tie
        else:
            return loss
    elif user_pick in ['3', 'scissors']:
        if bot_pick == 'rock!':
            return loss
        elif bot_pick == 'paper!':
            return win
        else:
            return tie

if __name__ == "__main__":
    app.run()
