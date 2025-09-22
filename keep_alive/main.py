import requests
import time
import logging
from datetime import datetime
import schedule
import threading
import sys
import os

# ✅ Colorama for colored console output
from colorama import Fore, Style, init
init(autoreset=True)

# Configure logging with proper encoding for Windows
def setup_logging():
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    file_handler = logging.FileHandler('keepalive.log', encoding='utf-8')
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    if os.name == 'nt':
        try:
            os.system('chcp 65001 >nul 2>&1')
        except:
            pass

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

setup_logging()

class StreamlitKeepAlive:
    def __init__(self, urls, interval_minutes=5):
        if isinstance(urls, str):
            self.urls = [urls.rstrip('/')]
        else:
            self.urls = [url.rstrip('/') for url in urls]

        self.interval_minutes = interval_minutes
        self.session = requests.Session()

        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })

        self.url_stats = {url: {'success_count': 0, 'failure_count': 0} for url in self.urls}

    def ping_single_app(self, url):
        try:
            logging.info(Fore.CYAN + f"Pinging {url}")

            response = self.session.get(url, timeout=30, allow_redirects=True)

            if response.status_code == 200:
                self.url_stats[url]['success_count'] += 1
                logging.info(Fore.GREEN + f"[SUCCESS] {url} - Status: {response.status_code}, "
                                          f"Response time: {response.elapsed.total_seconds():.2f}s")
            else:
                self.url_stats[url]['failure_count'] += 1
                logging.warning(Fore.YELLOW + f"[WARNING] {url} - Unexpected status code: {response.status_code}")

        except requests.exceptions.Timeout:
            self.url_stats[url]['failure_count'] += 1
            logging.error(Fore.RED + f"[ERROR] {url} - Request timeout")

        except requests.exceptions.ConnectionError:
            self.url_stats[url]['failure_count'] += 1
            logging.error(Fore.RED + f"[ERROR] {url} - Connection error")

        except requests.exceptions.RequestException as e:
            self.url_stats[url]['failure_count'] += 1
            logging.error(Fore.RED + f"[ERROR] {url} - Request failed: {str(e)}")

        except Exception as e:
            self.url_stats[url]['failure_count'] += 1
            logging.error(Fore.RED + f"[ERROR] {url} - Unexpected error: {str(e)}")

    def ping_all_apps(self):
        logging.info(Style.BRIGHT + Fore.CYAN + f"[CYCLE START] Pinging {len(self.urls)} URLs")
        for i, url in enumerate(self.urls, 1):
            logging.info(Fore.BLUE + f"[{i}/{len(self.urls)}] {url}")
            self.ping_single_app(url)
            if i < len(self.urls):
                time.sleep(2)
        logging.info(Style.BRIGHT + Fore.CYAN + "[CYCLE END] Completed ping cycle")
        self.print_cycle_summary()

    def run_continuous(self):
        logging.info(Style.BRIGHT + Fore.MAGENTA + f"[START] Monitoring {len(self.urls)} URLs")
        logging.info(Fore.MAGENTA + f"[CONFIG] Interval: {self.interval_minutes} minutes")

        try:
            while True:
                self.ping_all_apps()
                logging.info(Fore.YELLOW + f"[WAIT] Waiting {self.interval_minutes} minutes...")
                time.sleep(self.interval_minutes * 60)

        except KeyboardInterrupt:
            logging.info(Style.BRIGHT + Fore.RED + "[STOP] Service stopped by user")
            self.print_final_stats()

        except Exception as e:
            logging.error(Style.BRIGHT + Fore.RED + f"[CRASH] Service crashed: {str(e)}")
            self.print_final_stats()

    def run_scheduled(self):
        logging.info(Style.BRIGHT + Fore.MAGENTA + f"[START] Scheduled monitoring {len(self.urls)} URLs")
        logging.info(Fore.MAGENTA + f"[CONFIG] Interval: {self.interval_minutes} minutes")

        schedule.every(self.interval_minutes).minutes.do(self.ping_all_apps)
        self.ping_all_apps()

        try:
            while True:
                schedule.run_pending()
                time.sleep(30)
        except KeyboardInterrupt:
            logging.info(Style.BRIGHT + Fore.RED + "[STOP] Service stopped by user")
            self.print_final_stats()

    def print_cycle_summary(self):
        total_success = sum(stats['success_count'] for stats in self.url_stats.values())
        total_failure = sum(stats['failure_count'] for stats in self.url_stats.values())
        logging.info(Style.BRIGHT + Fore.CYAN +
                     f"[CYCLE SUMMARY] Success: {total_success}, Failed: {total_failure}")

    def print_final_stats(self):
        logging.info(Style.BRIGHT + Fore.MAGENTA + "[STATS] === SERVICE STATISTICS ===")
        overall_success = overall_failure = 0

        for url, stats in self.url_stats.items():
            total_pings = stats['success_count'] + stats['failure_count']
            success_rate = (stats['success_count'] / total_pings * 100) if total_pings > 0 else 0

            logging.info(Style.BRIGHT + Fore.CYAN + f"\n--- {url} ---")
            logging.info(f"  Success: {stats['success_count']}")
            logging.info(f"  Failed: {stats['failure_count']}")
            logging.info(f"  Success rate: {success_rate:.1f}%")

            overall_success += stats['success_count']
            overall_failure += stats['failure_count']

        overall_total = overall_success + overall_failure
        overall_rate = (overall_success / overall_total * 100) if overall_total > 0 else 0

        logging.info(Style.BRIGHT + Fore.CYAN + f"\n--- OVERALL ---")
        logging.info(f"Total: {overall_total}, Success: {overall_success}, "
                     f"Failed: {overall_failure}, Rate: {overall_rate:.1f}%")

def main():
    STREAMLIT_URLS = [
        "https://mushroom-classification-sk.streamlit.app",
        "https://kmeans-comp.streamlit.app",
        "https://pomodoroui.streamlit.app",
        "https://huggingface.co/spaces/jobannagra/simple-bg-remove"
    ]
    PING_INTERVAL = 5

    keepalive = StreamlitKeepAlive(STREAMLIT_URLS, PING_INTERVAL)

    print(Fore.YELLOW + "\n" + "="*60)
    print(Style.BRIGHT + Fore.GREEN + "MULTI-URL KEEP-ALIVE SERVICE")
    print(Fore.YELLOW + "="*60)

    print(Fore.CYAN + f"Target URLs ({len(STREAMLIT_URLS)}):")
    for i, url in enumerate(STREAMLIT_URLS, 1):
        print(Fore.CYAN + f"  {i}. {url}")

    print(Fore.MAGENTA + f"Ping interval: {PING_INTERVAL} minutes")
    print(Fore.YELLOW + "Press Ctrl+C to stop the service")
    print(Fore.YELLOW + "="*60 + "\n")

    keepalive.run_continuous()

if __name__ == "__main__":
    main()
