#!/usr/bin/env python3
"""
Friday - Simple Working Bot
Just to test if basic functionality works
"""

import requests
import json
import time

class SimpleFriday:
    def __init__(self, token):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}"
        self.offset = 0
        
    def send_message(self, chat_id, text):
        url = f"{self.base_url}/sendMessage"
        data = {"chat_id": chat_id, "text": text}
        try:
            response = requests.post(url, json=data)
            return response.json()
        except Exception as e:
            print(f"Error sending message: {e}")
            return None
    
    def get_updates(self):
        url = f"{self.base_url}/getUpdates"
        params = {"offset": self.offset, "timeout": 10}
        try:
            response = requests.get(url, params=params)
            return response.json()
        except Exception as e:
            print(f"Error getting updates: {e}")
            return {"ok": False, "result": []}
    
    def handle_message(self, message):
        chat_id = message["chat"]["id"]
        text = message.get("text", "")
        user_name = message["from"].get("first_name", "friend")
        
        print(f"Received message: {text} from {user_name}")
        
        if text.startswith("/start"):
            response = f"Hello {user_name}! I'm Friday, your AI assistant. I'm working! 🤖"
        elif "remind" in text.lower():
            response = f"Got it {user_name}! I'll remind you about that. Friday is working! ✅"
        elif "hi" in text.lower() or "hello" in text.lower():
            response = f"Hi {user_name}! Friday here, ready to help! 👋"
        else:
            response = f"I hear you {user_name}! Friday is listening and working perfectly! 😊"
        
        print(f"Sending response: {response}")
        return self.send_message(chat_id, response)
    
    def run(self):
        print("🤖 Simple Friday Bot Starting...")
        print("✅ Bot is now online and listening!")
        print("📱 Send a message to test!")
        print("-" * 40)
        
        while True:
            try:
                updates = self.get_updates()
                
                if updates.get("ok") and updates.get("result"):
                    for update in updates["result"]:
                        self.offset = update["update_id"] + 1
                        
                        if "message" in update:
                            self.handle_message(update["message"])
                
                time.sleep(1)
                
            except KeyboardInterrupt:
                print("\n👋 Bot shutting down...")
                break
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(5)

def main():
    TOKEN = "7949040161:AAHo5p5Hu84fcQcm1Wsa_UDOmXxjOYq2cOo"
    
    print("🔧 Testing bot connection...")
    
    # Test connection first
    test_url = f"https://api.telegram.org/bot{TOKEN}/getMe"
    try:
        response = requests.get(test_url)
        if response.status_code == 200:
            bot_info = response.json()
            print(f"✅ Bot connected: {bot_info['result']['first_name']}")
            print(f"✅ Username: @{bot_info['result']['username']}")
        else:
            print(f"❌ Connection failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return
    
    # Start bot
    bot = SimpleFriday(TOKEN)
    bot.run()

if __name__ == "__main__":
    main()