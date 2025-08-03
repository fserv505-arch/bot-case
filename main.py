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
        config['message_to_owner'] = os.getenv('MESSAGE_TO_OWNER', 'Hi! I\'m interested in your apartment.')
    else:
        # Fall back to config file (for local development)
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)
    
    return config

config = load_config()

SEEN_FILE = "seen_listings.json"
FILTERED_URL = "https://qasa.se/en/find-home?furnished=furnished&maxMonthlyCost=12300&maxRoomCount=4&searchAreas=Stockholm~~se&sharedHome=privateHome"

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
        yag.send(to=config['gmail_user'], subject=subject, contents=body)
        print(f"Email sent for: {listing['title']}")
    except Exception as e:
        print(f"Failed to send email: {e}")

def scrape_qasa():
    print("Checking Qasa for new listings...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
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

        try:
            # Updated selector for Qasa listing cards
            listings = page.query_selector_all('a[href^="/en/home/"]')
            print(f"Found {len(listings)} listings on the page.")
        except Exception as e:
            print(f"Error finding listings: {e}")
            print(page.content())  # Print the HTML for debugging
            listings = []

        new_found = 0

        for card in listings:
            try:
                href = card.get_attribute("href")
                if not href:
                    continue
                listing_id = href.split("/")[-1]
                if listing_id in seen_ids:
                    continue

                # Extract title
                try:
                    title = card.query_selector("h2").inner_text()
                except Exception:
                    title = "Unknown"
                # Extract location
                try:
                    location = page.query_selector("h1").inner_text()
                except Exception:
                    location = "Unknown"
                # Extract price
                try:
                    price_text = card.query_selector(".eq1ubw50").inner_text()
                    price = int(price_text.replace("SEK", "").replace("\xa0", "").replace(",", "").strip())
                except Exception as e:
                    print(f"Error parsing price: {e}")
                    price = 0
                url = f"https://qasa.se{href}"
                # Extract move-in date
                try:
                    date_spans = page.query_selector_all("div.qds-d3xutt .qds-10hlnxp.erqv7p41")
                    move_in_date = date_spans[0].inner_text() if len(date_spans) > 0 else "Unknown"
                    move_out_date = date_spans[1].inner_text() if len(date_spans) > 1 else "Unknown"
                except Exception:
                    move_in_date = "Unknown"
                # Extract rooms
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

                # Save and act
                seen_ids.add(listing_id)
                send_email(listing_data)
                # contact_landlord(page, listing_data)  # This line is now removed

                new_found += 1
            except Exception as e:
                print(f"Error processing listing: {e}\nListing URL: {url if 'url' in locals() else 'unknown'}")

        save_seen_ids()
        print(f"{new_found} new listings found.")

        browser.close()

def get_random_delay():
    # Use a triangular distribution for more natural intervals
    # min=5, max=40, mode=22 (mean will be above 20)
    return random.triangular(5, 40, 22)

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