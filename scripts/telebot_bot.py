import os
import time
import telebot
import requests
import threading
import schedule
import datetime
import json
import random
import urllib3
from telebot import types

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup

BOT_TOKEN = ""

bot = telebot.TeleBot(BOT_TOKEN)

flag = True

USERS_FILE = "users.json"

URL1 = "https://termine.staedteregion-aachen.de/auslaenderamt/"
URL2 = "https://termine.staedteregion-aachen.de/auslaenderamt/select2?md=1"
URL3 = "https://termine.staedteregion-aachen.de/auslaenderamt/suggest?mdt=75&select_cnc=1&cnc-204=0&cnc-205=0&cnc-198=0&cnc-201=0&cnc-202=0&cnc-227=0&cnc-189=0&cnc-203=0&cnc-196=0&cnc-190=0&cnc-185=0&cnc-187=0&cnc-188=0&cnc-186=0&cnc-192=0&cnc-191=1&cnc-194=0&cnc-197=0&cnc-193=0&cnc-183=0&cnc-184=0&cnc-195=0&cnc-200=0&cnc-225=0"

DEFAULT_TITLE_RESPONSE = " Schritt 3 von 5 : Terminvorschläge - Keine Zeiten verfügbar "
DEFAULT_TEXT = "Für die aktuelle Anliegenauswahl ist leider kein Termin verfügbar. Neue Termine werden täglich freigeschaltet. Bitte versuchen Sie die Terminbuchung zu einem späteren Zeitpunkt erneut."

TIME_SLEEP_BTW_URLS = 5
TIME_SLEEP_BTW_RQSTS = 30

chat_ids = {}

#####################################################################################
##################################### UTILS #########################################
#####################################################################################


class ScheduleTask(threading.Thread):
    def __init__(self):
        super(ScheduleTask, self).__init__(name="GoodMorningThread")
        schedule.every().day.at("08:00").do(self.send_daily_message)
        self.start()

    def send_daily_message(self):
        for id in chat_ids.keys():
            try:
                bot.send_message(chat_id=id, text="Good Morning!\nHopefully more Luck this day :)")
            except telebot.apihelper.ApiTelegramException:
                write_to_file("id: " + str(id) + " was blocking the sending")

    def run(self):
        while True:
            schedule.run_pending()
            time.sleep(1)


class CheckAppointmentsTask(threading.Thread):
    def __init__(self):
        super(CheckAppointmentsTask, self).__init__(name="CheckAppointmentsThread")
        self.options = Options()
        self.options.add_argument("--headless=new")
        self.service = Service(executable_path="/usr/bin/chromedriver")

    def get_from_web_selenium(self):
        try:
            driver = webdriver.Chrome(service=self.service, options=self.options)
            driver.get(URL1)
            time.sleep(3)

            cookie = driver.find_element(by="id", value="cookie_msg_btn_yes")
            cookie.click()
            time.sleep(2)

            driver.get(URL2)
            time.sleep(2)

            driver.get(URL3)
            WebDriverWait(driver, 20).until(
                expected_conditions.visibility_of_element_located((By.NAME, "select_location"))
            )
            element = driver.find_element(by=By.NAME, value="select_location")
            element.click()
            time.sleep(2)
            page = driver.page_source
            driver.quit()
        except Exception as e:
            write_to_file(f"\n\nWhile getting the data from web an Exception occured: {e}\n\n")
            return DEFAULT_TITLE_RESPONSE, DEFAULT_TEXT

        soup = BeautifulSoup(page, "html.parser")
        inhalt = soup.find(id="inhalt")
        title_element = inhalt.find("h1")

        main = soup.find("main")
        text_element = main.find(string=DEFAULT_TEXT)

        return title_element.text, str(text_element)

    def send_OMG_message(self):
        for id in chat_ids.keys():
            if chat_ids[id]:
                try:
                    bot.send_message(
                        chat_id=id, text=f"OMG, there is a new appointment, go check right now!!!\n{URL1}"
                    )
                except telebot.apihelper.ApiTelegramException:
                    write_to_file("id: " + str(id) + " was blocking the sending")

    def is_non_default_output(self, title, text):
        if (title != DEFAULT_TITLE_RESPONSE) or (text != DEFAULT_TEXT):
            return True
        else:
            return False

    def run(self):
        global flag
        flag = True
        while flag:
            date = str(datetime.datetime.now())
            write_to_file(date + " : " + "Attemptnig to get data")
            title, text = self.get_from_web_selenium()
            write_to_file(date + " : " + "Got title: " + str(title))
            if self.is_non_default_output(title, text):
                write_to_file(date + " : " + title)
                self.send_OMG_message()
            time_to_wait = random.randint(120, 240)  # between 2 and 4 minutes
            time.sleep(time_to_wait)


