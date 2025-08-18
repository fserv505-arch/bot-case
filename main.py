import json
import os
import time
import yaml
import yagmail
import schedule
from playwright.sync_api import sync_playwright
import random
from datetime import datetime, time as dt_time, timedelta

# Load config from environment variables or config file
def load_config():
    config = {}
    
    # Try to load from environment variables first (for deployment)
    if os.getenv('GMAIL_USER'):
        config['gmail_user'] = os.getenv('GMAIL_USER')
        config['gmail_password'] = os.getenv('GMAIL_PASSWORD')
        config['qasa_email'] = os.getenv('QASA_EMAIL')
        config['qasa_password'] = os.getenv('QASA_PASSWORD')
        # Only add message_to_owner if we're actually using it
        message = os.getenv('MESSAGE_TO_OWNER')
        if message:
            config['message_to_owner'] = message
    else:
        # Fall back to config file (for local development)
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)
    
    return config

config = load_config()

SEEN_FILE = "/app/seen_listings.json"

# Personalizable search URL and recipient email
DEFAULT_SEARCH_URL = "https://qasa.se/en/find-home?furnished=furnished&maxMonthlyCost=12300&maxRoomCount=4&searchAreas=Stockholm~~se&sharedHome=privateHome"
FILTERED_URL = os.getenv('SEARCH_URL') or config.get('search_url', DEFAULT_SEARCH_URL)
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL') or config.get('recipient_email', config.get('gmail_user'))

# Load previously seen listing IDs
if os.path.exists(SEEN_FILE):
    with open(SEEN_FILE, "r") as f:
        seen_ids = set(json.load(f))
else:
    seen_ids = set()

def save_seen_ids():
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen_ids), f)

def send_email(listing):
    # Check if emails are disabled
    if os.getenv('DISABLE_EMAILS', 'false').lower() == 'true':
        print(f"Emails disabled - would have sent: {listing['title']}")
        return
        
    try:
        yag = yagmail.SMTP(config['gmail_user'], config['gmail_password'])
        subject = f"🏠 New Qasa Listing: {listing['title']} – {listing['price']} SEK"
        body = f"""
New apartment found:

📍 Location: {listing['location']}
💰 Price: {listing['price']} SEK
🛏️ Rooms: {listing['rooms']}
📅 Move-in: {listing['move_in_date']}
🔗 Link: {listing['url']}

Automatically found by your Qasa bot.
"""
        yag.send(to=RECIPIENT_EMAIL, subject=subject, contents=body)
        print(f"Email sent for: {listing['title']}")
    except Exception as e:
        print(f"Failed to send email: {e}")

