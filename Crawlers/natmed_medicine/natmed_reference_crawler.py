from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from neo4j.v1 import GraphDatabase, basic_auth
from pymongo import MongoClient
import json

NATMED_URL = "https://naturalmedicines.therapeuticresearch.com/references.aspx?productid={}"
NATMED_TITLE = "Natural Medicines - References"

NATMED_CREDENTIALS = "./credentials.txt"
NATMED_LINKS = "./links.txt"

NATMED_CRAWLER = './natmed_reference_crawler.js'

NATMED_CN = "mongodb://localhost:27017"
NATMED_DB = "natmed"
NATMED_COL = "references"

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

def get_ids(session):
    query = session.run("MATCH (m:Medicine) RETURN m.id")
    return [e.values()[0] for e in query]

def consume_output(output, col):
    arr = json.loads(output)
    
    for obj in arr:
        col.update({'_id': obj['_id']}, obj, True)

if __name__ == '__main__':
    gdriver = GraphDatabase.driver("bolt://localhost:7687", auth=basic_auth("neo4j", "naturalmed"))
    driver = webdriver.Chrome(executable_path="./../chromedriver")
    client = MongoClient(NATMED_CN)
    col = client[NATMED_DB][NATMED_COL]

    session = gdriver.session()

    crawler = get_crawler()

    try:
        ids = get_ids(session)

        for id in ids:
            driver.get(NATMED_URL.format(id))

            if not is_logged(driver):
                login(driver)
            
            output = driver.execute_script(crawler)

            consume_output(output, col)

    finally:
        driver.close()
        session.close()