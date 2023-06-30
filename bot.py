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

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

BOT_TOKEN="YOUR_TOKEN_HERE"

bot = telebot.TeleBot(BOT_TOKEN)

flag = True

USERS_FILE = "users.json"

URL1 = "https://termine.staedteregion-aachen.de/auslaenderamt/"
URL2 = "https://termine.staedteregion-aachen.de/auslaenderamt/select2?md=1"
URL3 = "https://termine.staedteregion-aachen.de/auslaenderamt/suggest?cnc-191=1&loc=28"

DEFAULT_TITLE_RESPONSE = " Schritt 3: Keine Terminvorschläge verfügbar "
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
                bot.send_message(chat_id=id, text='Good Morning!\nHopefully more Luck this day :)')
            except telebot.apihelper.ApiTelegramException:
                write_to_file("id: " + str(id) + " was blocking the sending")

    def run(self):
        while True:
            schedule.run_pending()
            time.sleep(1)


class CheckAppointmentsTask(threading.Thread):
    def __init__(self):
        super(CheckAppointmentsTask, self).__init__(name="CheckAppointmentsThread")
        
    def get_from_web(self):
        try:
            with requests.Session() as s:
                s.get(URL1)
                time.sleep(TIME_SLEEP_BTW_URLS)
                
                s.get(URL2)
                time.sleep(TIME_SLEEP_BTW_URLS)
                
                page = s.get(URL3)
                s.close()
        except Exception as e:
            write_to_file(f"\n\nWhile getting the data from web an Exceptionoccured: {e}\n\n")
            return DEFAULT_TITLE_RESPONSE, DEFAULT_TEXT
        
        soup = BeautifulSoup(page.content, "html.parser")
        inhalt = soup.find(id="inhalt")
        title_element = inhalt.find("h1")
        
        main = soup.find("main")
        text_element = main.find(string = DEFAULT_TEXT)
        
        return title_element.text, str(text_element)

    def get_from_web_playwright(self):
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(URL1)
            page.get_by_role("button").get_by_text("Akzeptieren").click()
            page.get_by_role("button").get_by_text("Aufenthaltsangelegenheiten").click()
            page.get_by_role("tablist").get_by_text("RWTH - Außenstelle Super C").click()
            page.locator("#button-plus-191").click()
            page.locator("#WeiterButton").click()
            page.get_by_role("button").get_by_text("OK").click()
            time.sleep(3)
            # page.screenshot(path=f'imgs/screenshot.png', full_page=True)
            title_text = page.locator("#inhalt").get_by_text("Schritt 3").text_content()
            browser.close()
            return title_text
        
    def send_OMG_message(self):
        for id in chat_ids.keys():
            if chat_ids[id]:
                try:
                    bot.send_message(chat_id=id, text=f'OMG, there is a new appointment, go check right now!!!\n{URL1}')
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
            write_to_file(date + " : " + "Attemptig to get data")
            title, text = self.get_from_web()
            write_to_file(date + " : " + "Got title: " + str(title))
            if self.is_non_default_output(title, text):
                write_to_file(date + " : " + title)
                self.send_OMG_message()
            time_to_wait = random.randint(120, 240) # between 2 and 4 minutes
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
        d[message.from_user.username] = message.from_user.id
        json_object = json.dumps(d)
        file.write(json_object)

def add_user(message, already_in_use = False):
    chat_ids[message.from_user.id] = already_in_use
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

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    if message.from_user.id not in chat_ids:
        add_user(message)
    bot.reply_to(message, "Hi, I am your assistant for the appointments at SuperC Ausländeramt. I am now searching for the appointments for you. \
I check if there are any updates on the website every 2-4 minutes.\n\
If you want to stop sending just write /stop.\n\
If you want me to restart, after you've stopped me, please write /start_checking.\n\
I hope I will be able to help you:)")

@bot.message_handler(commands=['start_checking'])
def loop(message):
    global flag
    flag = True
    
    if message.from_user.id not in chat_ids.keys():
        add_user(message)
    
    #check if the user is already using this option
    if chat_ids[message.from_user.id]:
        bot.reply_to(message, "I'm already working on it for you")
    else:
        chat_ids[message.from_user.id] = True
        bot.reply_to(message, "Thanks, now I am checking every 2-4 minutes for new appointments. As soon as I will find anything, I will let you know😉")

@bot.message_handler(commands=['admin_start_update'])
def start_admin_update(message):
    for id in chat_ids.keys():
        try:
            bot.send_message(chat_id=id, text='I am now in the process of the update, so I might not be working for a while\nI will tell you when my software is up to date:)')
        except telebot.apihelper.ApiTelegramException:
            write_to_file("id: " + str(id) + " was blocking the sending")

@bot.message_handler(commands=['admin_finish_update'])
def finish_admin_update(message):
    for id in chat_ids.keys():
        try:
            bot.send_message(chat_id=id, text='I am finished with an update, and I am glad to be searching for appointments for you.\n\nAfter this update I do not run the script every 30s but every 2 to 4 minutes. Furthermore I hope to be more robust now.\n\nIf you want me to search, please type \n/start_checking\nonce again :)\n\nBTW, sorry for the inconvenience with multiple restarts:)')
        except telebot.apihelper.ApiTelegramException:
            write_to_file("id: " + str(id) + " was blocking the sending")
@bot.message_handler(commands=['admin_stop'])
def admin_stop(message):
    global flag
    flag = False
    write_to_file(f"{message.from_user.first_name} did an admin stop")
    bot.reply_to(message, "If you are not an admin, please don't use this option. This option stops the check for every user.")

@bot.message_handler(commands=['stop'])
def stop(message):
    chat_ids[message.from_user.id] = False
    write_to_file(f"{message.from_user.first_name} wanted to stop:(")
    bot.reply_to(message, "I will not be sending you any updates to this topic anymore😢")

#####################################################################################
###################################### MAIN #########################################
#####################################################################################

if __name__=="__main__":
    write_to_file("Starting a bot")
    init_chat_ids()
    ScheduleTask()
    while True:
        try:
            check_task = CheckAppointmentsTask()
            check_task.start()
            telebot.apihelper.RETRY_ON_ERROR = True
            bot.infinity_polling(timeout=60, long_polling_timeout = 30)
            assert True==False, "The end of the code was achieved, something went wrong"
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

            