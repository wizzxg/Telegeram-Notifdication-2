import requests
from bs4 import BeautifulSoup
import time

# --- YOUR SETTINGS ---
URL = "https://www.kisa.ge/donate/8y4nomx7jd"
BOT_TOKEN = "8687584211:AAH3F6gYHEtkdZujkR818zlqd_8hDq_BXpc"
CHANNEL_ID = "-1003900072136" # Removed the '#' for the Telegram API
HTML_CLASS = "text-[32px] font-medium text-default50" 

# Keep track of the last amount we saw
previous_amount = None

def get_current_amount():
    try:
        # 1. Download the webpage
        response = requests.get(URL)
        
        # 2. Read the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 3. Find the specific <p> element holding the number
        element = soup.find('p', class_=HTML_CLASS) 
        
        if element:
            # 4. Clean the text: remove the Lari symbol (₾), commas, newlines, and spaces
            # (Your HTML image shows the number and symbol are split across multiple lines)
            raw_text = element.text
            clean_text = raw_text.replace('₾', '').replace(',', '').replace('\n', '').strip()
            
            # 5. Convert it to a number 
            return float(clean_text)
        else:
            print("Could not find the element on the page. The website might be using JavaScript to load this data.")
            return None
            
    except Exception as e:
        print(f"Error checking website: {e}")
        return None

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHANNEL_ID,
        "text": message
    }
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print("Message sent to Telegram successfully!")
        else:
            print(f"Failed to send message. Telegram API response: {response.text}")
    except Exception as e:
        print(f"Error sending message: {e}")

# --- MAIN BOT LOOP ---
print("Bot is starting...")

while True:
    current_amount = get_current_amount()
    
    if current_amount is not None:
        # If this is the first time running, just save the current amount
        if previous_amount is None:
            previous_amount = current_amount
            print(f"Initial amount recorded: {current_amount} GEL")
            
        # If the new amount is higher than the old amount
        elif current_amount > previous_amount:
            difference = current_amount - previous_amount
            
            # Create the Georgian message
            message = f"თქვენი პროდუქტი გაიყიდა +{difference} GEL"
            
            # Send the message and update the previous amount
            send_telegram_message(message)
            print(f"Update detected! New total is {current_amount} GEL. Message sent.")
            previous_amount = current_amount
        else:
            print(f"Checked site. Amount unchanged: {current_amount} GEL.")
            
    # Wait for 60 seconds before checking the website again
    time.sleep(60)