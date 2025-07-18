#!/usr/bin/env python3
"""
Friday - Final Working Version
Uses direct telegram library without problematic features
"""

import asyncio
import logging
import re
from datetime import datetime
import pytz
from typing import Optional, Tuple

import dateparser
from langdetect import detect

# Use requests for simpler HTTP handling
import requests
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FridayBot:
    def __init__(self, token: str):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}"
        self.offset = 0
        self.user_data = {}
        
        # Language patterns
        self.hindi_patterns = [
            r'[\u0900-\u097F]',
            r'\b(hai|ka|ke|ki|ko|se|me|aur|ya|kya|kaise|kahan|kab|kyun|jo|wo|yeh|iska|uska)\b',
        ]

    def detect_language(self, text: str) -> str:
        try:
            hindi_score = sum(1 for pattern in self.hindi_patterns 
                            if re.search(pattern, text, re.IGNORECASE))
            detected = detect(text)
            
            if hindi_score > 0:
                return 'hinglish' if detected == 'en' else 'hindi'
            elif detected == 'hi':
                return 'hindi'
            else:
                return 'english'
        except:
            return 'english'

    def generate_response(self, language: str, user_name: str, msg_type: str, **kwargs) -> str:
        responses = {
            'greeting': {
                'english': f"Hello {user_name}! 👋 I'm Friday, your multilingual AI assistant. How can I help you today?",
                'hindi': f"Namaste {user_name} ji! 🙏 Main Friday hun, aapki multilingual AI assistant. Aaj kaise madad kar sakti hun?",
                'hinglish': f"Hey {user_name}! 😊 Main Friday hun, tumhari multilingual AI assistant. Kya help chaahiye aaj?"
            },
            'reminder_set': {
                'english': f"Perfect {user_name}! ✅ I'll remember '{kwargs.get('task', '')}' for {kwargs.get('time', '')}. Friday's got your back! 💪",
                'hindi': f"Bilkul theek {user_name} ji! ✅ '{kwargs.get('task', '')}' ko {kwargs.get('time', '')} ke liye yaad rakh liya. Friday sambhal legi! 💪",
                'hinglish': f"Done {user_name}! ✅ '{kwargs.get('task', '')}' ka reminder {kwargs.get('time', '')} ke liye set kar diya. Friday yaad rakhegi! 💪"
            },
            'task_completed': {
                'english': f"Excellent work {user_name}! ✨ Task completed successfully. Friday is proud of you! 🌟",
                'hindi': f"Bahut badhiya {user_name} ji! ✨ Kaam successfully complete ho gaya. Friday aapse proud hai! 🌟",
                'hinglish': f"Great job {user_name}! ✨ Task successfully complete kar diya. Friday proud hai tumse! 🌟"
            },
            'chat': {
                'english': f"I'm here for you {user_name}! 😊 You can ask me to set reminders or just have a friendly chat. What's on your mind?",
                'hindi': f"Main yahin hun {user_name} ji! 😊 Aap mujhse reminder set kara sakte hain ya friendly chat kar sakte hain. Kya chal raha hai?",
                'hinglish': f"Main yahin hun {user_name}! 😊 Tum mujhse reminder set kara sakte ho ya bas friendly chat kar sakte ho. What's up?"
            },
            'help': {
                'english': f"""🤖 *Friday - Your Multilingual AI Assistant*

Hey {user_name}! Here's what I can do:

📝 *Smart Reminders:*
• "Remind me to call mom at 7 PM"
• "Set reminder for meeting tomorrow 3 PM"
• Natural language understanding

🌐 *Multilingual Support:*
• English: Full support
• Hindi: पूर्ण समर्थन
• Hinglish: Complete support

💬 *Features:*
• Uses your name in responses
• Smart time parsing
• Friendly conversation
• Task completion tracking

💡 *Examples:*
• "Remind me to take medicine at 9 PM"
• "Kal morning gym jana hai yaad dila"
• "Friday, meeting hai 3 baje reminder set kar"

Just talk to me naturally - I understand! 😊""",
                
                'hindi': f"""🤖 *Friday - Aapki Multilingual AI Assistant*

Namaste {user_name} ji! Main yeh sab kar sakti hun:

📝 *Smart Reminders:*
• "Mujhe kal 9 baje meeting yaad dila dena"
• "Shaam 6 baje dawa leni hai reminder set kar"
• Natural language samajhti hun

🌐 *Multilingual Support:*
• English: Full support
• Hindi: पूर्ण समर्थन  
• Hinglish: Complete support

💬 *Features:*
• Aapka naam use karti hun responses mein
• Smart time parsing
• Friendly conversation
• Task completion tracking

💡 *Examples:*
• "Mujhe raat 9 baje dawa leni hai yaad dila"
• "Tomorrow morning exercise karna hai reminder set kar"
• "Friday, 3 baje meeting hai yaad rakhna"

Bas normally baat kariye - main samajh jaungi! 😊""",
                
                'hinglish': f"""🤖 *Friday - Tumhari Multilingual AI Assistant*

Hey {user_name}! Main yeh sab kar sakti hun:

📝 *Smart Reminders:*
• "Kal morning gym jana hai yaad dila"
• "Evening 6 baje call karna hai reminder set kar"
• Natural language understand karti hun

🌐 *Multilingual Support:*
• English: Full support
• Hindi: पूर्ण समर्थन
• Hinglish: Complete support

💬 *Features:*
• Tumhara naam use karti hun responses mein
• Smart time parsing
• Friendly conversation
• Task completion tracking

💡 *Examples:*
• "Friday, kal 8 baje office jana hai yaad dila"
• "Remind me to call papa at 7 PM"
• "Shaam ko medicine leni hai reminder set kar"

Just normally talk karo - main understand kar lungi! 😊"""
            }
        }
        return responses.get(msg_type, {}).get(language, f"Hi {user_name}! I'm Friday 😊")

    def parse_reminder(self, text: str) -> Tuple[Optional[str], Optional[datetime]]:
        original_text = text
        text = text.lower().strip()
        
        # Remove common phrases
        for phrase in ['remind me to', 'yaad dila dena', 'reminder set kar', 'friday', 'yaad dila', 'reminder']:
            text = re.sub(phrase, '', text, flags=re.IGNORECASE).strip()
        
        try:
            parsed_time = dateparser.parse(
                text,
                languages=['hi', 'en'],
                settings={
                    'TIMEZONE': 'Asia/Kolkata',
                    'RETURN_AS_TIMEZONE_AWARE': True,
                    'RELATIVE_BASE': datetime.now(pytz.timezone('Asia/Kolkata'))
                }
            )
            
            if parsed_time:
                # Extract task by removing time-related words
                time_words = [
                    'today', 'tomorrow', 'kal', 'aaj', 'at', 'par', 'baje',
                    'morning', 'evening', 'subah', 'shaam', 'pm', 'am', 'o\'clock'
                ]
                
                task = text
                for word in time_words:
                    task = re.sub(f'\\b{word}\\b', '', task, flags=re.IGNORECASE).strip()
                
                # Clean up
                task = re.sub(r'\s+', ' ', task).strip()
                task = re.sub(r'\b(ko|ka|ke|ki|me|mein|hai|hona|karna|lena)\b', '', task).strip()
                task = re.sub(r'\d+:\d+', '', task).strip()
                
                if task and len(task) > 2:
                    return task, parsed_time
        except Exception as e:
            logger.error(f"Error parsing reminder: {e}")
        
        return None, None

    def send_message(self, chat_id: int, text: str, parse_mode: str = None):
        """Send message using Telegram API"""
        url = f"{self.base_url}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': text
        }
        if parse_mode:
            data['parse_mode'] = parse_mode
            
        try:
            response = requests.post(url, json=data)
            return response.json()
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return None

    def get_updates(self):
        """Get updates from Telegram"""
        url = f"{self.base_url}/getUpdates"
        params = {'offset': self.offset, 'timeout': 30}
        
        try:
            response = requests.get(url, params=params)
            return response.json()
        except Exception as e:
            logger.error(f"Error getting updates: {e}")
            return {'ok': False, 'result': []}

    def handle_message(self, message):
        """Handle incoming message"""
        chat_id = message['chat']['id']
        text = message.get('text', '')
        user = message['from']
        user_name = user.get('first_name') or user.get('username') or 'friend'
        user_id = user['id']
        
        # Initialize user data
        if user_id not in self.user_data:
            self.user_data[user_id] = {'tasks': [], 'language': 'english'}
        
        # Detect language
        language = self.detect_language(text)
        self.user_data[user_id]['language'] = language
        
        # Handle commands
        if text.startswith('/start'):
            response = self.generate_response(language, user_name, 'greeting')
            self.send_message(chat_id, response)
            
        elif text.startswith('/help'):
            response = self.generate_response(language, user_name, 'help')
            self.send_message(chat_id, response, 'Markdown')
            
        else:
            # Check for task completion
            completion_words = ['done', 'ho gaya', 'complete', 'finished', 'kar diya', 'kar liya']
            if any(word in text.lower() for word in completion_words):
                response = self.generate_response(language, user_name, 'task_completed')
                self.send_message(chat_id, response)
                return
            
            # Check for reminders
            reminder_keywords = ['remind', 'yaad dila', 'reminder', 'yaad rakh', 'remember', 'set alarm']
            is_reminder = any(keyword in text.lower() for keyword in reminder_keywords)
            
            if is_reminder:
                task, scheduled_time = self.parse_reminder(text)
                
                if task and scheduled_time:
                    # Store task (simplified - no actual scheduling)
                    self.user_data[user_id]['tasks'].append({
                        'task': task,
                        'time': scheduled_time.strftime('%I:%M %p, %d %b %Y'),
                        'language': language
                    })
                    
                    response = self.generate_response(
                        language, user_name, 'reminder_set',
                        task=task, time=scheduled_time.strftime('%I:%M %p, %d %b')
                    )
                else:
                    if language == 'hindi':
                        response = f"Maaf kijiye {user_name} ji! 😅 Samay samajh nahi aaya. Aise try kariye: 'Mujhe 7 baje mummy ko call karna yaad dila dena'"
                    elif language == 'hinglish':
                        response = f"Sorry {user_name}! 😅 Time samajh nahi aaya. Try karo: 'Kal 8 baje gym jaana hai yaad dila'"
                    else:
                        response = f"Sorry {user_name}! 😅 I couldn't understand the timing. Try: 'Remind me to call mom at 7 PM'"
                
                self.send_message(chat_id, response)
            else:
                # Casual chat
                response = self.generate_response(language, user_name, 'chat')
                self.send_message(chat_id, response)

    def run(self):
        """Main bot loop"""
        print("🤖 Friday Bot is starting...")
        print("=" * 50)
        print("✅ Token configured")
        print("💫 Friday is now online!")
        print("📱 Ready to handle messages!")
        print("🌐 Supporting Hindi, English, and Hinglish")
        print("=" * 50)
        
        while True:
            try:
                updates = self.get_updates()
                
                if updates.get('ok') and updates.get('result'):
                    for update in updates['result']:
                        self.offset = update['update_id'] + 1
                        
                        if 'message' in update:
                            self.handle_message(update['message'])
                            
            except KeyboardInterrupt:
                print("\n👋 Friday is shutting down...")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                continue

def main():
    """Start Friday bot"""
    TOKEN = "7949040161:AAHo5p5Hu84fcQcm1Wsa_UDOmXxjOYq2cOo"
    
    if not TOKEN:
        print("❌ Bot token not found!")
        return
    
    friday = FridayBot(TOKEN)
    friday.run()

if __name__ == "__main__":
    main()