import cloudscraper
from bs4 import BeautifulSoup
import time
import threading
import os
from flask import Flask

# --- FLASK WEB SERVER SETUP ---
app = Flask(__name__)

@app.route('/')
def home():
    return "I am alive! The bot is running in the background."

# --- YOUR BOT SETTINGS ---
URL = "https://www.kisa.ge/donate/8y4nomx7jd"
BOT_TOKEN = "8687584211:AAH3F6gYHEtkdZujkR818zlqd_8hDq_BXpc"
CHANNEL_ID = "-5148905806" 
HTML_CLASS = "text-[32px] font-medium text-default50" 

# --- CLOUDFLARE BYPASS ENGINE ---
# This creates a scraper that acts exactly like Google Chrome on Windows
scraper = cloudscraper.create_scraper(browser={
    'browser': 'chrome',
    'platform': 'windows',
    'desktop': True
})

def get_current_amount():
    try:
        # CACHE BUSTER: Add the exact time to the URL so the server gives us live data
        cache_busting_url = f"{URL}?t={int(time.time())}"
        
        # We use 'scraper.get' instead of 'requests.get' to bypass security
        response = scraper.get(cache_busting_url)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        element = soup.find('p', class_=HTML_CLASS) 
        
        if element:
            raw_text = element.text
            clean_text = raw_text.replace('₾', '').replace(',', '').replace('\n', '').strip()
            return float(clean_text)
        else:
            print(f"Element not found! Server returned Status Code: {response.status_code}")
            # If it fails, print the first 200 characters of what Render actually saw to help us debug
            print(f"What Render saw: {response.text[:200]}")
            return None
    except Exception as e:
        print(f"Error checking website: {e}")
    return None

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHANNEL_ID, "text": message}
    try:
        scraper.post(url, data=data)
    except Exception as e:
        print(f"Error sending message: {e}")

# --- MAIN BOT LOOP ---
def run_bot():
    print("Bot background thread is starting...")
    previous_amount = None
    
    while True:
        try:
            current_amount = get_current_amount()
            
            if current_amount is not None:
                if previous_amount is None:
                    previous_amount = current_amount
                    print(f"Initial amount recorded: {current_amount} GEL")
                elif current_amount > previous_amount:
                    difference = current_amount - previous_amount
                    message = f"თქვენი პროდუქტი გაიყიდა +{difference} GEL"
                    send_telegram_message(message)
                    print(f"Update: {current_amount} GEL. Message sent.")
                    previous_amount = current_amount
                else:
                    print(f"Checked site. Unchanged: {current_amount} GEL.")
        except Exception as e:
            print(f"Error in bot loop: {e}")
            
        # Wait 60 seconds before checking again
        time.sleep(60) 

# --- START THE BACKGROUND THREAD GLOBALLY ---
# Placing it here forces Render's Gunicorn server to run it immediately
bot_thread = threading.Thread(target=run_bot)
bot_thread.daemon = True 
bot_thread.start()

# --- START THE WEB SERVER ---
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
