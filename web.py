from flask import Flask
import threading
import os
import sys

# Import and run the main bot in a separate thread
def run_bot():
    import main
    # Run the main bot loop
    while True:
        try:
            main.scrape_qasa()
            import time
            import random
            delay = main.get_random_delay()
            print(f"Next check in {int(delay)} minutes...")
            time.sleep(delay * 60)
        except Exception as e:
            print(f"Error in bot loop: {e}")
            time.sleep(60)  # Wait 1 minute before retrying

app = Flask(__name__)

@app.route('/')
def health_check():
    return "Qasa Bot is running! 🏠"

@app.route('/health')
def health():
    return {"status": "healthy", "service": "qasa-bot"}

if __name__ == '__main__':
    # Start the bot in a background thread
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Start the web server
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port) 