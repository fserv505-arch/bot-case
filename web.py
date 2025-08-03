from flask import Flask
import threading
import os
import sys

# Import and run the main bot in a separate thread
def run_bot():
    import main
    main.scrape_qasa()  # Run the main bot logic

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