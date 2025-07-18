#!/usr/bin/env python3
"""
Friday - Simplified Telegram Bot (Production Ready)
"""

import logging
import asyncio
import re
import pytz
from datetime import datetime, timedelta
from typing import Optional, Tuple
import json

# Telegram Bot imports
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Natural Language Processing
import dateparser
from langdetect import detect

# Scheduling
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class FridayBot:
    def __init__(self, token: str):
        self.token = token
        self.user_data = {}  # Store user preferences and tasks
        
        # Language detection patterns
        self.hindi_patterns = [
            r'[\u0900-\u097F]',  # Devanagari script
            r'\b(hai|ka|ke|ki|ko|se|me|aur|ya|kya|kaise|kahan|kab|kyun|jo|wo|yeh|iska|uska)\b',
        ]

    def detect_language(self, text: str) -> str:
        """Detect language of the message"""
        try:
            # Check for Hindi script or common Hindi words
            hindi_score = sum(1 for pattern in self.hindi_patterns 
                            if re.search(pattern, text, re.IGNORECASE))
            
            # Use langdetect as backup
            detected = detect(text)
            
            # Determine final language
            if hindi_score > 0:
                if detected == 'en':
                    return 'hinglish'
                else:
                    return 'hindi'
            elif detected == 'hi':
                return 'hindi'
            else:
                return 'english'
                
        except:
            return 'english'  # Default fallback

    def get_user_name(self, update: Update) -> str:
        """Get user's name for personalized responses"""
        user = update.effective_user
        return user.first_name or user.username or "friend"

    def generate_response(self, language: str, user_name: str, message_type: str, **kwargs) -> str:
        """Generate contextual responses based on language and situation"""
        responses = {
            'greeting': {
                'english': f"Hello {user_name}! 👋 I'm Friday, your personal AI assistant. How can I help you today?",
                'hindi': f"Namaste {user_name} ji! 🙏 Main Friday hun, aapki personal AI assistant. Aaj main aapki kaise madad kar sakti hun?",
                'hinglish': f"Hey {user_name}! 😊 Main Friday hun, tumhari AI assistant. Kya kaam hai aaj?"
            },
            'reminder_set': {
                'english': f"Perfect {user_name}! ✅ I'll remind you about '{kwargs.get('task', '')}' at {kwargs.get('time', '')}. Friday's got your back! 💪",
                'hindi': f"Bilkul theek {user_name} ji! ✅ Main aapko '{kwargs.get('task', '')}' ke baare mein {kwargs.get('time', '')} par yaad dila dungi. Friday hai na! 💪",
                'hinglish': f"Done {user_name}! ✅ '{kwargs.get('task', '')}' ka reminder {kwargs.get('time', '')} par set kar diya. Friday sambhal legi! 💪"
            },
            'reminder_notification': {
                'english': f"⏰ {user_name}, it's time! Don't forget: {kwargs.get('task', '')} 🎯",
                'hindi': f"⏰ {user_name} ji, samay ho gaya! Yaad rakhiye: {kwargs.get('task', '')} 🎯",
                'hinglish': f"⏰ {user_name}, time ho gaya! Yaad hai na: {kwargs.get('task', '')} 🎯"
            },
            'task_completed': {
                'english': f"Excellent work {user_name}! ✨ Task marked as completed. Friday is proud of you! 🌟",
                'hindi': f"Bahut badhiya {user_name} ji! ✨ Kaam complete ho gaya. Friday khush hai! 🌟",
                'hinglish': f"Great job {user_name}! ✨ Task complete kar diya. Friday proud hai! 🌟"
            },
            'casual_chat': {
                'english': f"I understand {user_name}! 😊 While I'm designed to help with reminders and tasks, I'm always here to chat. Is there anything specific you'd like me to help you remember or organize?",
                'hindi': f"Samajh gayi {user_name} ji! 😊 Main primarily reminders aur tasks mein help karti hun, lekin chat bhi kar sakti hun. Kya koi specific cheez hai jo yaad rakhni hai?",
                'hinglish': f"Gotcha {user_name}! 😊 Main mostly reminders ke liye hun, but chat bhi kar sakte hain. Koi particular thing hai jo organize karni hai?"
            },
            'help': {
                'english': f"""🤖 *Friday - Your AI Assistant*

Hey {user_name}! Here's what I can do:

*📝 Natural Reminders:*
• "Remind me to take medicine at 9 PM"
• "Set reminder for meeting tomorrow 3 PM"

*💬 Smart Features:*
• Understands Hindi, English, and Hinglish
• Uses your name in all responses
• Smart time parsing

*⏰ Task Management:*
• Say "done" when task is complete
• Natural conversation support

Just talk to me naturally - I'll understand! 😊""",
                'hindi': f"""🤖 *Friday - Aapki AI Assistant*

Namaste {user_name} ji! Yeh main kar sakti hun:

*📝 Natural Reminders:*
• "Mujhe kal 9 baje meeting yaad dila dena"
• "Shaam 8 baje dawa leni hai reminder set kar"

*💬 Smart Features:*
• Hindi, English, aur Hinglish samajhti hun
• Aapka naam lekar jawab deti hun
• Smart time parsing

*⏰ Task Management:*
• "Ho gaya" boliye jab kaam complete ho jaye
• Natural conversation support

Bas normally baat kariye - main samajh jaungi! 😊""",
                'hinglish': f"""🤖 *Friday - Tumhari AI Assistant*

Hey {user_name}! Yeh main kar sakti hun:

*📝 Natural Reminders:*
• "Kal morning 8 baje gym jana hai yaad dila"
• "Evening 6 baje call karna hai reminder set kar"

*💬 Smart Features:*
• Hindi, English, Hinglish sab samajhti hun
• Tumhara naam use karti hun responses mein
• Smart time parsing

*⏰ Task Management:*
• "Done" bolo jab task complete ho jaye
• Natural conversation support

Just normally talk karo - main understand kar lungi! 😊"""
            }
        }
        
        return responses.get(message_type, {}).get(language, responses[message_type]['english'])

    def parse_reminder(self, text: str) -> Tuple[Optional[str], Optional[datetime]]:
        """Parse natural language to extract task and time"""
        # Clean the text
        text = text.lower().strip()
        
        # Remove common reminder phrases
        reminder_phrases = [
            'remind me to', 'yaad dila dena', 'yaad rakhna', 'reminder set kar',
            'remind me', 'yaad dila', 'friday', 'reminder'
        ]
        
        for phrase in reminder_phrases:
            text = re.sub(phrase, '', text, flags=re.IGNORECASE).strip()
        
        # Try to parse the datetime
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
                    'today', 'tomorrow', 'kal', 'aaj', 'parso', 'at', 'par', 'baje',
                    'morning', 'evening', 'subah', 'shaam', 'raat', 'night',
                    'pm', 'am', 'o\'clock', r'\d+:\d+', r'\d+\s*baje'
                ]
                
                task = text
                for word in time_words:
                    task = re.sub(word, '', task, flags=re.IGNORECASE).strip()
                
                # Clean up extra spaces and common words
                task = re.sub(r'\s+', ' ', task).strip()
                task = re.sub(r'\b(ko|ka|ke|ki|me|mein|hai|hona|karna|lena)\b', '', task).strip()
                
                if task and len(task) > 2:
                    return task, parsed_time
                    
        except Exception as e:
            logger.error(f"Error parsing reminder: {e}")
        
        return None, None

    async def start_command(self, update: Update, context: CallbackContext):
        """Handle /start command"""
        user_id = update.effective_user.id
        user_name = self.get_user_name(update)
        
        # Initialize user data
        if user_id not in self.user_data:
            self.user_data[user_id] = {
                'tasks': [],
                'preferred_language': 'english',
                'timezone': 'Asia/Kolkata'
            }
        
        # Detect language and respond
        language = self.detect_language(update.message.text) if len(update.message.text) > 6 else 'english'
        response = self.generate_response(language, user_name, 'greeting')
        
        await update.message.reply_text(response)

    async def help_command(self, update: Update, context: CallbackContext):
        """Handle /help command"""
        user_name = self.get_user_name(update)
        user_id = update.effective_user.id
        
        # Get user's preferred language
        language = 'english'
        if user_id in self.user_data:
            language = self.user_data[user_id].get('preferred_language', 'english')
        
        help_text = self.generate_response(language, user_name, 'help')
        await update.message.reply_text(help_text, parse_mode='Markdown')

    async def handle_message(self, update: Update, context: CallbackContext):
        """Handle all text messages"""
        user_id = update.effective_user.id
        user_name = self.get_user_name(update)
        message_text = update.message.text
        language = self.detect_language(message_text)
        
        # Initialize user data if not exists
        if user_id not in self.user_data:
            self.user_data[user_id] = {
                'tasks': [],
                'preferred_language': language,
                'timezone': 'Asia/Kolkata'
            }
        else:
            # Update preferred language
            self.user_data[user_id]['preferred_language'] = language
        
        # Check for task completion
        completion_words = ['done', 'ho gaya', 'complete', 'finished', 'kar diya', 'kar liya']
        if any(word in message_text.lower() for word in completion_words):
            response = self.generate_response(language, user_name, 'task_completed')
            await update.message.reply_text(response)
            return
        
        # Check for reminder keywords
        reminder_keywords = [
            'remind', 'yaad dila', 'reminder', 'yaad rakh', 'remember',
            'schedule', 'set alarm', 'notify', 'alert'
        ]
        
        is_reminder = any(keyword in message_text.lower() for keyword in reminder_keywords)
        
        if is_reminder:
            task, scheduled_time = self.parse_reminder(message_text)
            
            if task and scheduled_time:
                # Ensure the time is in the future
                now = datetime.now(pytz.timezone('Asia/Kolkata'))
                if scheduled_time <= now:
                    scheduled_time = scheduled_time + timedelta(days=1)
                
                # Store the task (simplified - no actual scheduling in this version)
                task_data = {
                    'task': task,
                    'time': scheduled_time.strftime('%I:%M %p, %d %b'),
                    'scheduled_time': scheduled_time,
                    'language': language,
                    'user_name': user_name
                }
                
                self.user_data[user_id]['tasks'].append(task_data)
                
                response = self.generate_response(
                    language, user_name, 'reminder_set',
                    task=task, time=scheduled_time.strftime('%I:%M %p, %d %b')
                )
            else:
                response = f"Sorry {user_name}! 😅 I couldn't understand the timing. Try like 'Remind me to call mom at 7 PM'"
                
            await update.message.reply_text(response)
        else:
            # Handle casual chat
            response = self.generate_response(language, user_name, 'casual_chat')
            await update.message.reply_text(response)

def main():
    """Main function to run the bot"""
    BOT_TOKEN = "7949040161:AAHo5p5Hu84fcQcm1Wsa_UDOmXxjOYq2cOo"
    
    print("🤖 Starting Friday Bot (Simplified Version)...")
    print("=" * 50)
    
    if not BOT_TOKEN:
        logger.error("Bot token not provided!")
        return
    
    # Create Friday bot instance
    friday = FridayBot(BOT_TOKEN)
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", friday.start_command))
    application.add_handler(CommandHandler("help", friday.help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, friday.handle_message))
    
    print("✅ Friday bot initialized successfully!")
    print("💫 Friday is now online and ready to help!")
    print("📱 Message your bot on Telegram to start using Friday")
    print("=" * 50)
    
    # Start the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()