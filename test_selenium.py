import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service

#driver = webdriver.Chrome(service = service)  # Optional argument, if not specified will search path.

service = Service(executable_path="/usr/bin/chromedriver")
driver = webdriver.Chrome(service = service)

driver.get("https://www.selenium.dev/selenium/web/web-form.html")
time.sleep(5) # Let the user actually see something!

driver.save_screenshot('screen.png')
time.sleep(5) # Let the user actually see something!

driver.quit()