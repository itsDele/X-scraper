from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import os
import json
import csv
import pandas as pd
import argparse
from concurrent.futures import ThreadPoolExecutor
import threading
import asyncio


def parse_arguments():
    # command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input-file",
        required=True,
        help="Path to the input JSON file containing URLs, output formats, credentials, proxy settings, and output directory.",
    )
    parser.add_argument(
        "--max-concurrent",
        type=int,
        default=2,
        help="Maximum number of concurrent browser.",
    )
    return parser.parse_args()


def load_input_file(input_file):

    with open(input_file, "r", encoding="utf-8") as f:
        config = json.load(f)

    urls = config.get("urls", [])
    output_formats = config.get("output_formats", ["json", "csv", "excel", "txt"])
    credentials = config.get("credentials", {})
    proxy = config.get("proxy", {})
    output_dir = config.get("output_dir", "output")

    return urls, output_formats, credentials, proxy, output_dir


def setup_driver(proxy=None):
    # setup proxy if needed
    chrome_options = Options()
    if proxy:
        proxy_str = f"{proxy['host']}:{proxy['port']}"
        if proxy.get("username") and proxy.get("password"):
            proxy_str = f"{proxy['username']}:{proxy['password']}@{proxy_str}"
        chrome_options.add_argument(f"--proxy-server={proxy_str}")
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def loginX(driver, credentials):

    username = credentials["TWITTER_USERNAME"]
    password = credentials["TWITTER_PASSWORD"]
    email = credentials["TWITTER_EMAIL"]

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


def retweets(driver, url, output_dir, output_formats, lock):
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

    with lock:
        os.makedirs(output_dir, exist_ok=True)
        url_id = url.split("/")[-1]
        retweeters_dict = [
            {"username": username, "profile_link": link}
            for username, link in retweeters
        ]

        if "json" in output_formats:
            with open(
                os.path.join(output_dir, f"retweets_{url_id}.json"),
                "w",
                encoding="utf-8",
            ) as json_file:
                json.dump(retweeters_dict, json_file, ensure_ascii=False, indent=4)
        if "csv" in output_formats:
            with open(
                os.path.join(output_dir, f"retweets_{url_id}.csv"),
                "w",
                newline="",
                encoding="utf-8",
            ) as csv_file:
                writer = csv.DictWriter(
                    csv_file, fieldnames=["username", "profile_link"]
                )
                writer.writeheader()
                writer.writerows(retweeters_dict)
        if "excel" in output_formats:
            df = pd.DataFrame(retweeters_dict)
            df.to_excel(
                os.path.join(output_dir, f"retweets_{url_id}.xlsx"), index=False
            )
        if "txt" in output_formats:
            with open(
                os.path.join(output_dir, f"retweets_{url_id}.txt"),
                "w",
                encoding="utf-8",
            ) as txt_file:
                for i, (username, link) in enumerate(retweeters, 1):
                    txt_file.write(f"{i}. {username} - {link}\n")

    return driver, retweeters


def qoutes(driver, url, output_dir, output_formats, lock):
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
    with lock:
        os.makedirs(output_dir, exist_ok=True)
        url_id = url.split("/")[-1]
        quoters_dict = [
            {
                "username": username,
                "profile_link": profile_link,
                "quote_text": quote_text,
                "quote_url": quote_url,
            }
            for username, profile_link, quote_text, quote_url in quoters
        ]

        if "json" in output_formats:
            with open(
                os.path.join(output_dir, f"quoters_{url_id}.json"),
                "w",
                encoding="utf-8",
            ) as json_file:
                json.dump(quoters_dict, json_file, ensure_ascii=False, indent=4)
        if "csv" in output_formats:
            with open(
                os.path.join(output_dir, f"quoters_{url_id}.csv"),
                "w",
                newline="",
                encoding="utf-8",
            ) as csv_file:
                writer = csv.DictWriter(
                    csv_file,
                    fieldnames=["username", "profile_link", "quote_text", "quote_url"],
                )
                writer.writeheader()
                writer.writerows(quoters_dict)
        if "excel" in output_formats:
            df = pd.DataFrame(quoters_dict)
            df.to_excel(os.path.join(output_dir, f"quoters_{url_id}.xlsx"), index=False)
        if "txt" in output_formats:
            with open(
                os.path.join(output_dir, f"quoters_{url_id}.txt"), "w", encoding="utf-8"
            ) as txt_file:
                for i, (username, profile_link, quote_text, quote_url) in enumerate(
                    quoters, 1
                ):
                    txt_file.write(f"{i}. {username} - {profile_link}\n")
                    txt_file.write(f"   Quote: {quote_text}\n")
                    txt_file.write(f"   Quote URL: {quote_url}\n\n")

    return driver, quoters


def process_url(url, credentials, proxy, output_dir, output_formats, lock):
    driver = setup_driver(proxy)
    try:
        driver = loginX(driver, credentials)
        driver, retweeters = retweets(driver, url, output_dir, output_formats, lock)
        driver, quoters = qoutes(driver, url, output_dir, output_formats, lock)
        return url, retweeters, quoters
    finally:
        driver.quit()


async def main():
    args = parse_arguments()
    urls, output_formats, credentials, proxy, output_dir = load_input_file(
        args.input_file
    )
    lock = threading.Lock()
    max_concurrent = args.max_concurrent

    with ThreadPoolExecutor(max_workers=max_concurrent) as executor:
        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(
                executor,
                process_url,
                url,
                credentials,
                proxy,
                output_dir,
                output_formats,
                lock,
            )
            for url in urls
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, Exception):
                print(f"Error processing URL: {result}")
            else:
                url, retweeters, quoters = result
                print(
                    f"Processed {url}: {len(retweeters)} retweeters, {len(quoters)} quoters"
                )


if __name__ == "__main__":
    asyncio.run(main())
