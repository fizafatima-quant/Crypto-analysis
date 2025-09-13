import requests

BOT_TOKEN = "8372914316:AAFYI6nE5fRckNJdyAfXNeerAp2hxbpV_rY"

def get_chat_id():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    try:
        response = requests.get(url)
        data = response.json()
        print(data)  # full JSON
        # Try to print the chat ID of the last message
        if data["result"]:
            chat_id = data["result"][-1]["message"]["chat"]["id"]
            print(f"Your chat ID is: {chat_id}")
        else:
            print("No messages found. Send a message to your bot first!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_chat_id()