def init_chat_ids():
    if os.path.isfile(USERS_FILE):
        with open(USERS_FILE, "r") as file:
            d = json.load(file)
            write_to_file("Existing users: " + str(d))
            for id in d.values():
                chat_ids[id] = True


def write_to_file(txt):
    print(txt)
    file = open("log.txt", "a")
    file.write(txt + "\n")
    file.close()


def add_user_to_json(message):
    d = {}
    if os.path.isfile(USERS_FILE):
        with open(USERS_FILE, "r") as file:
            d = json.load(file)
    with open(USERS_FILE, "w") as file:
        if (
            (message.from_user.username == None)
            or (message.from_user.username == "")
            or (message.from_user.username == "null")
        ):
            d["noname_" + str(random.randint(4, 100000))] = message.from_user.id
        else:
            d[message.from_user.username] = message.from_user.id
        json_object = json.dumps(d)
        file.write(json_object)


def add_user(message, start_to_check=True):
    chat_ids[message.from_user.id] = start_to_check
    date = str(datetime.datetime.now())
    txt = f"""
    ===== we have a new user! =====
    User id: {message.from_user.id}
    Name : {message.from_user.first_name}
    Username: {message.from_user.username}
    Time joined: {date} 
    ===============================
    """
    add_user_to_json(message)
    write_to_file(txt)


#####################################################################################
################################## BOT REQUESTS #####################################
#####################################################################################


@bot.message_handler(commands=["start", "hello"])
def send_welcome(message):
    if message.from_user.id not in chat_ids:
        add_user(message)
        bot.reply_to(
            message,
            "Hi, I am your assistant for the appointments at SuperC Ausländeramt. I am now searching for the appointments for students. \
I check if there are any updates on the website every 2-4 minutes.\n\
If you want me to stop sending you updates just write /stop.\n\
If you want me to restart, after you've stopped me, please write /restart.\n\
I hope I will be able to help you:)",
        )
    else:
        bot.reply_to(
            message, "Hey, I think we've already met :)\nIf you want to know what I can do, please write /help"
        )


@bot.message_handler(commands=["help"])
def send_help(message):
    bot.reply_to(
        message,
        "Here is what you need to know: \
I check if there are any updates on the website every 2-4 minutes.\n\
If you want to stop sending just write /stop.\n\
If you want me to restart, after you've stopped me, please write /restart.\n\
I hope I will be able to help you:)",
    )


@bot.message_handler(commands=["restart"])
def loop(message):
    global flag
    flag = True

    if message.from_user.id not in chat_ids.keys():
        add_user(message)

    # check if the user is already using this option
    if chat_ids[message.from_user.id]:
        bot.reply_to(message, "I'm already working on it for you")
    else:
        chat_ids[message.from_user.id] = True
        bot.reply_to(
            message,
            "Thanks, now I am checking every 2-4 minutes for new appointments. As soon as I will find anything, I will let you know😉,
        )
)

@bot.message_handler(commands=["admin_start_update"])
def start_admin_update(message):
    for id in chat_ids.keys():
        try:
            bot.send_message(
                chat_id=id,
                text="I am now in the process of the update, so I might not be working for a while\nI will tell you when my software is up to date:)",
            )
        except telebot.apihelper.ApiTelegramException:
            write_to_file("id: " + str(id) + " was blocking the sending")


