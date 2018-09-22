from selenium import webdriver
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import sys
import getopt
import os
from datetime import datetime
from pymongo import MongoClient
import hashlib
import pytz
from app.models.Translink import Translink
from dotenv import load_dotenv, find_dotenv

client = MongoClient('localhost', 27017)
db = client.GoCard
gocard = db.gocard

load_dotenv(dotenv_path=find_dotenv())

download_dir = os.getenv("STORAGE_PATH")

def driver_setup():

    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X)")
    options.add_argument('window-size=800x841')
    options.add_argument('headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    prefs = {'download.prompt_for_download': False,
             'download.directory_upgrade': True,
             "download.default_directory": download_dir,
             'safebrowsing.enabled': False,
             'safebrowsing.disable_download_protection': True}

    options.add_experimental_option('prefs', prefs)

    # driver = webdriver.Chrome(
    #     executable_path="/home/vagrant/driver/chromedriver", chrome_options=options, service_args=['--verbose', '--log-path=/home/vagrant/chromedriver.log'])
    driver = webdriver.Chrome(
        "/Users/williamhenry/Downloads/chromedriver-latest", chrome_options=options)

    translink = Translink.query.filter_by(deleted_at=None).first()

    gocard_number = translink.gocard_number
    password = translink.password

    return {
        'driver': driver,
        'gocard_number': gocard_number,
        'password': password
    }


def run():

    setup = driver_setup()
    driver = setup['driver']
    gocard_number = setup['gocard_number']
    password = setup['password']

    url = "https://gocard.translink.com.au/"
    driver.get(url)

    wait = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, '//input[contains(@value, \"Login\")]'))
    )

    wait = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//input[contains(@id,\"CardNumber\")]"))
    )

    wait = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//input[contains(@id,\"Password\")]"))
    )

    email = driver.find_element_by_xpath(
        "//input[contains(@id,\"CardNumber\")]")

    email.send_keys(gocard_number)  # gocard_number

    pwd = driver.find_element_by_xpath(
        "//input[contains(@id,\"Password\")]")

    pwd.send_keys(password)  # password

    driver.find_element_by_xpath(
        '//input[contains(@value, \"Login\")]').click()

    wait = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//h1[contains(text(),\"Summary of account\")]"))
    )

    tbody = driver.find_element_by_xpath(
        '//table[contains(@id,\"balance-table\")]').find_element_by_tag_name('tbody')

    for row in tbody.find_elements_by_tag_name('tr'):

        cell = row.find_elements_by_tag_name("td")  # the price
        date = ((cell[0]).text).strip()
        price = ((cell[1]).text).strip()

        id_str = hashlib.sha256((date+'_'+price).encode())

        date = datetime.strptime(date, '%d %b %Y %I:%M %p')
        g = gocard.find_one({'id': id_str.hexdigest()})
        if not g:

            gocard.insert(
                {
                    'id': id_str.hexdigest(),
                    'price': price,
                    'date': date,
                    'gocard_number': gocard_number,
                    'created_at': datetime.now(tz=pytz.timezone('Australia/Brisbane'))
                }
            )

    wait = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, '//a[contains(text(),\"History\")]'))
    )

    driver.find_element_by_xpath('//a[contains(text(),\"History\")]').click()

    wait = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, '//h1[contains(text(),\"card history\")]'))
    )

    wait = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, '//select[contains(@id,\'search-period\')]'))
    )

    driver.find_element_by_xpath(
        '//select[contains(@id,\'search-period\')]').click()

    driver.find_element_by_xpath(
        '//option[contains(text(),\'this month\')]').click()

    driver.find_element_by_xpath(
        '(//input[contains(@value,\'Search\')])[2]').click()

    driver.save_screenshot('./test1.png')

    print('clicking the csv button')

    driver.find_element_by_xpath('//a[contains(text(), \'CSV\')]').click()

    driver.command_executor._commands["send_command"] = (
        "POST", '/session/$sessionId/chromium/send_command')

    params = {'cmd': 'Page.setDownloadBehavior', 'params': {
        'behavior': 'allow', 'downloadPath': download_dir}}

    driver.execute("send_command", params)

    time.sleep(10)

    print("Finish Selenium Process, Quit Chrome!!")
    driver.quit()
