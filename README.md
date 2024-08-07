# Ausländerbehörde appointments bot

 Bot for the appoiuntments at SuperC for the Ausländerbehörde. Since it is barely possible to get an appointment online, this bot will check the website for available appointments and send you a notification via Telegram.

## Installation

1. Clone the repository
2. Install the requirements with `pip install -r requirements.txt`
3. Create a Telegram bot with the [BotFather](https://t.me/botfather) and copy the token to the variable **bot_token** in *scripts/telegram_bot.py*
4. Start the bot with `python -m scripts.telegram_bot --bot-type RWTH`

Recommendation: Use a virtual environment for the installation (`python -m venv venv`).

## Usage

If you want to use another implementation, look into **tests/test_playwright.py** or **tests/test_selenium.py**. Mark: playwright library is not perfectly suitable for the RaspberryPi 3B+, that is why the main bot is written with **requests** or **selenium**. 

## Chromedriver

### MacOS

Install chromedriver:
    
```
brew install --cask chromedriver
```

### RPI Ubuntu

Install chromedriver on Ubuntu Server RPI3 ARM 64:

```
sudo apt-get install chromium-chromedriver
```

Check where is the chromedriver

```
which chromedriver
```

Example output **/usr/bin/chromedriver**

Got to **/usr/bin/** and update the rights:

```
chmod 777 /usr/bin/chromedriver
```

Eventually maybe restart the RPI.

For more information refer to:
- [Blog](https://ivanderevianko.com/2020/01/selenium-chromedriver-for-raspberrypi)
- [Stackoverflow](https://stackoverflow.com/questions/22476112/using-chromedriver-with-selenium-python-ubuntu)