@bot.message_handler(commands=["admin_finish_update"])
def finish_admin_update(message):
    for id in chat_ids.keys():
        try:
            bot.send_message(
                chat_id=id,
                text="I am finished with an update, and I am glad to be searching for appointments for you.\n\n \
After this update I can tackle the new website changes, so I hope I will be able to help you even more:)\n \
BTW, for some of you I stopped working after a while, highly probable because you got replaced by other users :(\
This should not be the problem now, I hope. I changed:)\
If you forget the commands, just write /help, but I mean, it is pretty straight forward :)",
            )
        except telebot.apihelper.ApiTelegramException:
            write_to_file("id: " + str(id) + " was blocking the sending")


@bot.message_handler(commands=["admin_stop"])
def admin_stop(message):
    global flag
    flag = False
    write_to_file(f"{message.from_user.first_name} did an admin stop")
    bot.reply_to(
        message, "If you are not an admin, please don't use this option. This option stops the check for every user."
    )


@bot.message_handler(commands=["stop"])
def stop(message):
    chat_ids[message.from_user.id] = False
    write_to_file(f"{message.from_user.first_name} wanted to stop:(")
    bot.reply_to(message, "I will not be sending you any updates to this topic anymore😢"
)

@bot.message_handler(regexp="Helpful")
def helpful(message):
    print(message.from_user.id)
    markup = types.ReplyKeyboardRemove(selective=False)
    write_to_file(f"{message.from_user.first_name} found bot helpful:)")
    bot.send_message(
        message.from_user.id, "Thank you for your feedback! I'm glad I could help you!", reply_markup=markup
    )


@bot.message_handler(regexp="Not that much")
def not_helpul(message):
    print(message.from_user.id)
    markup = types.ReplyKeyboardRemove(selective=False)
    write_to_file(f"{message.from_user.first_name} found bot not helpful:(")
    bot.send_message(message.from_user.id, "Hope my code will be of some help then:)", reply_markup=markup)


#####################################################################################
###################################### MAIN #########################################
#####################################################################################


# ---------------------------      BYE MESSAGE      ---------------------------------#
def send_bye_message():
    markup = types.ReplyKeyboardMarkup(row_width=2)
    itembtn1 = types.KeyboardButton("Helpful")
    itembtn2 = types.KeyboardButton("Not that much:(")
    markup.add(itembtn1, itembtn2)

    msg = "Thanks a lot for using me (the bot). \
Since I already achieved my goal in supplying my author and my authors friends with \
appointments, I finally can rest :) I hope I could as well help some of you, unknown \
guests!\n\
If you are still in need of an appointment, please take a look at me on github: \n\n\
https://github.com/mackostya/superc-bot \n\n\
If you found this bot helpful, please don't hesitate to choose the corresponding box for it and like me \
on github. It will help my author to understand if he should continue developing this type of software or not.\
"
    for id in chat_ids.keys():
        try:
            bot.send_message(chat_id=id, text=msg, reply_markup=markup)
        except telebot.apihelper.ApiTelegramException:
            write_to_file("id: " + str(id) + " was blocking the sending")
    telebot.apihelper.RETRY_ON_ERROR = True
    bot.infinity_polling(timeout=60, long_polling_timeout=30)


# -----------------------------------------------------------------------------------#

if __name__ == "__main__":
    SEND_BYE = True
    write_to_file("Starting a bot")
    init_chat_ids()
    if SEND_BYE:
        # last message :(
        send_bye_message()
    else:
        # normal working day :)
        ScheduleTask()
        while True:
            try:
                check_task = CheckAppointmentsTask()
                check_task.start()
                telebot.apihelper.RETRY_ON_ERROR = True
                bot.infinity_polling(timeout=60, long_polling_timeout=30)
                assert True == False, "The end of the code was achieved, something went wrong"
            except requests.exceptions.ConnectionError or urllib3.exceptions.MaxRetryError:
                check_task.join()
                bot.stop_polling()
                write_to_file(f"Connection error occured, restarting the bot in 30 seconds")
                time.sleep(30)
            except Exception as e:
                check_task.join()
                bot.stop_polling()
                write_to_file(f"Error occured: {e}, restarting the bot in 30 seconds")
                time.sleep(30)
