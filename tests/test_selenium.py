import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup

DEFAULT_TITLE = " Schritt 3 von 5 : Terminvorschläge - Keine Zeiten verfügbar "
DEFAULT_TEXT = "Für die aktuelle Anliegenauswahl ist leider kein Termin verfügbar. Neue Termine werden täglich freigeschaltet. Bitte versuchen Sie die Terminbuchung zu einem späteren Zeitpunkt erneut."
URL1 = "https://termine.staedteregion-aachen.de/auslaenderamt/"
URL2 = "https://termine.staedteregion-aachen.de/auslaenderamt/select2?md=1"
URL3 = "https://termine.staedteregion-aachen.de/auslaenderamt/suggest?mdt=75&select_cnc=1&cnc-204=0&cnc-205=0&cnc-198=0&cnc-201=0&cnc-202=0&cnc-227=0&cnc-189=0&cnc-203=0&cnc-196=0&cnc-190=0&cnc-185=0&cnc-187=0&cnc-188=0&cnc-186=0&cnc-192=0&cnc-191=1&cnc-194=0&cnc-197=0&cnc-193=0&cnc-183=0&cnc-184=0&cnc-195=0&cnc-200=0&cnc-225=0"

print("Starting Selenium Test")

options = Options()
options.add_argument("--headless=new")
service = Service(executable_path="/usr/bin/chromedriver")
driver = webdriver.Chrome(service = service, options=options)
driver.get(URL1)
time.sleep(3) # Let the user actually see something!
cookie = driver.find_element(by="id", value="cookie_msg_btn_yes")
cookie.click()
time.sleep(2)
driver.get(URL2)
time.sleep(2)
driver.get(URL3)
WebDriverWait(driver, 20).until(expected_conditions.visibility_of_element_located((By.NAME, "select_location")))
element = driver.find_element(by=By.NAME, value="select_location")

element.click()

time.sleep(2)
driver.save_screenshot('screen.png')

soup = BeautifulSoup(driver.page_source, "html.parser")
inhalt = soup.find(id="inhalt")
title_element = inhalt.find("h1")
driver.quit()

print(title_element.text)
print(title_element.text == DEFAULT_TITLE)
main = soup.find("main")
text_element = main.find(string = DEFAULT_TEXT)
print(text_element)