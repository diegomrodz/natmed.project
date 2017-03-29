from selenium import webdriver
from selenium.webdriver.common.keys import Keys

NATMED_START_URL = "https://naturalmedicines.therapeuticresearch.com/databases/food,-herbs-supplements.aspx?letter=0"
NATMED_TITLE = "Natural Medicines - Food, Herbs & Supplements"

NATMED_CREDENTIALS = "./credentials.txt"
NATMED_LINKS = "./links.txt"

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

if __name__ == '__main__':
    driver = webdriver.Chrome(executable_path="./../chromedriver")

    try:
        driver.get(NATMED_START_URL)

        if not is_logged(driver):
            login(driver)
        
        links = []

        for a in driver.find_elements_by_css_selector("#A-Z a:not(.active)") :
            links.append(a.get_attribute('href'))
        
        with open(NATMED_LINKS, "w") as f:
            for link in links:
                driver.get(link)

                for a in driver.find_elements_by_css_selector("ul.LG a"):
                    f.write(a.get_attribute("href") + "\n")

    finally:
        driver.close()