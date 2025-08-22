import asyncio
import argparse
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any, Tuple
from browser import setup_driver, loginX
from scraper import scrape_retweets, scrape_quotes
from utils import load_input_file
import logging

# defult workers are set to 2 you can adjust(read how to use.md)
MAX_CONCURRENT_DEFAULT = 2


# cli commands
def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input-file",
        required=True,
        help="Path to the input JSON file containing URLs, output formats, credentials, proxy settings, and output directory.",
    )
    parser.add_argument(
        "--max-concurrent",
        type=int,
        default=MAX_CONCURRENT_DEFAULT,
        help="number of driver browsers.",
    )
    return parser.parse_args()


def process_url(
    url: str,
    credentials: Dict[str, str],
    proxy: Dict[str, str],
    output_dir: str,
    output_formats: List[str],
    lock: threading.Lock,
) -> Tuple[str, List[Dict[str, str]], List[Dict[str, str]]]:
    """
     Process a URL to collect retweeters and quoters.

    Args:
        url:  URL of the X post.
        credentials: your x username, password, and email.
        proxy:  Proxy settings with host, port, username, and password.
        output_dir: Output directory for saving files.
        output_formats: Output formats (json, csv, excel, txt).
        lock:  Lock for thread-safe operations.

    Returns:
        Tuple containing the URL, list of retweeters, and list of quoters.
    """
    driver = setup_driver(proxy)
    try:
        driver = loginX(driver, credentials)
        retweeters = scrape_retweets(driver, url, output_dir, output_formats, lock)
        quoters = scrape_quotes(driver, url, output_dir, output_formats, lock)
        return url, retweeters, quoters
    except Exception as e:
        logging.error(f"Error processing URL {url}: {str(e)}")
        raise
    finally:
        driver.quit()


async def main() -> None:
    """
    Main function to run the program.

    Orchestrates the scraping process by loading input, setting up concurrent tasks,
    and processing results.
    """
    args = parse_arguments()
    urls, output_formats, credentials, proxy, output_dir = load_input_file(
        args.input_file
    )
    lock = threading.Lock()

    with ThreadPoolExecutor(max_workers=args.max_concurrent) as executor:
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
                logging.error(f"Error processing URL: {result}")
            else:
                url, retweeters, quoters = result
                logging.info(
                    f"Processed {url}: {len(retweeters)} retweeters, {len(quoters)} quoters"
                )


if __name__ == "__main__":
    asyncio.run(main())
