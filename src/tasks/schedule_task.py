import threading
import time
import schedule
import asyncio
import logging
from src.chat_members import ChatMembers

from src.utils import send_message


class ScheduleTask(threading.Thread):
    def __init__(self, bot, chat_members: ChatMembers):
        super(ScheduleTask, self).__init__(name="GoodMorningThread")
        schedule.every().day.at("08:32").do(self.send_daily_message)
        self.bot = bot
        self.chat_members = chat_members

    def send_daily_message(self):
        chat_ids = self.chat_members.get_chat_ids()
        loop = asyncio.new_event_loop()
        text = f"Good morning, have a nice day! New day new luck!"
        for id in chat_ids.keys():
            try:
                loop.run_until_complete(send_message(self.bot, id, text))
            except Exception as e:
                logging.error(f"Could not send message to {id}, due to: {e}")
        time.sleep(10)
        loop.close()

    def run(self):
        while True:
            schedule.run_pending()
            time.sleep(1)
