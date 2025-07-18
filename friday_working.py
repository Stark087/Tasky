#!/usr/bin/env python3
"""
Friday - Working Telegram Bot
Simplified version that avoids compatibility issues
"""

import logging
import re
from datetime import datetime, timedelta
import pytz
from typing import Optional, Tuple

# Telegram imports
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# NLP imports
import dateparser
from langdetect import detect

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Friday:
    def __init__(self):
        self.user_data = {}
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

    def get_user_name(self, update: Update) -> str:
        user = update.effective_user
        return user.first_name or user.username or "friend"

    def generate_response(self, language: str, user_name: str, msg_type: str, **kwargs) -> str:
        responses = {
            'greeting': {
                'english': f"Hello {user_name}! 👋 I'm Friday, your AI assistant. How can I help?",
                'hindi': f"Namaste {user_name} ji! 🙏 Main Friday hun, aapki AI assistant. Kaise madad kar sakti hun?",
                'hinglish': f"Hey {user_name}! 😊 Main Friday hun, tumhari AI assistant. Kya help chaahiye?"
            },
            'reminder_set': {
                'english': f"Perfect {user_name}! ✅ Reminder set for '{kwargs.get('task', '')}' at {kwargs.get('time', '')}. Friday's got you! 💪",
                'hindi': f"Bilkul theek {user_name} ji! ✅ '{kwargs.get('task', '')}' ka reminder {kwargs.get('time', '')} par set kar diya. Friday sambhal legi! 💪",
                'hinglish': f"Done {user_name}! ✅ '{kwargs.get('task', '')}' ka reminder {kwargs.get('time', '')} par set kar diya! 💪"
            },
            'task_completed': {
                'english': f"Awesome {user_name}! ✨ Task completed. Friday is proud! 🌟",
                'hindi': f"Bahut badhiya {user_name} ji! ✨ Kaam complete! Friday khush hai! 🌟",
                'hinglish': f"Great job {user_name}! ✨ Task complete kar diya! Friday proud hai! 🌟"
            },
            'chat': {
                'english': f"I'm here for you {user_name}! 😊 Ask me to set reminders or just chat!",
                'hindi': f"Main yahin hun {user_name} ji! 😊 Reminder set karne ke liye ya chat karne ke liye!",
                'hinglish': f"Main yahin hun {user_name}! 😊 Reminder set karo ya bas chat karo!"
            },
            'help': {
                'english': f"""🤖 *Friday AI Assistant*

Hey {user_name}! I can help you with:

📝 *Reminders:*
• "Remind me to call mom at 7 PM"
• "Set reminder for gym tomorrow 9 AM"

🌐 *Languages:*
• Hindi, English, Hinglish - sab samajhti hun!

💬 *Commands:*
• /start - Get started
• /help - This help message

Just talk naturally - I'll understand! 😊""",
                'hindi': f"""🤖 *Friday AI Assistant*

Namaste {user_name} ji! Main yeh kar sakti hun:

📝 *Reminders:*
• "Mujhe kal 9 baje meeting yaad dila dena"
• "Shaam 6 baje dawa leni hai reminder set kar"

🌐 *Languages:*
• Hindi, English, Hinglish - sab samajhti hun!

💬 *Commands:*
• /start - Shuru karne ke liye
• /help - Yeh help message

Bas normally baat kariye! 😊""",
                'hinglish': f"""🤖 *Friday AI Assistant*

Hey {user_name}! Main yeh kar sakti hun:

📝 *Reminders:*
• "Kal morning gym jana hai yaad dila"
• "Evening call karna hai reminder set kar"

🌐 *Languages:*
• Hindi, English, Hinglish - sab understand karti hun!

💬 *Commands:*
• /start - Start karne ke liye
• /help - Yeh help message

Just normally talk karo! 😊"""
            }
        }
        return responses.get(msg_type, {}).get(language, f"Hi {user_name}! I'm Friday 😊")

    def parse_reminder(self, text: str) -> Tuple[Optional[str], Optional[datetime]]:
        text = text.lower().strip()
        
        # Remove common phrases
        for phrase in ['remind me to', 'yaad dila dena', 'reminder set kar', 'friday']:
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
                # Extract task
                time_words = ['today', 'tomorrow', 'kal', 'at', 'par', 'baje', 'morning', 'evening', 'pm', 'am']
                task = text
                for word in time_words:
                    task = re.sub(word, '', task, flags=re.IGNORECASE).strip()
                task = re.sub(r'\s+', ' ', task).strip()
                task = re.sub(r'\b(ko|ka|ke|ki|me|mein|hai)\b', '', task).strip()
                
                if task and len(task) > 2:
                    return task, parsed_time
        except:
            pass
        
        return None, None

friday = Friday()

async def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user_name = friday.get_user_name(update)
    
    if user_id not in friday.user_data:
        friday.user_data[user_id] = {'tasks': [], 'language': 'english'}
    
    language = friday.detect_language(update.message.text)
    response = friday.generate_response(language, user_name, 'greeting')
    await update.message.reply_text(response)

async def help_command(update: Update, context: CallbackContext):
    user_name = friday.get_user_name(update)
    user_id = update.effective_user.id
    
    language = friday.user_data.get(user_id, {}).get('language', 'english')
    help_text = friday.generate_response(language, user_name, 'help')
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def handle_message(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user_name = friday.get_user_name(update)
    message_text = update.message.text
    language = friday.detect_language(message_text)
    
    # Initialize user data
    if user_id not in friday.user_data:
        friday.user_data[user_id] = {'tasks': [], 'language': language}
    else:
        friday.user_data[user_id]['language'] = language
    
    # Check for completion
    completion_words = ['done', 'ho gaya', 'complete', 'kar diya']
    if any(word in message_text.lower() for word in completion_words):
        response = friday.generate_response(language, user_name, 'task_completed')
        await update.message.reply_text(response)
        return
    
    # Check for reminders
    reminder_keywords = ['remind', 'yaad dila', 'reminder', 'yaad rakh', 'remember']
    is_reminder = any(keyword in message_text.lower() for keyword in reminder_keywords)
    
    if is_reminder:
        task, scheduled_time = friday.parse_reminder(message_text)
        
        if task and scheduled_time:
            # Store task
            friday.user_data[user_id]['tasks'].append({
                'task': task,
                'time': scheduled_time.strftime('%I:%M %p, %d %b'),
                'language': language
            })
            
            response = friday.generate_response(
                language, user_name, 'reminder_set',
                task=task, time=scheduled_time.strftime('%I:%M %p, %d %b')
            )
        else:
            response = f"Sorry {user_name}! 😅 Try like 'Remind me to call mom at 7 PM'"
        
        await update.message.reply_text(response)
    else:
        # Casual chat
        response = friday.generate_response(language, user_name, 'chat')
        await update.message.reply_text(response)

def main():
    """Start Friday bot"""
    TOKEN = "7949040161:AAHo5p5Hu84fcQcm1Wsa_UDOmXxjOYq2cOo"
    
    print("🤖 Starting Friday Bot...")
    print("=" * 40)
    
    # Create application
    app = Application.builder().token(TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✅ Friday is online!")
    print("💫 Ready to help with reminders!")
    print("📱 Message your bot to start!")
    print("=" * 40)
    
    # Start polling
    app.run_polling()

if __name__ == "__main__":
    main()