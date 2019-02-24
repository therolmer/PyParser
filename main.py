from bs4 import BeautifulSoup
from threading import Event, Thread
from selenium import webdriver
from selenium.common.exceptions import SessionNotCreatedException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from collections import namedtuple
import os

#from selenium.webdriver.chrome.options import Options

import requests

OneItem = namedtuple("OneItem", "url name price")

reismus220V = OneItem("https://velikiy-novgorod.220-volt.ru/catalog-12575/", "Рейсмус", 0)
tokarStanok220V = OneItem("https://velikiy-novgorod.220-volt.ru/catalog-330153/", "Токарный станок", 0)
reismusVI = OneItem("https://novgorod.vseinstrumenti.ru/stanki/strogalnye/rejsmusno-fugovalnye/makita/2012-nb/", "Рейсмус", 0)

requestTimeout = 15;

WINDOW_SIZE = "1920,1080"


def init_driver():

    #print (os.path.abspath(os.curdir))

    ff = "geckodriver.exe"
    firefox_options = Options()
    firefox_options.headless = True

    firefox_profile = FirefoxProfile()
    firefox_profile.set_preference("permissions.default.stylesheet", 2);
    firefox_profile.set_preference("permissions.default.image", 2);

    #chrome_options.add_argument("--disable-gpu")
    #chrome_options.add_argument("--no-sandbox")
    #prefs = {"profile.managed_default_content_settings.images": 2}
    #chrome_options.add_argument("headless")
    #chrome_options.add_experimental_option("prefs", prefs)

    try:
        #driver = webdriver.firefox(executable_path=ff, options=chrome_options)
        driver = webdriver.Firefox(executable_path=ff, options=firefox_options, firefox_profile = firefox_profile)

    except SessionNotCreatedException:
        print("Ошибка инициализации браузера. Скорее всего у вас не установлен браузер. Пожалуйста обратитесь к разработчику парсера")

    driver.set_window_size(1200, 600)
    return driver

def ParseVseIntrumenti(driver, item):
    driver.get(item.url)
    price = driver.find_elements_by_class_name("price-value")
    itemPrice = (int)(price[0].text.replace(" ", ""))

    if itemPrice != item.price:
        print("Все инструменты " + item.name + " " + str(itemPrice))
        item = item._replace(price=itemPrice)

    return item


def Parse220v(item):
    page_response = requests.get(item.url, timeout=requestTimeout)
    page_content = BeautifulSoup(page_response.content, "html.parser")
    itemPrice = (int)(page_content.find(id="price_per_m").text.replace(" ", ""))

    if itemPrice != item.price:
        print("220V " + item.name + " " + str(itemPrice))
        item=item._replace(price=itemPrice)

    return item

chromeDriver = init_driver()


def parse():
    global reismus220V
    reismus220V = Parse220v(reismus220V)

    global reismusVI
    ParseVseIntrumenti(chromeDriver, reismusVI)

    global tokarStanok220V
    tokarStanok220V = Parse220v(tokarStanok220V)

class MyThread(Thread):
    def __init__(self, event):
        Thread.__init__(self)
        self.stopped = event

    def run(self):
        while not self.stopped.wait(60):
            parse()
            # call a function

stopFlag = Event()
thread = MyThread(stopFlag)
thread.start()
# this will stop the timer
#stopFlag.set()

#chromeDriver.quit()

