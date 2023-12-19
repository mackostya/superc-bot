import time
import threading
import random
import asyncio
import logging

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


class CheckAppointmentsTask(threading.Thread):
    def __init__(self, bot, chat_members: ChatMembers, bot_type: str):
        super(CheckAppointmentsTask, self).__init__(name="CheckAppointmentsTask")
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
        self.options.add_argument("--headless=new")
        self.service = Service(executable_path="/usr/local/bin/chromedriver")

    def get_from_web_selenium(self):
        try:
            driver = webdriver.Chrome(service=self.service, options=self.options)
            driver.get(self.url_1)
            time.sleep(3)
            cookie = driver.find_element(by="id", value="cookie_msg_btn_yes")
            cookie.click()
            time.sleep(2)
            driver.get(self.url_2)
            time.sleep(2)

            driver.get(self.url_3)
            element = driver.find_element(by="id", value="suggest_location_content")
            element = element.find_element(by=By.NAME, value="select_location")
            element.click()
            driver.save_screenshot("imgs/screenshot.png")
            time.sleep(2)
            page = driver.page_source
            driver.quit()
        except Exception as e:
            logging.info(f"\n\nWhile getting the data from web an Exception occured: {e}\n\n")
            return DEFAULT_TITLE_RESPONSE, DEFAULT_TEXT

        soup = BeautifulSoup(page, "html.parser")
        inhalt = soup.find(id="inhalt")
        title_element = inhalt.find("h1")

        main = soup.find("main")
        text_element = main.find(string=DEFAULT_TEXT)

        return title_element.text, str(text_element)

    def _send_message_to_all(self, text: str):
        if not self._already_sent:
            chat_ids = self.chat_members.get_chat_ids()
            loop = asyncio.new_event_loop()
            for id in chat_ids.keys():
                if chat_ids[id]:
                    try:
                        loop.run_until_complete(send_message(self.bot, id, text))
                    except Exception as e:
                        logging.error(f"Could not send message to {id}, due to: {e}")
            time.sleep(10)
            loop.close()
            self._already_sent = True

    def is_non_default_output(self, title: str, text: str):
        if (title != DEFAULT_TITLE_RESPONSE) or (text != DEFAULT_TEXT):
            return True
        else:
            if self._already_sent:
                text = "No appointmetns available anymore:(\nI will let you know when there will be some."
                self._send_message_to_all(text)
            self._already_sent = False
            return False

    def run(self):
        while True:
            logging.info("Attemptig to get data")
            title, text = self.get_from_web_selenium()
            logging.info("Got title: " + str(title))
            if self.is_non_default_output(title, text):
                logging.info(title)
                text = f"OMG, there is a new appointment, go check right now!!!\n{self.url_1}"
                self._send_message_to_all(text)
            time_to_wait = random.randint(120, 240)  # between 2 and 4 minutes
            time.sleep(time_to_wait)