def scrape_qasa():
    print("Checking Qasa for new listings...")
    
    # Debug: Check browser installation
    import os
    import subprocess
    try:
        # Check if browsers are installed
        result = subprocess.run(['playwright', 'install', '--dry-run'], capture_output=True, text=True)
        print(f"Browser check result: {result.stdout}")
        
        # Check browser cache directory
        cache_dir = os.path.expanduser("~/.cache/ms-playwright")
        if os.path.exists(cache_dir):
            print(f"Browser cache exists at: {cache_dir}")
            import subprocess
            result = subprocess.run(['ls', '-la', cache_dir], capture_output=True, text=True)
            print(f"Cache contents: {result.stdout}")
        else:
            print(f"Browser cache not found at: {cache_dir}")
            
    except Exception as e:
        print(f"Debug check failed: {e}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
        context = browser.new_context()
        page = context.new_page()

        page.goto(FILTERED_URL)
        page.wait_for_timeout(4000)

        try:
            page.click('button:has-text("Accept")')
            print("Accepted cookies.")
            page.wait_for_timeout(1000)
        except Exception as e:
            print(f"No cookie popup or failed to accept cookies: {e}")

        new_found = 0

        def parse_price_from_html(html_text: str) -> int:
            try:
                import re
                match = re.search(r'([0-9][0-9\s\xa0,\.]+)\s*(SEK|kr)', html_text, re.IGNORECASE)
                if not match:
                    return 0
                digits = ''.join(ch for ch in match.group(1) if ch.isdigit())
                return int(digits) if digits else 0
            except Exception:
                return 0

        def handle_blocket_domain():
            nonlocal new_found
            print("Detected Blocket Bostad domain. Using Blocket scraper.")
            # Try to find listing anchors
            try:
                cards = page.query_selector_all('a[href^="/en/home/"], a[href*="/home/"]')
                print(f"Found {len(cards)} potential listing links on Blocket page.")
            except Exception as e:
                print(f"Error finding Blocket listings: {e}")
                print(page.content())
                cards = []

            seen_hrefs = set()
            for card in cards:
                try:
                    href = card.get_attribute("href")
                    if not href or 'find-home' in href:
                        continue
                    if href in seen_hrefs:
                        continue
                    seen_hrefs.add(href)

                    listing_id = href.rstrip('/').split('/')[-1]
                    if listing_id in seen_ids:
                        continue

                    detail_url = href if href.startswith('http') else f"https://bostad.blocket.se{href}"
                    detail_page = context.new_page()
                    try:
                        detail_page.goto(detail_url)
                        detail_page.wait_for_timeout(3000)
                        try:
                            detail_page.click('button:has-text("Accept")')
                            detail_page.wait_for_timeout(500)
                        except Exception:
                            pass

                        # Extract details from detail page for robustness
                        try:
                            title = detail_page.query_selector('h1').inner_text()
                        except Exception:
                            title = 'Unknown'

                        try:
                            html_text = detail_page.content()
                            price = parse_price_from_html(html_text)
                        except Exception:
                            price = 0

                        listing_data = {
                            'id': listing_id,
                            'title': title,
                            'location': 'Unknown',
                            'price': price,
                            'url': detail_url,
                            'move_in_date': 'Unknown',
                            'rooms': '?'
                        }

                        seen_ids.add(listing_id)
                        print(f"New listing found (Blocket): {listing_id} - {listing_data['title']}")
                        send_email(listing_data)
                        new_found += 1
                    finally:
                        try:
                            detail_page.close()
                        except Exception:
                            pass
                except Exception as e:
                    print(f"Error processing Blocket listing: {e}")

        def handle_qasa_domain():
            nonlocal new_found
            print("Detected Qasa domain. Using Qasa scraper.")
            try:
                listings = page.query_selector_all('a[href^="/en/home/"]')
                print(f"Found {len(listings)} listings on the page.")
            except Exception as e:
                print(f"Error finding listings: {e}")
                print(page.content())
                listings = []

            for card in listings:
                try:
                    href = card.get_attribute("href")
                    if not href:
                        continue
                    listing_id = href.split("/")[-1]
                    print(f"Checking listing: {listing_id}")
                    if listing_id in seen_ids:
                        print(f"Already seen: {listing_id}")
                        continue

                    try:
                        title = card.query_selector("h2").inner_text()
                    except Exception:
                        title = "Unknown"
                    try:
                        location = page.query_selector("h1").inner_text()
                    except Exception:
                        location = "Unknown"
                    try:
                        price_text = card.query_selector(".eq1ubw50").inner_text()
                        price = int(price_text.replace("SEK", "").replace("\xa0", "").replace(",", "").strip())
                    except Exception as e:
                        print(f"Error parsing price: {e}")
                        price = 0
                    url = f"https://qasa.se{href}"
                    try:
                        date_spans = page.query_selector_all("div.qds-d3xutt .qds-10hlnxp.erqv7p41")
                        move_in_date = date_spans[0].inner_text() if len(date_spans) > 0 else "Unknown"
                        move_out_date = date_spans[1].inner_text() if len(date_spans) > 1 else "Unknown"
                    except Exception:
                        move_in_date = "Unknown"
                    try:
                        rooms = card.query_selector_all(".qds-10hlnxp.erqv7p41")[1].inner_text()
                    except Exception:
                        rooms = "?"

                    listing_data = {
                        "id": listing_id,
                        "title": title,
                        "location": location,
                        "price": price,
                        "url": url,
                        "move_in_date": move_in_date,
                        "rooms": rooms
                    }

                    seen_ids.add(listing_id)
                    print(f"New listing found: {listing_id} - {listing_data['title']}")
                    send_email(listing_data)
                    new_found += 1
                except Exception as e:
                    print(f"Error processing listing: {e}\nListing URL: {url if 'url' in locals() else 'unknown'}")

        # Choose scraper by domain
        if 'bostad.blocket.se' in FILTERED_URL:
            handle_blocket_domain()
        else:
            handle_qasa_domain()

        save_seen_ids()
        print(f"{new_found} new listings found.")
        print(f"Total seen listings: {len(seen_ids)}")

        browser.close()

def get_random_delay():
    # Use a triangular distribution for more natural intervals
    # min=10, max=35, mode=25 (mean will be around 25)
    # But ensure minimum 10 minutes to avoid spam
    delay = random.triangular(10, 35, 25)
    return max(delay, 10)  # Minimum 10 minutes

def is_active_hours():
    """Check if current time is within active hours (7 AM to 11 PM)"""
    current_time = datetime.now().time()
    
    # Get hours from config or use defaults
    start_hour = int(os.getenv('ACTIVE_START_HOUR', 7))
    end_hour = int(os.getenv('ACTIVE_END_HOUR', 23))
    
    start_time = dt_time(start_hour, 0)
    end_time = dt_time(end_hour, 0)
    
    return start_time <= current_time <= end_time

def get_sleep_until_active():
    """Calculate minutes until next active period"""
    current_time = datetime.now()
    
    # Get hours from config or use defaults
    start_hour = int(os.getenv('ACTIVE_START_HOUR', 7))
    end_hour = int(os.getenv('ACTIVE_END_HOUR', 23))
    
    tomorrow = current_time.replace(hour=start_hour, minute=0, second=0, microsecond=0) + timedelta(days=1)
    
    if current_time.hour >= end_hour:  # After end time
        return (tomorrow - current_time).total_seconds() / 60
    else:  # Before start time
        today_start = current_time.replace(hour=start_hour, minute=0, second=0, microsecond=0)
        return (today_start - current_time).total_seconds() / 60

while True:
    if is_active_hours():
        scrape_qasa()
        delay = get_random_delay()
        print(f"Next check in {int(delay)} minutes...")
        time.sleep(delay * 60)
    else:
        sleep_minutes = get_sleep_until_active()
        start_hour = int(os.getenv('ACTIVE_START_HOUR', 7))
        end_hour = int(os.getenv('ACTIVE_END_HOUR', 23))
        print(f"Outside active hours ({start_hour}:00 - {end_hour}:00). Sleeping until {start_hour}:00...")
        print(f"Sleeping for {int(sleep_minutes)} minutes...")
        time.sleep(sleep_minutes * 60)