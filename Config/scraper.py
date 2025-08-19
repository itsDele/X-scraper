from selenium import webdriver
from selenium.webdriver.common.by import By
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
    driver.find_element(By.NAME, "text").send_keys(username)
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


def retweets(driver, url):
    retweet_urls = f"{url}/retweets"
    driver.get(retweet_urls)
    time.sleep(5)

    users = driver.find_elements(By.CSS_SELECTOR, '[data-testid="UserCell"]')

    print(f"Found {len(users)} retweeters:")
    for i, user in enumerate(users, 1):
        try:
            profile_link = user.find_element(
                By.CSS_SELECTOR, 'a[href*="/"]'
            ).get_attribute("href")
            username = "@" + profile_link.split("/")[-1]
            print(f"{i}. {username} - {profile_link}")
        except:
            continue

    driver.quit()


url = "https://x.com/clcoding/status/1957509803057574278"

driver = webdriver.Chrome()
driver = loginX(driver)
retweets(driver, url)
