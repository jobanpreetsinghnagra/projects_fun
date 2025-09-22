import requests
import time
import logging
from datetime import datetime
import schedule
import threading
import sys
import os

# Configure logging with proper encoding for Windows
def setup_logging():
    # Create formatters
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # File handler with UTF-8 encoding
    file_handler = logging.FileHandler('keepalive.log', encoding='utf-8')
    file_handler.setFormatter(formatter)
    
    # Console handler with proper encoding
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Set console encoding to UTF-8 on Windows
    if os.name == 'nt':  # Windows
        try:
            # Try to set console to UTF-8
            os.system('chcp 65001 >nul 2>&1')
        except:
            pass
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

setup_logging()

class StreamlitKeepAlive:
    def __init__(self, urls, interval_minutes=5):
        """
        Initialize the keep-alive service
        
        Args:
            urls (list): List of Streamlit app URLs
            interval_minutes (int): Minutes between request cycles (default: 5)
        """
        # Handle both single URL and list of URLs for backward compatibility
        if isinstance(urls, str):
            self.urls = [urls.rstrip('/')]
        else:
            self.urls = [url.rstrip('/') for url in urls]  # Remove trailing slash if present
            
        self.interval_minutes = interval_minutes
        self.session = requests.Session()
        
        # Configure session with headers to appear like a real browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # Statistics per URL
        self.url_stats = {}
        for url in self.urls:
            self.url_stats[url] = {
                'success_count': 0,
                'failure_count': 0
            }
        
    def ping_single_app(self, url):
        """Send a GET request to a single Streamlit app"""
        try:
            logging.info(f"Pinging {url}")
            
            # Make request with timeout
            response = self.session.get(
                url, 
                timeout=30,
                allow_redirects=True
            )
            
            if response.status_code == 200:
                self.url_stats[url]['success_count'] += 1
                logging.info(f"[SUCCESS] {url} - Status: {response.status_code}, "
                           f"Response time: {response.elapsed.total_seconds():.2f}s")
            else:
                self.url_stats[url]['failure_count'] += 1
                logging.warning(f"[WARNING] {url} - Unexpected status code: {response.status_code}")
                
        except requests.exceptions.Timeout:
            self.url_stats[url]['failure_count'] += 1
            logging.error(f"[ERROR] {url} - Request timeout - App might be sleeping or slow to respond")
            
        except requests.exceptions.ConnectionError:
            self.url_stats[url]['failure_count'] += 1
            logging.error(f"[ERROR] {url} - Connection error - Check your internet connection and URL")
            
        except requests.exceptions.RequestException as e:
            self.url_stats[url]['failure_count'] += 1
            logging.error(f"[ERROR] {url} - Request failed: {str(e)}")
            
        except Exception as e:
            self.url_stats[url]['failure_count'] += 1
            logging.error(f"[ERROR] {url} - Unexpected error: {str(e)}")
    
    def ping_all_apps(self):
        """Send requests to all URLs in the list, one by one"""
        logging.info(f"[CYCLE START] Starting ping cycle for {len(self.urls)} URLs")
        
        for i, url in enumerate(self.urls, 1):
            logging.info(f"[{i}/{len(self.urls)}] Processing URL: {url}")
            self.ping_single_app(url)
            
            # Add small delay between requests to avoid overwhelming servers
            if i < len(self.urls):  # Don't wait after the last URL
                time.sleep(2)  # 2 second delay between URLs
        
        logging.info("[CYCLE END] Completed ping cycle for all URLs")
        self.print_cycle_summary()
    
    def run_continuous(self):
        """Run the keep-alive service continuously using simple time.sleep()"""
        logging.info(f"[START] Starting keep-alive service for {len(self.urls)} URLs")
        logging.info(f"[CONFIG] Pinging all URLs every {self.interval_minutes} minutes")
        
        try:
            while True:
                self.ping_all_apps()
                logging.info(f"[WAIT] Waiting {self.interval_minutes} minutes until next cycle...")
                time.sleep(self.interval_minutes * 60)  # Convert minutes to seconds
                
        except KeyboardInterrupt:
            logging.info("[STOP] Service stopped by user (Ctrl+C)")
            self.print_final_stats()
            
        except Exception as e:
            logging.error(f"[CRASH] Service crashed: {str(e)}")
            self.print_final_stats()
    
    def run_scheduled(self):
        """Run the keep-alive service using the schedule library"""
        logging.info(f"[START] Starting scheduled keep-alive service for {len(self.urls)} URLs")
        logging.info(f"[CONFIG] Pinging all URLs every {self.interval_minutes} minutes")
        
        # Schedule the job
        schedule.every(self.interval_minutes).minutes.do(self.ping_all_apps)
        
        # Run initial ping cycle
        self.ping_all_apps()
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(30)  # Check every 30 seconds
                
        except KeyboardInterrupt:
            logging.info("[STOP] Service stopped by user (Ctrl+C)")
            self.print_final_stats()
    
    def print_cycle_summary(self):
        """Print summary of the current cycle"""
        total_success = sum(stats['success_count'] for stats in self.url_stats.values())
        total_failure = sum(stats['failure_count'] for stats in self.url_stats.values())
        
        logging.info(f"[CYCLE SUMMARY] URLs processed: {len(self.urls)}, "
                    f"Current cycle - Success: {total_success}, Failed: {total_failure}")
    
    def print_final_stats(self):
        """Print detailed service statistics for all URLs"""
        logging.info("[STATS] === SERVICE STATISTICS ===")
        logging.info(f"Total URLs monitored: {len(self.urls)}")
        logging.info(f"Ping interval: {self.interval_minutes} minutes")
        
        overall_success = 0
        overall_failure = 0
        
        for url, stats in self.url_stats.items():
            total_pings = stats['success_count'] + stats['failure_count']
            success_rate = (stats['success_count'] / total_pings * 100) if total_pings > 0 else 0
            
            logging.info(f"\n--- {url} ---")
            logging.info(f"  Total pings: {total_pings}")
            logging.info(f"  Successful: {stats['success_count']}")
            logging.info(f"  Failed: {stats['failure_count']}")
            logging.info(f"  Success rate: {success_rate:.1f}%")
            
            overall_success += stats['success_count']
            overall_failure += stats['failure_count']
        
        # Overall statistics
        overall_total = overall_success + overall_failure
        overall_rate = (overall_success / overall_total * 100) if overall_total > 0 else 0
        
        logging.info(f"\n--- OVERALL STATISTICS ---")
        logging.info(f"Total requests sent: {overall_total}")
        logging.info(f"Overall successful: {overall_success}")
        logging.info(f"Overall failed: {overall_failure}")
        logging.info(f"Overall success rate: {overall_rate:.1f}%")


