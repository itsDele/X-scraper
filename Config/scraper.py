from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from dotenv import load_dotenv

load_dotenv()

username = os.getenv("TWITTER_USERNAME")
password = os.getenv("TWITTER_PASSWORD")
email = os.getenv("TWITTER_EMAIL")


def loginX(driver):
    # login page
    driver.get("https://x.com/i/flow/login")
    time.sleep(3)

    # Enter username
    username_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "text"))
    )
    username_field.send_keys(username)

    driver.find_element(By.XPATH, "//span[contains(text(), 'Next')]").click()
    time.sleep(3)

    # if verification is needed
    if "unusual login activity" in driver.page_source:
        driver.find_element(By.NAME, "text").send_keys(email)
        driver.find_element(By.XPATH, "//span[contains(text(), 'Next')]").click()
        time.sleep(3)

    # password and login
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.XPATH, "//span[contains(text(), 'Log in')]").click()
    time.sleep(5)

    return driver


def scroll_to_load_all(driver, element_selector, patience=3, scroll_pause=2):

    last_count = 0
    no_change_count = 0

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause)

        elements = driver.find_elements(By.CSS_SELECTOR, element_selector)

        new_count = len(elements)
        if new_count == last_count:
            no_change_count += 1
            if no_change_count >= patience:
                break
        else:
            no_change_count = 0

        last_count = new_count


def retweets(driver, url):
    retweet_url = f"{url}/retweets"
    driver.get(retweet_url)
    time.sleep(5)

    retweeters = []
    seen = set()
    patience_count = 0
    patience = 5
    scroll_pause = 3
    viewport_height = driver.execute_script("return window.innerHeight")

    while True:
        current_cells = driver.find_elements(
            By.CSS_SELECTOR, '[data-testid="UserCell"]'
        )
        new_added = False
        for cell in current_cells:
            try:
                link_elem = cell.find_element(By.CSS_SELECTOR, 'a[href*="/"]')
                profile_link = link_elem.get_attribute("href")
                username = "@" + profile_link.split("/")[-1]
                if username not in seen:
                    seen.add(username)
                    retweeters.append((username, profile_link))
                    new_added = True
            except:
                continue

        if not new_added:
            patience_count += 1
            if patience_count >= patience:
                break
        else:
            patience_count = 0

        driver.execute_script(f"window.scrollBy(0, {viewport_height});")
        time.sleep(scroll_pause)

    print(f"Found {len(retweeters)} retweeters:")
    for i, (username, link) in enumerate(retweeters, 1):
        print(f"{i}. {username} - {link}")

    driver.quit()


url = "https://x.com/clcoding/status/1957509803057574278"

driver = webdriver.Chrome()
driver = loginX(driver)
retweets(driver, url)
