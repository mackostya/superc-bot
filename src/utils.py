import os
import json
import random
from telegram import Update
import logging
import asyncio


def init_chat_ids(users_file: str):
    chat_ids = {}
    if os.path.isfile(users_file):
        with open(users_file, "r") as file:
            d = json.load(file)
            logging.info("Existing users: " + str(d))
            for id in d.values():
                chat_ids[id] = True
    return chat_ids


def add_user_to_json(update: Update, users_file: str):
    d = {}
    if os.path.isfile(users_file):
        with open(users_file, "r") as file:
            d = json.load(file)
    with open(users_file, "w") as file:
        if (
            (update.effective_chat.username == None)
            or (update.effective_chat.username == "")
            or (update.effective_chat.username == "null")
        ):
            d["noname_" + str(random.randint(4, 100000))] = update.effective_chat.id
        else:
            d[update.effective_chat.username] = update.effective_chat.id
        json_object = json.dumps(d)
        file.write(json_object)


async def send_message(bot, chat_id: int, text: str):
    await bot.send_message(
        chat_id=chat_id,
        text=text,
    )
    asyncio.sleep(5)
