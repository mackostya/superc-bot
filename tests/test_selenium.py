import time
import logging

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

DEFAULT_TITLE = " Schritt 4 von 6: Terminvorschläge - Keine Zeiten verfügbar "
DEFAULT_TEXT = "Für die aktuelle Anliegenauswahl ist leider kein Termin verfügbar. Neue Termine werden täglich freigeschaltet. Bitte versuchen Sie die Terminbuchung zu einem späteren Zeitpunkt erneut."
URL_RWTH_1 = "https://termine.staedteregion-aachen.de/auslaenderamt/"
URL_RWTH_2 = "https://termine.staedteregion-aachen.de/auslaenderamt/select2?md=1"
URL_RWTH_3 = "https://termine.staedteregion-aachen.de/auslaenderamt/location?mdt=91&select_cnc=1&cnc-299=0&cnc-300=0&cnc-293=0&cnc-296=0&cnc-297=0&cnc-301=0&cnc-284=0&cnc-298=0&cnc-291=0&cnc-285=0&cnc-282=0&cnc-283=0&cnc-303=0&cnc-281=0&cnc-287=0&cnc-286=1&cnc-289=0&cnc-292=0&cnc-288=0&cnc-279=0&cnc-280=0&cnc-290=0&cnc-295=0&cnc-294=0"

URL_CIT_1 = "https://termine.staedteregion-aachen.de/auslaenderamt/"
URL_CIT_2 = "https://termine.staedteregion-aachen.de/auslaenderamt/select2?md=2"
URL_CIT_3 = "https://termine.staedteregion-aachen.de/auslaenderamt/location?mdt=66&select_cnc=1&cnc-211=1"


def test_rwth(type="RWTH"):
    logging.basicConfig(
        format="[TEST] %(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )
    logging.info("Starting Selenium RWTH Test" if type == "RWTH" else "Starting Selenium CIT Test")

    options = Options()
    # options.add_argument("--headless=new")
    # options.add_argument("--no-sandbox")
    # options.add_argument("--disable-dev-shm-usage")
    options.add_argument("start-maximized") # https://stackoverflow.com/a/26283818/1689770
    options.add_argument("enable-automation") # https://stackoverflow.com/a/43840128/1689770
    options.add_argument("--headless") # only if you are ACTUALLY running headless
    options.add_argument("--no-sandbox") #https://stackoverflow.com/a/50725918/1689770
    options.add_argument("--disable-dev-shm-usage") #https://stackoverflow.com/a/50725918/1689770
    options.add_argument("--disable-browser-side-navigation") #https://stackoverflow.com/a/49123152/1689770
    options.add_argument("--disable-gpu")
    service = Service(executable_path="/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)
    
    driver.get(URL_RWTH_1 if type == "RWTH" else URL_CIT_1)
    time.sleep(3)  # Let the user actually see something!
    logging.info("Got first url")
    driver.save_screenshot("imgs/screenshot_1.png")

    cookie = driver.find_element(by="id", value="cookie_msg_btn_yes")
    cookie.click()
    logging.info("Got rid of the cookie")

    time.sleep(2)
    driver.get(URL_RWTH_2 if type == "RWTH" else URL_CIT_2)
    logging.info("Got second url")
    driver.save_screenshot("imgs/screenshot_2.png")

    time.sleep(2)
    driver.get(URL_RWTH_3 if type == "RWTH" else URL_CIT_3)
    logging.info("Got third url")

    element = driver.find_element(by="id", value="suggest_location_content")
    element = element.find_element(by=By.NAME, value="select_location")
    element.click()
    driver.save_screenshot("imgs/screenshot_3.png")

    time.sleep(2)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    inhalt = soup.find(id="inhalt")
    title_element = inhalt.find("h1")
    driver.quit()

    logging.info(title_element.text)
    logging.info(title_element.text == DEFAULT_TITLE)
    main = soup.find("main")
    text_element = main.find(string=DEFAULT_TEXT)
    logging.info(text_element)


if __name__ == "__main__":
    test_rwth("RWTH")
