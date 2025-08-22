from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

import time
from typing import Dict, Optional


def setup_driver(proxy: Optional[Dict[str, str]] = None) -> webdriver.Chrome:
    """
    Set up Chrome driver with optional proxy.

    Args:
        proxy:  Proxy settings with host, port, username, and password.

    Returns:
        webdriver.Chrome: your configured chrome driver.
    """
    chrome_options = Options()
    # Suppress unnecessary logs and disable GPU to avoid errors
    chrome_options.add_argument("--enable-unsafe-swiftshader")  #  to suppress warnings
    chrome_options.add_argument("--log-level=3")  # Only show errors
    chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration
    chrome_options.add_argument("--no-sandbox")  # Improve compatibility
    chrome_options.add_argument("--disable-dev-shm-usage")  # Avoid shared memory issues
    chrome_options.add_argument(
        "--disable-webgl"
    )  # Disable WebGL to avoid related errors
    # chrome_options.add_argument("--headless")        you can run in headless mode to reduce the gpu use and its better for servers
    if proxy:
        proxy_str = f"{proxy['host']}:{proxy['port']}"
        if proxy.get("username") and proxy.get("password"):
            proxy_str = f"{proxy['username']}:{proxy['password']}@{proxy_str}"
        chrome_options.add_argument(f"--proxy-server={proxy_str}")
    return webdriver.Chrome(options=chrome_options)


def loginX(driver: webdriver.Chrome, credentials: Dict[str, str]) -> webdriver.Chrome:
    """
    Log in to X using your credentials.

    Args:
        driver: your Chrome driver .
        credentials:  your x username, password, and email.

    Returns:
        webdriver.Chrome: Driver after successful login.
    """
    driver.get("https://x.com/i/flow/login")
    time.sleep(3)

    # wait for the username field elemnt to appear and then send your x username into the field
    username_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "text"))
    )
    username_field.send_keys(credentials["TWITTER_USERNAME"])
    driver.find_element(By.XPATH, "//span[contains(text(), 'Next')]").click()
    time.sleep(3)

    # sometimes x requires second verfication so we need to pass that by using your x email the page contains this text:
    # Check for unusual login activity if the page appears we'll send your x email to the required field for verfication
    if "unusual login activity" in driver.page_source:
        driver.find_element(By.NAME, "text").send_keys(credentials["TWITTER_EMAIL"])
        driver.find_element(By.XPATH, "//span[contains(text(), 'Next')]").click()
        time.sleep(3)

    # now find the password element and then send your x password to the field and log in
    driver.find_element(By.NAME, "password").send_keys(credentials["TWITTER_PASSWORD"])
    driver.find_element(By.XPATH, "//span[contains(text(), 'Log in')]").click()
    time.sleep(5)

    return driver


# returns the logged in driver
