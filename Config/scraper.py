from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import os

username = os.getenv("TWITTER_USERNAME")
password = os.getenv("TWITTER_PASSWORD")


def loginX(driver, username, password):
    driver = webdriver.Chrome()
    driver.get("https://x.com/i/flow/login")

    time.sleep(3)
    username_field = driver.find_element('input[name="text"]')
    username_field.send_keys(username)
    next = driver.find_element(By.XPATH, "//span[contains(text(), 'Next')]")
    next.click()

    time.sleep(3)
    password_field = driver.find_element('input[name="password"]')
    password_field.send_keys(password)
    login_button = driver.find_element("//span[contains(text(),'Log in')]")
    login_button.click()
    time.sleep(1)


# url = "https://x.com/clcoding/status/1957509803057574278"
# retweet_urls = f"{url}/retweets"
# driver.get(retweet_urls)
# time.sleep(5)


# users = driver.find_elements(
#   By.CSS_SELECTOR, value=".css-175oi2r r-1awozwy r-18u37iz r-dnmrzs"
# )
# driver.quit()
# print(users)
