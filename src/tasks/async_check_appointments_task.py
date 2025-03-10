import threading
import random
import asyncio
import logging
import getpass

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

from src.chat_members import ChatMembers
from src.utils import send_message
from configs.config import (
    URL_CIT_1,
    URL_CIT_2,
    URL_CIT_3,
    URL_RWTH_1,
    URL_RWTH_2,
    URL_RWTH_3,
    DEFAULT_TITLE_RESPONSE,
    DEFAULT_TEXT,
)


class AsyncCheckAppointmentsTask(threading.Thread):
    def __init__(self, bot, chat_members: ChatMembers, bot_type: str):
        super(AsyncCheckAppointmentsTask, self).__init__(name="AsyncCheckAppointmentsTask")
        self.bot_type = bot_type
        logging.info(f"Starting {self.bot_type} task")

        if self.bot_type == "RWTH":
            self.url_1 = URL_RWTH_1
            self.url_2 = URL_RWTH_2
            self.url_3 = URL_RWTH_3
        elif self.bot_type == "CIT":
            self.url_1 = URL_CIT_1
            self.url_2 = URL_CIT_2
            self.url_3 = URL_CIT_3
        else:
            raise ValueError(f"Bot type {self.bot_type} is not supported")

        self.bot = bot
        self.chat_members = chat_members
        self._already_sent = False

        self.options = Options()
        # self.options.add_argument("--headless=new")
        # self.options.add_argument("--no-sandbox")
        # self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("start-maximized") # https://stackoverflow.com/a/26283818/1689770
        self.options.add_argument("enable-automation") # https://stackoverflow.com/a/43840128/1689770
        self.options.add_argument("--headless") # only if you are ACTUALLY running headless
        self.options.add_argument("--no-sandbox") #https://stackoverflow.com/a/50725918/1689770
        self.options.add_argument("--disable-dev-shm-usage") #https://stackoverflow.com/a/50725918/1689770
        self.options.add_argument("--disable-browser-side-navigation") #https://stackoverflow.com/a/49123152/1689770
        self.options.add_argument("--disable-gpu")
        if getpass.getuser() == "mackostya":
            executable_path = "/usr/bin/chromedriver"
        else:
            executable_path = "/usr/bin/chromedriver"
        self.service = Service(executable_path=executable_path)
        self.loop = asyncio.new_event_loop()

    async def async_get_from_web_selenium(self):
        try:
            driver = webdriver.Chrome(service=self.service, options=self.options)
            driver.get(self.url_1)
            await asyncio.sleep(3)
            cookie = driver.find_element(by="id", value="cookie_msg_btn_yes")
            cookie.click()
            await asyncio.sleep(2)
            driver.get(self.url_2)
            await asyncio.sleep(2)

            driver.get(self.url_3)
            element = driver.find_element(by="id", value="suggest_location_content")
            element = element.find_element(by=By.NAME, value="select_location")
            element.click()
            # driver.save_screenshot("imgs/screenshot.png")
            await asyncio.sleep(2)
            page = driver.page_source
        except Exception as e:
            logging.info(f"\n\nWhile getting the data from web an Exception occured: {e}\n\n")
            return DEFAULT_TITLE_RESPONSE, DEFAULT_TEXT
        
        try:
            soup = BeautifulSoup(page, "html.parser")
            inhalt = soup.find(id="inhalt")
            title_element = inhalt.find("h1")
            main = soup.find("main")
            text_element = main.find(string=DEFAULT_TEXT)
        except Exception as e:
            logging.info(f"\n\nWhile decoding the page an Exception occured: {e}\n\n")
            return DEFAULT_TITLE_RESPONSE, DEFAULT_TEXT


        return title_element.text, str(text_element)

    async def async_is_non_default_output(self, title: str, text: str):
        if (title != DEFAULT_TITLE_RESPONSE) or (text != DEFAULT_TEXT):
            return True
        else:
            if self._already_sent:
                logging.info("No appointmetns available anymore:(")
                text = "No appointmetns available anymore:(\nI will let you know when there will be some."
                await self._async_send_message_to_all(text)
                self._already_sent = False
            return False

    async def _async_send_message_to_all(self, text):
        chat_ids = self.chat_members.get_chat_ids()
        for id in chat_ids.keys():
            if chat_ids[id]:
                try:
                    await send_message(self.bot, id, text)
                except Exception as e:
                    logging.error(f"Could not send message to {id}, due to: {e}")

    async def async_task(self):
        while True:
            logging.info("Attempting to get data")
            title, text = await self.async_get_from_web_selenium()
            logging.info("Got title: " + str(title))
            if await self.async_is_non_default_output(title, text):
                logging.info(f"Appointment available! {title}")
                text = f"OMG, there is a new appointment, go check right now!!!\n{self.url_1}"
                if not self._already_sent:
                    await self._async_send_message_to_all(text)
                    self._already_sent = True
            time_to_wait = random.randint(60, 120)  # between 2 and 4 minutes
            await asyncio.sleep(time_to_wait)

    def run(self):
        self.loop.run_until_complete(self.async_task())
