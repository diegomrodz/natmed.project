from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import json

NATMED_TITLE = "Natural Medicines - Professional"

NATMED_LINKS = "./links.txt"
NATMED_CRAWLER = "./natmed_foods_crawler.js"
NATMED_CREDENTIALS = "./credentials.txt"

NATMED_CN = "mongodb://localhost:27017"
NATMED_DB = "natmed"
NATMED_COL = "foods"

def get_crawler():
    with open(NATMED_CRAWLER) as f:
        return "".join(f.readlines())

def is_logged(driver):
    return driver.title == NATMED_TITLE

def get_credentials():
    with open(NATMED_CREDENTIALS) as f:
        return [line.strip() for line in f.readlines()]

def login(driver):
    credentials = get_credentials()

    el = driver.find_element_by_id("username")
    el.send_keys(credentials[0])

    el = driver.find_element_by_id("password")
    el.send_keys(credentials[1])

    el = driver.find_element_by_id("submitLogin")
    el.click()

    assert is_logged(driver), "Couldn't login into the natmed website"

def get_id(url):
    return url.split("=")[1]

def consume_output(output, col):
    obj = json.loads(output)

    obj['_id'] = get_id(obj['url'])

    col.insert_one(obj)

if __name__ == '__main__':
    client = MongoClient(NATMED_CN)
    col = client[NATMED_DB][NATMED_COL]
    
    driver = webdriver.Chrome(executable_path="./chromedriver")

    crawler = get_crawler()

    try:
        with open(NATMED_LINKS, "r") as f:
            for url in [line.strip() for line in f.readlines() if line != ""]: 
                driver.get(url)

                if not is_logged(driver):
                    login(driver)
                
                output = driver.execute_script(crawler)
                consume_output(output, col)
    finally:
        driver.close()