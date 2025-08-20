from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from dotenv import load_dotenv
import json
import csv
import pandas as pd

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

    # Save to files
    retweeters_dict = [
        {"username": username, "profile_link": link} for username, link in retweeters
    ]

    # JSON
    with open("retweets.json", "w", encoding="utf-8") as json_file:
        json.dump(retweeters_dict, json_file, ensure_ascii=False, indent=4)

    # CSV
    with open("retweets.csv", "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["username", "profile_link"])
        writer.writeheader()
        writer.writerows(retweeters_dict)

    # Excel Pandas
    df = pd.DataFrame(retweeters_dict)
    df.to_excel("retweets.xlsx", index=False)

    # TXT
    with open("retweets.txt", "w", encoding="utf-8") as txt_file:
        for i, (username, link) in enumerate(retweeters, 1):
            txt_file.write(f"{i}. {username} - {link}\n")

    return driver, retweeters


def qoutes(driver, url):
    qoutes_url = f"{url}/quotes"
    driver.get(qoutes_url)
    time.sleep(5)

    quoters = []
    seen = set()
    patience_count = 0
    patience = 5
    scroll_pause = 3
    viewport_height = driver.execute_script("return window.innerHeight")

    while True:
        current_cells = driver.find_elements(By.CSS_SELECTOR, '[data-testid="tweet"]')
        new_added = False
        for cell in current_cells:
            try:
                # Get username and profile link
                link_elem = cell.find_element(By.CSS_SELECTOR, 'a[href*="/"]')
                profile_link = link_elem.get_attribute("href")
                username = "@" + profile_link.split("/")[-1]

                # Get quote tweet URL
                quote_link = cell.find_element(By.CSS_SELECTOR, 'a[href*="/status/"]')
                quote_url = quote_link.get_attribute("href")

                # Get quote tweet text
                quote_text_elem = cell.find_element(
                    By.CSS_SELECTOR, '[data-testid="tweetText"]'
                )
                quote_text = quote_text_elem.text.strip()

                if username not in seen:
                    seen.add(username)
                    quoters.append((username, profile_link, quote_text, quote_url))
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

    # Save to files
    quoters_dict = [
        {
            "username": username,
            "profile_link": profile_link,
            "quote_text": quote_text,
            "quote_url": quote_url,
        }
        for username, profile_link, quote_text, quote_url in quoters
    ]

    # JSON
    with open("quoters.json", "w", encoding="utf-8") as json_file:
        json.dump(quoters_dict, json_file, ensure_ascii=False, indent=4)

    # CSV
    with open("quoters.csv", "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(
            csv_file, fieldnames=["username", "profile_link", "quote_text", "quote_url"]
        )
        writer.writeheader()
        writer.writerows(quoters_dict)

    # Excel Pandas
    df = pd.DataFrame(quoters_dict)
    df.to_excel("quoters.xlsx", index=False)

    # TXT
    with open("quoters.txt", "w", encoding="utf-8") as txt_file:
        for i, (username, profile_link, quote_text, quote_url) in enumerate(quoters, 1):
            txt_file.write(f"{i}. {username} - {profile_link}\n")
            txt_file.write(f"   Quote: {quote_text}\n")
            txt_file.write(f"   Quote URL: {quote_url}\n\n")

    return driver, quoters


url = "https://x.com/clcoding/status/1957509803057574278"

driver = webdriver.Chrome()
driver = loginX(driver)
driver, retweeters_data = retweets(driver, url)
driver, quoters_data = qoutes(driver, url)
driver.quit()
