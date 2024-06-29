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
URL_RWTH_3 = "https://termine.staedteregion-aachen.de/auslaenderamt/location?mdt=88&select_cnc=1&cnc-270=0&cnc-271=0&cnc-264=0&cnc-267=0&cnc-268=0&cnc-272=0&cnc-255=0&cnc-269=0&cnc-262=0&cnc-256=0&cnc-253=0&cnc-254=0&cnc-274=0&cnc-252=0&cnc-258=0&cnc-257=1&cnc-260=0&cnc-263=0&cnc-259=0&cnc-249=0&cnc-250=0&cnc-261=0&cnc-266=0&cnc-265=0"

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
    options.add_argument("--headless=new")
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
