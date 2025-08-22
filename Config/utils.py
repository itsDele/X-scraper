import json
import csv
import os
import pandas as pd
import time
import threading
from typing import List, Dict, Any, Callable, Optional
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By


class Constants:
    PATIENCE = 5  # Number of unchanged cycles before stopping scroll
    SCROLL_PAUSE = 3  # Pause time between scrolls (seconds)
    USER_CELL_SELECTOR = '[data-testid="UserCell"]'  # CSS selector for user cells
    TWEET_SELECTOR = '[data-testid="tweet"]'  # CSS selector for tweets in quotes


def load_input_file(
    input_file: str,
) -> tuple[List[str], List[str], Dict[str, str], Dict[str, str], str]:
    """
    Load the input JSON file.

    Args:
        input_file: Path to the JSON file.

    Returns:
        Tuple containing URLs, output formats, credentials, proxy settings, and output directory.
    """
    with open(input_file, "r", encoding="utf-8") as f:
        config = json.load(f)
    return (
        config.get("urls", []),
        config.get("output_formats", ["json", "csv", "excel", "txt"]),
        config.get("credentials", {}),
        config.get("proxy", {}),
        config.get("output_dir", "output"),
    )


def scroll_and_collect(
    driver: Chrome,
    element_selector: str,
    extract_func: Callable,
    patience: int,
    scroll_pause: int,
) -> List[Any]:
    """
    Scroll the page and collect elements.

    Args:
        driver:Chrome driver.
        element_selector:CSS selector for elements.
        extract_func:Function to extract data from each element.
        patience: Number of unchanged cycles before stopping.
        scroll_pause: Pause time between scrolls (seconds).

    Returns:
        List[Any]: List of extracted data.
    """
    collected = []
    seen = set()
    patience_count = 0
    viewport_height = driver.execute_script("return window.innerHeight")

    while True:
        elements = driver.find_elements(By.CSS_SELECTOR, element_selector)
        new_added = False
        for element in elements:
            try:
                result = extract_func(element)
                if result is None:
                    continue
                if result[0] not in seen:
                    seen.add(result[0])
                    collected.append(result)
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
    return collected


def save_to_files(
    data: List[Dict[str, str]],
    output_dir: str,
    filename_prefix: str,
    output_formats: List[str],
    lock: "threading.Lock",
) -> None:
    """
    Save data to files in multiple formats.

    Args:
        data: Data to save.
        output_dir: Output directory.
        filename_prefix: Filename prefix.
        output_formats: Output formats.
        lock: Lock for thread-safe operations.
    """
    with lock:
        os.makedirs(output_dir, exist_ok=True)
        if "json" in output_formats:
            with open(
                os.path.join(output_dir, f"{filename_prefix}.json"),
                "w",
                encoding="utf-8",
            ) as json_file:
                json.dump(data, json_file, ensure_ascii=False, indent=4)
        if "csv" in output_formats:
            with open(
                os.path.join(output_dir, f"{filename_prefix}.csv"),
                "w",
                newline="",
                encoding="utf-8",
            ) as csv_file:
                fieldnames = data[0].keys() if data else []
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
        if "excel" in output_formats:
            df = pd.DataFrame(data)
            df.to_excel(
                os.path.join(output_dir, f"{filename_prefix}.xlsx"), index=False
            )
        if "txt" in output_formats:
            with open(
                os.path.join(output_dir, f"{filename_prefix}.txt"),
                "w",
                encoding="utf-8",
            ) as txt_file:
                for i, item in enumerate(data, 1):
                    txt_file.write(
                        f"{i}. {item['username']} - {item['profile_link']}\n"
                    )
                    if "quote_text" in item:
                        txt_file.write(f"   Quote: {item['quote_text']}\n")
                        txt_file.write(f"   Quote URL: {item['quote_url']}\n\n")