def main():
    # 🔧 CONFIGURATION - Update these values
    
    # Method 1: Single URL (backward compatible)
    # STREAMLIT_URLS = "https://mushroom-classification-sk.streamlit.app"
    
    # Method 2: Multiple URLs (recommended for multiple apps)
    STREAMLIT_URLS = [
        "https://mushroom-classification-sk.streamlit.app",
        "https://kmeans-comp.streamlit.app",
        "https://pomodoroui.streamlit.app",
        "https://huggingface.co/spaces/jobannagra/simple-bg-remove"
        # Add more URLs as needed
    ]
    
    PING_INTERVAL = 5  # Minutes between ping cycles (applies to all URLs)
    
    # Validate URLs
    urls_to_check = STREAMLIT_URLS if isinstance(STREAMLIT_URLS, list) else [STREAMLIT_URLS]
    
    for url in urls_to_check:
        if "your-app-name.streamlit.app" in url or "your-second-app" in url or "your-third-app" in url:
            print("[WARNING] Please update STREAMLIT_URLS with your actual Streamlit app URLs!")
            print("Example:")
            print('STREAMLIT_URLS = [')
            print('    "https://mushroom-classification-sk.streamlit.app",')
            print('    "https://my-dashboard.streamlit.app",')
            print('    "https://data-analyzer.streamlit.app"')
            print(']')
            return
    
    # Create and start the keep-alive service
    keepalive = StreamlitKeepAlive(STREAMLIT_URLS, PING_INTERVAL)
    
    print("\n" + "="*60)
    print("MULTI-URL  KEEP-ALIVE SERVICE")
    print("="*60)
    
    if isinstance(STREAMLIT_URLS, list):
        print(f"Target URLs ({len(STREAMLIT_URLS)}):")
        for i, url in enumerate(STREAMLIT_URLS, 1):
            print(f"  {i}. {url}")
    else:
        print(f"Target URL: {STREAMLIT_URLS}")
    
    print(f"Ping interval: {PING_INTERVAL} minutes (for complete cycle)")
    print("Press Ctrl+C to stop the service")
    print("="*60 + "\n")
    
    # Choose running method:
    # Method 1: Simple continuous loop (recommended)
    keepalive.run_continuous()
    
    # Method 2: Using schedule library (alternative)
    # keepalive.run_scheduled()


if __name__ == "__main__":
    main()