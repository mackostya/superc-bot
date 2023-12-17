import logging
import datetime
from .utils import init_chat_ids, add_user_to_json
from telegram import Update


class ChatMembers:
    def __init__(self):
        self.users_file = "users.json"
        self.chat_ids = init_chat_ids(self.users_file)

    def get_chat_ids(self):
        return self.chat_ids

    def add_user(self, update: Update, start_to_check: str = True):
        self.chat_ids[update.effective_chat.id] = start_to_check
        date = str(datetime.datetime.now())
        txt = f"""
===== we have a new user! =====
User id: {update.effective_chat.id}
Name : {update.effective_chat.first_name}
Username: {update.effective_chat.username}
Time joined: {date} 
===============================
        """
        add_user_to_json(update, self.users_file)
        logging.info(txt)
