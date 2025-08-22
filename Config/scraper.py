from selenium.webdriver.common.by import By
from selenium.webdriver import Chrome
from selenium.common.exceptions import NoSuchElementException
from typing import List, Dict, Tuple
from utils import scroll_and_collect, save_to_files, Constants
import threading


def scrape_retweets(
    driver: Chrome,
    url: str,
    output_dir: str,
    output_formats: List[str],
    lock: "threading.Lock",
) -> List[Dict[str, str]]:
    """
    Scrape retweeters from an X post.

    Args:
        driver:Chrome driver.
        url: URL of the X post.
        output_dir: Output directory for saving files.
        output_formats: Output formats (json, csv, excel, txt).
        lock: Lock for thread-safe operations.

    Returns:
        List[Dict[str, str]]: List of retweeters with username and profile link.
    """
    driver.get(f"{url}/retweets")
    retweeters = scroll_and_collect(
        driver=driver,
        element_selector='[data-testid="UserCell"]',
        extract_func=lambda cell: _extract_retweeter(cell),
        patience=Constants.PATIENCE,
        scroll_pause=Constants.SCROLL_PAUSE,
    )
    post_id = url.split("/")[-1]
    save_to_files(
        data=[
            {"username": username, "profile_link": link}
            for username, link in retweeters
        ],
        output_dir=output_dir,
        filename_prefix=f"retweets_{post_id}",
        output_formats=output_formats,
        lock=lock,
    )
    return [
        {"username": username, "profile_link": link} for username, link in retweeters
    ]


def scrape_quotes(
    driver: Chrome,
    url: str,
    output_dir: str,
    output_formats: List[str],
    lock: "threading.Lock",
) -> List[Dict[str, str]]:
    """
    Scrape quoters from an X post.

    Args:
        driver: Chrome driver .
        url: URL of the X post.
        output_dir: Output directory for saving files.
        output_formats: Output formats (json, csv, excel, txt).
        lock: Lock for thread-safe operations.

    Returns:
        List[Dict[str, str]]: List of quoters with username, profile link, quote text, and quote URL.
    """
    driver.get(f"{url}/quotes")
    quoters = scroll_and_collect(
        driver=driver,
        element_selector='[data-testid="tweet"]',
        extract_func=lambda cell: _extract_quoter(cell),
        patience=Constants.PATIENCE,
        scroll_pause=Constants.SCROLL_PAUSE,
    )
    post_id = url.split("/")[-1]
    save_to_files(
        data=[
            {
                "username": username,
                "profile_link": link,
                "quote_text": text,
                "quote_url": quote_url,
            }
            for username, link, text, quote_url in quoters
        ],
        output_dir=output_dir,
        filename_prefix=f"quotes_{post_id}",
        output_formats=output_formats,
        lock=lock,
    )
    return [
        {
            "username": username,
            "profile_link": link,
            "quote_text": text,
            "quote_url": quote_url,
        }
        for username, link, text, quote_url in quoters
    ]


def _extract_retweeter(cell) -> Tuple[str, str]:
    """
    Extract retweeter information from a cell.

    Args:
        cell: User cell element.

    Returns:
        Tuple[str, str]:  Username and profile link.
    """
    try:
        link_elem = cell.find_element(By.CSS_SELECTOR, 'a[href*="/"]')
        profile_link = link_elem.get_attribute("href")
        username = "@" + profile_link.split("/")[-1]
        return username, profile_link
    except:
        return None, None


def _extract_quoter(cell) -> Tuple[str, str, str, str]:
    """
    Extract quoter information from a cell.

    Args:
        cell: Tweet cell element.

    Returns:
        Tuple[str, str, str, str]: Username, profile link, quote text, and quote URL.
    """
    try:
        link_elem = cell.find_element(By.CSS_SELECTOR, 'a[href*="/"]')
        profile_link = link_elem.get_attribute("href")
        username = "@" + profile_link.split("/")[-1]
        quote_link = cell.find_element(By.CSS_SELECTOR, 'a[href*="/status/"]')
        quote_url = quote_link.get_attribute("href")
        quote_text_elem = cell.find_element(
            By.CSS_SELECTOR, '[data-testid="tweetText"]'
        )
        quote_text = quote_text_elem.text.strip()
        return username, profile_link, quote_text, quote_url
    except:
        return None, None, None, None
