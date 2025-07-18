#!/usr/bin/env python3
"""
Friday - A Smart Multilingual Telegram Bot Assistant
A female AI assistant inspired by Iron Man's FRIDAY
"""

import logging
import asyncio
import re
import pytz
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
import json
import os

# Telegram Bot imports
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Natural Language Processing
import dateparser
from langdetect import detect
try:
    from langdetect.lang_detect_exception import LangDetectException as LangDetectError
except ImportError:
    # Fallback for different langdetect versions
    class LangDetectError(Exception):
        pass

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
        self.application = Application.builder().token(token).build()
        self.scheduler = AsyncIOScheduler(timezone=pytz.timezone('Asia/Kolkata'))
        self.user_data = {}  # Store user preferences and tasks
        self.active_reminders = {}  # Track active reminders
        
        # Language detection patterns
        self.hindi_patterns = [
            r'[\u0900-\u097F]',  # Devanagari script
            r'\b(hai|ka|ke|ki|ko|se|me|aur|ya|kya|kaise|kahan|kab|kyun|jo|wo|yeh|iska|uska)\b',
        ]
        
        # Setup handlers
        self._setup_handlers()
        
        # Start scheduler
        self.scheduler.start()
        
        # Setup daily greeting
        self._setup_daily_greeting()

    def _setup_handlers(self):
        """Setup all command and message handlers"""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("tasks", self.list_tasks))
        self.application.add_handler(CommandHandler("clear", self.clear_tasks))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

    def _setup_daily_greeting(self):
        """Setup daily morning greeting at 8 AM"""
        self.scheduler.add_job(
            self.send_daily_greeting,
            CronTrigger(hour=8, minute=0, timezone=pytz.timezone('Asia/Kolkata')),
            id='daily_greeting',
            replace_existing=True
        )

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
                
        except (LangDetectError, Exception):
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
            'snooze': {
                'english': f"No worries {user_name}! 😌 I'll remind you again in 15 minutes. Take your time!",
                'hindi': f"Koi baat nahi {user_name} ji! 😌 15 minute baad phir yaad dila dungi. Aaram se!",
                'hinglish': f"Chill {user_name}! 😌 15 min baad phir remind kar dungi. No tension!"
            },
            'daily_greeting': {
                'english': f"Good morning {user_name}! ☀️ Ready to conquer the day? Here are your pending tasks:",
                'hindi': f"Suprabhat {user_name} ji! ☀️ Aaj ka din jeetne ke liye tayyar hain? Yeh hain aapke pending kaam:",
                'hinglish': f"Morning {user_name}! ☀️ Aaj ka day rock karne ready ho? Yeh hai pending tasks:"
            },
            'no_tasks': {
                'english': f"All clear {user_name}! 🎉 No pending tasks. You're free to enjoy your day!",
                'hindi': f"Sab clear hai {user_name} ji! 🎉 Koi pending kaam nahi. Aaj ka din enjoy kariye!",
                'hinglish': f"All clear {user_name}! 🎉 Koi pending kaam nahi. Chill karo aaj!"
            },
            'casual_chat': {
                'english': f"I understand {user_name}! 😊 While I'm designed to help with reminders and tasks, I'm always here to chat. Is there anything specific you'd like me to help you remember or organize?",
                'hindi': f"Samajh gayi {user_name} ji! 😊 Main primarily reminders aur tasks mein help karti hun, lekin chat bhi kar sakti hun. Kya koi specific cheez hai jo yaad rakhni hai?",
                'hinglish': f"Gotcha {user_name}! 😊 Main mostly reminders ke liye hun, but chat bhi kar sakte hain. Koi particular thing hai jo organize karni hai?"
            },
            'error': {
                'english': f"Sorry {user_name}! 😅 I couldn't quite understand the timing. Could you try like 'Remind me to call mom at 7 PM' or 'kal 9 baje meeting hai'?",
                'hindi': f"Maaf kijiye {user_name} ji! 😅 Samay samajh nahi aaya. Kripya aise try kariye 'mujhe 7 baje mummy ko call karna yaad dila dena' ya '9 PM par medicine leni hai'?",
                'hinglish': f"Sorry {user_name}! 😅 Time samajh nahi aaya. Try karo like 'kal 8 baje gym jaana hai' ya 'evening 6 baje call karna hai'?"
            }
        }
        
        return responses.get(message_type, {}).get(language, responses[message_type]['english'])

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
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

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        user_name = self.get_user_name(update)
        
        help_text = f"""
🤖 *Friday - Your AI Assistant*

Hey {user_name}! Here's what I can do:

*📝 Natural Reminders:*
• "Remind me to take medicine at 9 PM"
• "Kal 8 baje tuition jaana hai yaad dila dena"
• "Roz subah paani peena yaad dila Friday"

*💬 Smart Features:*
• Understands Hindi, English, and Hinglish
• Replies in your preferred language
• Uses your name in all responses

*⏰ Reminder Management:*
• Say "done" or "ho gaya" when task is complete
• Say "snooze" or "baad me" to postpone by 15 minutes
• Daily morning summary at 8 AM

*🔧 Commands:*
/start - Get started with Friday
/help - Show this help message
/tasks - List all your pending tasks
/clear - Clear all pending tasks

Just talk to me naturally - I'll understand! 😊
        """
        
        await update.message.reply_text(help_text, parse_mode='Markdown')

    async def list_tasks(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List all pending tasks for the user"""
        user_id = update.effective_user.id
        user_name = self.get_user_name(update)
        
        if user_id not in self.user_data or not self.user_data[user_id]['tasks']:
            language = 'english'  # Default for commands
            response = self.generate_response(language, user_name, 'no_tasks')
            await update.message.reply_text(response)
            return
        
        tasks = self.user_data[user_id]['tasks']
        task_list = "\n".join([f"• {task['task']} - {task['time']}" for task in tasks])
        
        response = f"📋 *Your Pending Tasks, {user_name}:*\n\n{task_list}\n\n— Friday 💫"
        await update.message.reply_text(response, parse_mode='Markdown')

    async def clear_tasks(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Clear all pending tasks for the user"""
        user_id = update.effective_user.id
        user_name = self.get_user_name(update)
        
        if user_id in self.user_data:
            self.user_data[user_id]['tasks'] = []
        
        # Cancel all scheduled jobs for this user
        jobs_to_remove = [job.id for job in self.scheduler.get_jobs() 
                         if job.id.startswith(f"reminder_{user_id}_")]
        for job_id in jobs_to_remove:
            self.scheduler.remove_job(job_id)
        
        response = f"🗑️ All tasks cleared {user_name}! Fresh start. — Friday ✨"
        await update.message.reply_text(response)

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
            # Parse with multiple language support
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

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
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
            await self.handle_task_completion(update, context, language, user_name)
            return
        
        # Check for snooze
        snooze_words = ['snooze', 'baad me', 'later', 'abhi nahi', 'wait']
        if any(word in message_text.lower() for word in snooze_words):
            await self.handle_snooze(update, context, language, user_name)
            return
        
        # Check for reminder keywords
        reminder_keywords = [
            'remind', 'yaad dila', 'reminder', 'yaad rakh', 'remember',
            'schedule', 'set alarm', 'notify', 'alert'
        ]
        
        is_reminder = any(keyword in message_text.lower() for keyword in reminder_keywords)
        
        if is_reminder:
            await self.handle_reminder_request(update, context, language, user_name)
        else:
            await self.handle_casual_chat(update, context, language, user_name)

    async def handle_reminder_request(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                    language: str, user_name: str):
        """Handle reminder creation requests"""
        user_id = update.effective_user.id
        message_text = update.message.text
        
        task, scheduled_time = self.parse_reminder(message_text)
        
        if task and scheduled_time:
            # Ensure the time is in the future
            now = datetime.now(pytz.timezone('Asia/Kolkata'))
            if scheduled_time <= now:
                # If time is in the past, assume next day
                scheduled_time = scheduled_time + timedelta(days=1)
            
            # Store the task
            task_data = {
                'task': task,
                'time': scheduled_time.strftime('%I:%M %p, %d %b'),
                'scheduled_time': scheduled_time,
                'language': language,
                'user_name': user_name
            }
            
            self.user_data[user_id]['tasks'].append(task_data)
            
            # Schedule the reminder
            job_id = f"reminder_{user_id}_{len(self.user_data[user_id]['tasks'])}"
            self.scheduler.add_job(
                self.send_reminder,
                DateTrigger(run_date=scheduled_time),
                args=[user_id, task, language, user_name],
                id=job_id,
                replace_existing=True
            )
            
            response = self.generate_response(
                language, user_name, 'reminder_set',
                task=task, time=scheduled_time.strftime('%I:%M %p, %d %b')
            )
            
        else:
            response = self.generate_response(language, user_name, 'error')
        
        await update.message.reply_text(response)

    async def handle_task_completion(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                                   language: str, user_name: str):
        """Handle task completion"""
        user_id = update.effective_user.id
        
        # Mark most recent task as completed (simplified logic)
        if user_id in self.user_data and self.user_data[user_id]['tasks']:
            # Remove the most recent task
            completed_task = self.user_data[user_id]['tasks'].pop()
            
            # Try to cancel the scheduled job
            try:
                job_id = f"reminder_{user_id}_{len(self.user_data[user_id]['tasks']) + 1}"
                self.scheduler.remove_job(job_id)
            except Exception:
                pass  # Job might not exist or already executed
        
        response = self.generate_response(language, user_name, 'task_completed')
        await update.message.reply_text(response)

    async def handle_snooze(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                          language: str, user_name: str):
        """Handle snooze requests"""
        user_id = update.effective_user.id
        
        # Find the most recent task and reschedule it
        if user_id in self.user_data and self.user_data[user_id]['tasks']:
            task_data = self.user_data[user_id]['tasks'][-1]
            new_time = datetime.now(pytz.timezone('Asia/Kolkata')) + timedelta(minutes=15)
            
            # Update the task time
            task_data['scheduled_time'] = new_time
            task_data['time'] = new_time.strftime('%I:%M %p, %d %b')
            
            # Reschedule the job
            job_id = f"reminder_{user_id}_{len(self.user_data[user_id]['tasks'])}"
            self.scheduler.add_job(
                self.send_reminder,
                DateTrigger(run_date=new_time),
                args=[user_id, task_data['task'], language, user_name],
                id=job_id,
                replace_existing=True
            )
        
        response = self.generate_response(language, user_name, 'snooze')
        await update.message.reply_text(response)

    async def handle_casual_chat(self, update: Update, context: ContextTypes.DEFAULT_TYPE,
                               language: str, user_name: str):
        """Handle casual conversation"""
        response = self.generate_response(language, user_name, 'casual_chat')
        await update.message.reply_text(response)

    async def send_reminder(self, user_id: int, task: str, language: str, user_name: str):
        """Send a reminder to the user"""
        try:
            response = self.generate_response(language, user_name, 'reminder_notification', task=task)
            await self.application.bot.send_message(chat_id=user_id, text=response)
            
            # Remove the task from user's task list
            if user_id in self.user_data:
                self.user_data[user_id]['tasks'] = [
                    t for t in self.user_data[user_id]['tasks'] 
                    if t['task'] != task
                ]
                
        except Exception as e:
            logger.error(f"Error sending reminder to {user_id}: {e}")

    async def send_daily_greeting(self):
        """Send daily morning greeting to all users"""
        for user_id, data in self.user_data.items():
            try:
                if data['tasks']:
                    language = data.get('preferred_language', 'english')
                    # Get user name from stored data or use placeholder
                    user_name = "friend"  # Default name
                    
                    response = self.generate_response(language, user_name, 'daily_greeting')
                    
                    # Add task list
                    task_list = "\n".join([f"• {task['task']} - {task['time']}" 
                                         for task in data['tasks']])
                    response += f"\n\n{task_list}\n\n— Friday 💫"
                    
                    await self.application.bot.send_message(
                        chat_id=user_id, 
                        text=response,
                        parse_mode='Markdown'
                    )
                    
            except Exception as e:
                logger.error(f"Error sending daily greeting to {user_id}: {e}")

    def run(self):
        """Start the bot"""
        logger.info("Friday bot is starting...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

def main():
    """Main function to run the bot"""
    BOT_TOKEN = "7949040161:AAHo5p5Hu84fcQcm1Wsa_UDOmXxjOYq2cOo"
    
    if not BOT_TOKEN:
        logger.error("Bot token not provided!")
        return
    
    friday = FridayBot(BOT_TOKEN)
    friday.run()

if __name__ == "__main__":
    main()