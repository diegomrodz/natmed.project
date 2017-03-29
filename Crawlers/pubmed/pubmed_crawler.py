from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from pymongo import MongoClient
import json

PUBMED_CRAWLER = './pubmed_crawler.js'

NATMED_CN = "mongodb://localhost:27017"
NATMED_DB = "natmed"
NATMED_COL = "references"

PUBMED_QTD = 58000

def get_crawler():
    with open(PUBMED_CRAWLER) as f:
        return "".join(f.readlines())

def get_references(col):
    return col.aggregate([
        { "$unwind": { "path": "$link" } },
        { "$project": { "_id": 1, "link": "$link" } },
        { "$skip": 2425 }
    ])

def consume_output(_id, output, col):
    obj = json.loads(output)
    obj['_id'] = _id
    col.update({'_id': _id}, obj, True)

if __name__ == '__main__':
    driver = webdriver.Chrome(executable_path="./../chromedriver")
    client = MongoClient(NATMED_CN)
    col = client[NATMED_DB][NATMED_COL]

    crawler = get_crawler()

    try:
        print("Starting the crawler\n")
        count = 2425

        for ref in get_references(col):
            count += 1
            print("Bacth #{} de {}".format(count, PUBMED_QTD))
            print("Acessing the url: {}".format(ref['link']))
            driver.get(ref['link'])
            print("Executing the crawler")
            output = driver.execute_script(crawler)
            print("Consuming the ouput")
            consume_output(ref['_id'], output, col)
            print("Crawler executed with success!\n")
    finally:
        print("Ending the crawler")
        driver.close()