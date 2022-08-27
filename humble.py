#!/usr/bin/env python3

import argparse
from datetime import date
import os
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

BROWSERS = {
    "chrome": {
        "manager": ChromeDriverManager,
        "service": ChromeService,
        "name": "chromedriver",
        "webdriver": webdriver.Chrome,
    },
    "firefox": {
        "manager": GeckoDriverManager,
        "service": FirefoxService,
        "name": "geckodriver",
        "webdriver": webdriver.Firefox
    }
}

CWD = os.getcwd()

if os.name == "nt":
    DRIVER_PATH = f"{CWD}\\drivers"
    DRIVERS_PATH = f"{DRIVER_PATH}\\.wdm\\drivers.json"
else:
    DRIVER_PATH = f"{CWD}/drivers"
    DRIVERS_PATH = f"{DRIVER_PATH}/.wdm/drivers.json"


def parse_timestamp(timestamp):
    timestamp = timestamp.split("/")
    day, month, year = [int(n) for n in timestamp]
    return date(year, month, day)


def get_driver_path(driver, drivers_path):
    if not os.path.exists(drivers_path):
        driver["manager"](path=drivers_path).install()

    with open(drivers_path, "r") as drivers_file:
        drivers = json.load(drivers_file)
        drivers_file.close()

    driver_info = {}

    for driver_name in drivers:
        if driver["name"] in driver_name:
            driver_info = drivers[driver_name]

    timestamp = parse_timestamp(driver_info["timestamp"])
    current_t = date.today()

    if current_t.month == timestamp.month:
        return driver_info["binary_path"]
    else:
        driver["manager"](path=drivers_path).install()
        get_driver_path(driver, drivers_path)


argparser = argparse.ArgumentParser()

argparser.add_argument("-b",
                       "--browser",
                       choices=["chrome", "firefox"],
                       dest="browser",
                       help="to use",
                       required=True)

argparser.add_argument("-u",
                       "--url",
                       dest="url",
                       help="to scrape",
                       required=True)

args = argparser.parse_args()

BROWSER = BROWSERS[args.browser]
URL = args.url

driver_path = get_driver_path(BROWSER, DRIVERS_PATH)

browser = BROWSER["webdriver"](service=BROWSER["service"](executable_path=driver_path))

browser.get(URL)

browser.close()
