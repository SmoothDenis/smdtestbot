# Server import and other functions
import argparse
import os
from flask import Flask, request
import requests
import psycopg2
import datetime
from waitress import serve

# Your import
import telebot
from pyowm import OWM
from pyowm.utils.config import get_default_config
from pyowm.utils import timestamps
from telebot.types import BotCommand

# Secure transmission API TOKEN (paste to Heroku Config Vars)
API_TOKEN = os.environ["TOKEN_BOT"]
# Connect to API
bot = telebot.TeleBot(API_TOKEN)

# Setup server and URL Heroku for WebHook
server = Flask(__name__)
TELEBOT_URL = "telebot_webhook/"
# Get URL app from Heroku
BASE_URL = os.environ["BASE_URL"]

# Get data to connect database on Heroku
DATABASE_URL = os.environ["DATABASE_URL"]

# Get API OWM from Heroku
owm = OWM(os.environ["OWM_API"])

# SET ENVIRONMENT
config_dict = get_default_config()
config_dict["language"] = "ru"

# Call Insert data to weather_log
def push_to_database(message, t, w):
    # Try connect
    try:
        connection = psycopg2.connect(DATABASE_URL, sslmode="require")
        cursor = connection.cursor()

        postgres_insert_query = """INSERT INTO weather_log (time, tg_id, temp, detail) VALUES (%s,%s,%s,%s)"""
        record_to_insert = (
            datetime.datetime.now().strftime("%d-%m-%Y %H:%M"),
            message.chat.id,
            (int(t) * 100 // 100),
            w.detailed_status,
        )
        cursor.execute(postgres_insert_query, record_to_insert)

        connection.commit()
        count = cursor.rowcount
        print(count, "Record inserted successfully into weather_log table")

    finally:
        # Closing database connection.
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")


# PASTE THERE YOUR CODE | HANDLE BLOCK START

mgr = owm.weather_manager()

# PASTE ABOVE YOUR CODE | HANDLE BLOCK END

# Server functions
# POST URL for state change from down to up, make request to browser
@server.route("/" + TELEBOT_URL + API_TOKEN, methods=["POST"])
def get_message():
    bot.process_new_updates(
        [telebot.types.Update.de_json(request.stream.read().decode("utf-8"))]
    )
    return "!", 200


# SET WebHook if request main page
@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=BASE_URL + TELEBOT_URL + API_TOKEN)
    return "!", 200


# Fix to start the server on first launch or sleep status
def ping():
    requests.get(os.environ["BASE_URL"])


# Block for manual start (use option --pool)
parser = argparse.ArgumentParser(description="Run the bot")
parser.add_argument("--poll", action="store_true")
args = parser.parse_args()

if args.poll:
    bot.remove_webhook()
    bot.polling()
# No options - start server on Heroku, get PORT ENV from Config Vars and start WebHook listen
else:
    # server.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
    serve(server, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
    webhook()

# Self-request for normal work with sleep and autostart
ping()
