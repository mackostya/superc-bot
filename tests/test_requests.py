import requests
import time
from bs4 import BeautifulSoup

userName = {"userName":"Kosta"}
location = {"location":"Aachen"}

title_text = " Schritt 3: Keine Terminvorschläge verfügbar "
default_text = "Für die aktuelle Anliegenauswahl ist leider kein Termin verfügbar. Neue Termine werden täglich freigeschaltet. Bitte versuchen Sie die Terminbuchung zu einem späteren Zeitpunkt erneut."

URL1 = "https://termine.staedteregion-aachen.de/auslaenderamt/"
URL2 = "https://termine.staedteregion-aachen.de/auslaenderamt/select2?md=1"
URL3 = "https://termine.staedteregion-aachen.de/auslaenderamt/suggest?cnc-191=1&loc=28"
#URLTEST = "https://termine.staedteregion-aachen.de/auslaenderamt/suggest?mdt=73&select_cnc=1&cnc-204=1&cnc-205=0&cnc-198=0&cnc-201=0&cnc-202=0&cnc-224=0&cnc-189=0&cnc-203=0&cnc-196=0&cnc-200=0&cnc-199=0&cnc-188=0&cnc-186=0&cnc-193=0&cnc-183=0&cnc-184=0&cnc-185=0&cnc-187=0&cnc-190=0&cnc-195=0&cnc-191=0&cnc-194=0&cnc-197=0&cnc-192=0"
#URL4 = "https://termine.staedteregion-aachen.de/auslaenderamt/suggest?mdt=73&select_cnc=1&cnc-204=0&cnc-205=0&cnc-198=0&cnc-201=0&cnc-202=0&cnc-224=0&cnc-189=0&cnc-203=0&cnc-196=0&cnc-200=0&cnc-199=0&cnc-188=0&cnc-186=0&cnc-193=0&cnc-183=0&cnc-184=0&cnc-185=0&cnc-187=0&cnc-190=0&cnc-195=0&cnc-191=1&cnc-194=0&cnc-197=0&cnc-192=0"
print("Start accessing the links")

for i in range(3):
    print("Attempt ", i)
    s = requests.Session()
    s.get(URL1)
    time.sleep(5)
    s.get(URL2)
    time.sleep(5)
    page = s.get(URL3)
    s.close()

    soup = BeautifulSoup(page.content, "html.parser")
    inhalt = soup.find(id="inhalt")
    title_element = inhalt.find("h1")
    print("Title element:\n", title_element.text)
    # print(title_element.text == title_text)

    inhalt = soup.find("main")
    text = inhalt.find(string = default_text)
    print("Default text is the same: ", str(text) == default_text)

