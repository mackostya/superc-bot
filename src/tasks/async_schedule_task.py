import threading
import time
import schedule
import asyncio
import logging
from src.chat_members import ChatMembers

from src.utils import send_message


class AsyncScheduleTask(threading.Thread):
    def __init__(self, bot, chat_members: ChatMembers):
        super(AsyncScheduleTask, self).__init__(name="Async GoodMorningThread")
        self.bot = bot
        self.chat_members = chat_members
        self.loop = asyncio.new_event_loop()

    async def async_send_daily_message(self):
        chat_ids = self.chat_members.get_chat_ids()
        text = f"Good morning, have a nice day! New day new luck!"
        for id in chat_ids.keys():
            try:
                await send_message(self.bot, id, text)
            except Exception as e:
                logging.error(f"Could not send message to {id}, due to: {e}")

    async def async_task(self):
        while True:
            time.sleep(1)
            if time.strftime("%H:%M") == "08:00":
                await self.async_send_daily_message()

    def run(self):
        self.loop.run_until_complete(self.async_task())
