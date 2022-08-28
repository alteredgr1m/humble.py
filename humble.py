#!/usr/bin/env python3

import argparse
from datetime import date
import requests as req
import json
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager


def parse_filename_from(header: str) -> str:
    filename = header.split(" ")[1]
    start = filename.find("\"") + 1
    end = filename.find("\"", start)
    return filename[start:end]


def parse_timestamp(timestamp: str) -> date:
    timestamp = timestamp.split("/")
    day, month, year = [int(digit) for digit in timestamp]
    return date(year, month, day)


def get_driver_path(driver: webdriver, drivers_path: Path) -> str:
    if not drivers_path.exists():
        driver["manager"](path=drivers_path).install()

    with open(drivers_path, "r") as drivers_file:
        drivers = json.load(drivers_file)

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


def setup_browser(settings: dict) -> webdriver:
    browsers = {
        "chrome": {
            "options": ChromeOptions,
            "manager": ChromeDriverManager,
            "service": ChromeService,
            "name": "chromedriver",
            "webdriver": webdriver.Chrome
        },
        "firefox": {
            "options": FirefoxOptions,
            "manager": GeckoDriverManager,
            "service": FirefoxService,
            "name": "geckodriver",
            "webdriver": webdriver.Firefox
        }
    }

    print("- Setting up the browser.")

    browser = browsers[settings["browser"]]

    driver_path = get_driver_path(browser, settings["drivers_path"])

    browser_options = browser["options"]()
    browser_options.headless = settings["headless"]

    return browser["webdriver"](
        options=browser_options,
        service=browser["service"](executable_path=driver_path)
    )


def get_bundle(settings: dict) -> dict:
    path = settings["download_path"] / "bundle.json"

    print("- Fetching the bundle.")

    if path.exists():
        print("- Opening bundle.json from download destination.")
        with open(path, "r") as bundle:
            bundle = json.load(bundle)
        return bundle

    browser = setup_browser(settings)
    browser.get(settings["url"])

    name = browser.title.split("(")[0].strip()

    elements = browser.find_elements(By.LINK_TEXT, settings["format"])

    links = []

    for element in elements:
        link = element.get_attribute("href")
        links.append(link)

    browser.close()

    bundle = {
        "name": name,
        "links": links
    }

    with open(path, "w") as bundle_file:
        print("- Creating bundle.json in download destination.")
        json.dump(bundle, bundle_file)

    return bundle


def download_bundle(settings: dict, bundle: dict) -> None:
    name = bundle["name"]
    links = bundle["links"]
    link_count = len(links)
    link_counter = 1
    successes = 0
    path = settings["download_path"] / name

    if not path.exists():
        path.mkdir()

    print(f"- Downloading {len(links)} books.")

    for link in links:
        res = req.get(link)

        filename = parse_filename_from(res.headers["Content-Disposition"])

        message = f"- Downloading {filename} [{link_counter} / {link_count}]"

        print(message)

        if res.status_code == 200:
            book_path = path / filename

            with open(book_path, "wb") as book_file:
                book_file.write(res.content)

            print(f"{message} successful.")

            successes += 1
        else:
            print(f"{message} unsuccessful.")

        link_counter += 1

        print(f"- Downloaded {successes} out of {link_count} books.")


argparser = argparse.ArgumentParser()

argparser.add_argument("-b",
                       "--browser",
                       choices=["chrome", "firefox"],
                       dest="browser",
                       help="to use",
                       required=True,
                       type=str)

argparser.add_argument("-p",
                       "--path",
                       default=Path.cwd() / "drivers/downloads",
                       dest="download_path",
                       help="to download books to (Example: ~/Downloads)",
                       type=str)

argparser.add_argument("-u",
                       "--url",
                       dest="url",
                       help="to scrape",
                       required=True,
                       type=str)

argparser.add_argument("-f",
                       "--format",
                       default="PDF",
                       dest="format",
                       help="to download books in (PDF/EPUB/MOBI/CBZ)",
                       type=str)

argparser.add_argument("-hl",
                       "--headless",
                       default=True,
                       dest="headless",
                       help="run browser in headless mode",
                       type=bool)


user_settings = vars(argparser.parse_args())

user_settings["driver_path"] = Path.cwd() / "drivers"
user_settings["drivers_path"] = user_settings["driver_path"] / ".wdm/drivers.json"
user_settings["download_path"] = user_settings["download_path"].expanduser()

download_bundle(user_settings, get_bundle(user_settings))
