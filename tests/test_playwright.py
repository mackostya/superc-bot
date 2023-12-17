from playwright.sync_api import sync_playwright
import time

URL = "https://termine.staedteregion-aachen.de/auslaenderamt/"

with sync_playwright() as p:
    
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(URL)
    page.get_by_role("button").get_by_text("Akzeptieren").click()
    page.get_by_role("button").get_by_text("Aufenthaltsangelegenheiten").click()
    page.get_by_role("tablist").get_by_text("RWTH - Außenstelle Super C").click()
    page.locator("#button-plus-191").click()
    page.locator("#WeiterButton").click()
    page.get_by_role("button").get_by_text("OK").click()
    time.sleep(3)
    page.screenshot(path=f'imgs/screenshot.png', full_page=True)
    print(page.locator("#inhalt").get_by_text("Schritt 3").text_content())
    browser.close()