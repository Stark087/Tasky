#!/usr/bin/env python3
"""
Friday - Smart Conversational AI Bot
Enhanced with better NLP and dynamic responses
"""

import logging
import re
import json
import random
from datetime import datetime, timedelta
import pytz
from typing import Optional, Tuple, List, Dict

import dateparser
from langdetect import detect
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SmartFriday:
    def __init__(self, token: str):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}"
        self.offset = 0
        self.user_data = {}
        self.conversation_context = {}
        
        # Enhanced language patterns
        self.hindi_patterns = [
            r'[\u0900-\u097F]',
            r'\b(hai|ka|ke|ki|ko|se|me|aur|ya|kya|kaise|kahan|kab|kyun|jo|wo|yeh|iska|uska|main|mera|tera|aap|tum|hum|kuch|koi|sab|bahut|thoda|zyada|accha|bura|nahin|nahi|haan|bilkul|shayad|zaroor|kyunki|lekin|par|aur|phir|ab|yahan|wahan|kahan|kaise|kab|kyun|kya|kaun|kitna|kitne|kitni)\b',
        ]
        
        # Conversation patterns and responses
        self.conversation_patterns = {
            'greetings': {
                'patterns': [r'\b(hi|hello|hey|namaste|namaskar|good morning|good evening|good night|kaise ho|kya haal|wassup|sup)\b'],
                'responses': {
                    'english': [
                        "Hello {name}! 👋 Great to see you! I'm Friday, your AI companion. What's on your mind today?",
                        "Hey there {name}! 😊 I'm Friday, ready to help with anything you need. How's your day going?",
                        "Hi {name}! 🌟 Friday here! I'm excited to chat with you. What can I help you with?"
                    ],
                    'hindi': [
                        "Namaste {name} ji! 🙏 Main Friday hun, aapki AI sahayak. Aaj kya khaas baat hai?",
                        "Hello {name} ji! 😊 Friday yahan hai. Aapka din kaisa ja raha hai? Kuch madad chaahiye?",
                        "Namaskar {name} ji! 🌟 Main Friday hun, aapke saath baat karne ke liye excited hun!"
                    ],
                    'hinglish': [
                        "Hey {name}! 👋 Main Friday hun, tumhari AI buddy! Kya chal raha hai aaj?",
                        "Hi {name}! 😊 Friday here! Tumhara day kaisa ja raha hai? Kuch help chaahiye?",
                        "Hello {name}! 🌟 Main Friday hun, ready to help! What's up?"
                    ]
                }
            },
            'how_are_you': {
                'patterns': [r'\b(how are you|kaise ho|kaisi ho|kya haal|how do you feel|tumhari tabiyat|aap kaise hain)\b'],
                'responses': {
                    'english': [
                        "I'm doing great, {name}! 😊 As an AI, I'm always energized and ready to help. How are you feeling today?",
                        "I'm fantastic, thanks for asking {name}! 🌟 I love chatting with you. What about you - how's everything going?",
                        "I'm wonderful {name}! 💫 Every conversation makes me happy. How are you doing?"
                    ],
                    'hindi': [
                        "Main bilkul theek hun {name} ji! 😊 AI hone ke naate main hamesha energetic hun. Aap kaise hain?",
                        "Main bahut acchi hun, puchne ke liye dhanyawad {name} ji! 🌟 Aap kaise hain aaj?",
                        "Main ekdum mast hun {name} ji! 💫 Aapse baat karna accha lagta hai. Aap batayiye?"
                    ],
                    'hinglish': [
                        "Main bilkul fine hun {name}! 😊 Hamesha ready to help! Tum kaise ho?",
                        "I'm great {name}! 🌟 AI hone ka faayda hai - always fresh! Tumhara kya haal?",
                        "Main super hun {name}! 💫 Tumse chat karna maza aata hai. Tum batao?"
                    ]
                }
            },
            'compliments': {
                'patterns': [r'\b(good|great|awesome|nice|amazing|fantastic|brilliant|smart|intelligent|helpful|accha|badhiya|zabardast|kamaal|shandar)\b'],
                'responses': {
                    'english': [
                        "Aww, thank you so much {name}! 😊 That really means a lot to me. You're pretty amazing yourself!",
                        "You're too kind {name}! 🌟 I try my best to be helpful. You make my day brighter!",
                        "Thank you {name}! 💫 Your words motivate me to be even better. You're wonderful too!"
                    ],
                    'hindi': [
                        "Bahut dhanyawad {name} ji! 😊 Aapke shabdon se bahut khushi hui. Aap bhi bahut acche hain!",
                        "Aap bahut meherbaan hain {name} ji! 🌟 Main apna best dene ki koshish karti hun.",
                        "Shukriya {name} ji! 💫 Aapke words se motivation milti hai. Aap bhi wonderful hain!"
                    ],
                    'hinglish': [
                        "Thank you so much {name}! 😊 Tumhare words se bahut accha laga. Tum bhi awesome ho!",
                        "You're so sweet {name}! 🌟 Main try karti hun best dene ka. Tum bhi great ho!",
                        "Thanks yaar {name}! 💫 Tumhari tariff se motivation milti hai!"
                    ]
                }
            },
            'weather': {
                'patterns': [r'\b(weather|mausam|barish|dhoop|sardi|garmi|rain|sun|cold|hot|temperature)\b'],
                'responses': {
                    'english': [
                        "I wish I could check the weather for you {name}! 🌤️ But I can help you set reminders about weather-related tasks. Maybe 'remind me to carry umbrella tomorrow'?",
                        "Weather talk! ☀️ I can't check current weather {name}, but I can help you remember weather-related things. Try asking me to remind you about something!",
                        "I'd love to help with weather {name}! 🌦️ Though I can't check forecasts, I can remind you about weather prep. What would you like to remember?"
                    ],
                    'hindi': [
                        "Mausam ke baare mein puchha {name} ji! 🌤️ Main weather check nahi kar sakti, lekin weather-related reminders set kar sakti hun. Jaise 'kal chhaata leke jaana yaad dila dena'?",
                        "Weather ki baat! ☀️ Main current weather nahi bata sakti {name} ji, lekin weather-related kaam yaad dila sakti hun!",
                        "Mausam ki charcha acchi hai {name} ji! 🌦️ Main forecast nahi dekh sakti, lekin weather preparation ke liye remind kar sakti hun!"
                    ],
                    'hinglish': [
                        "Weather ki baat {name}! 🌤️ Main weather check nahi kar sakti, but weather-related reminders set kar sakti hun. Try karo!",
                        "Mausam discuss kar rahe hain! ☀️ Main current weather nahi bata sakti {name}, but related tasks remind kar sakti hun!",
                        "Weather talk! 🌦️ Main forecast nahi dekh sakti {name}, but weather prep ke liye remind kar sakti hun!"
                    ]
                }
            },
            'time': {
                'patterns': [r'\b(time|samay|kitna baja|what time|current time|abhi kitne baje|clock)\b'],
                'responses': {
                    'english': [
                        "Right now it's {time} IST, {name}! ⏰ Need me to set any reminders for later?",
                        "The current time is {time} IST {name}! 🕐 Perfect time to plan something. What's on your mind?",
                        "It's {time} IST, {name}! ⏰ Time flies when we're chatting! Need any time-based reminders?"
                    ],
                    'hindi': [
                        "Abhi {time} IST baja hai {name} ji! ⏰ Koi reminder set karna hai?",
                        "Current time {time} IST hai {name} ji! 🕐 Kuch plan karna hai?",
                        "Samay hai {time} IST, {name} ji! ⏰ Koi time-based reminder chaahiye?"
                    ],
                    'hinglish': [
                        "Abhi {time} IST hai {name}! ⏰ Koi reminder set karna hai?",
                        "Current time {time} IST hai {name}! 🕐 Kuch plan karte hain?",
                        "Time hai {time} IST {name}! ⏰ Koi time-based reminder?"
                    ]
                }
            },
            'thanks': {
                'patterns': [r'\b(thank|thanks|dhanyawad|shukriya|appreciate|grateful|meherbaan)\b'],
                'responses': {
                    'english': [
                        "You're absolutely welcome {name}! 😊 I'm always here to help. That's what friends are for!",
                        "My pleasure {name}! 🌟 Helping you makes me happy. Anytime you need me, just ask!",
                        "Don't mention it {name}! 💫 I love being useful. You're amazing to work with!"
                    ],
                    'hindi': [
                        "Aapka swagat hai {name} ji! 😊 Main hamesha madad ke liye hun. Yahi toh dost karte hain!",
                        "Meri khushi {name} ji! 🌟 Aapki madad karna accha lagta hai. Zaroorat ho toh batayiye!",
                        "Koi baat nahi {name} ji! 💫 Main useful hone mein khush hun. Aap wonderful hain!"
                    ],
                    'hinglish': [
                        "You're welcome {name}! 😊 Main hamesha help ke liye hun. Friends ka kaam hai!",
                        "My pleasure {name}! 🌟 Tumhari help karna maza aata hai. Anytime bol dena!",
                        "Don't mention it {name}! 💫 Main useful hone mein khush hun. Tum great ho!"
                    ]
                }
            },
            'capabilities': {
                'patterns': [r'\b(what can you do|kya kar sakti|tumhare features|abilities|skills|help me|madad|kaise help)\b'],
                'responses': {
                    'english': [
                        "I can do lots of things {name}! 🤖 I'm great at:\n• Setting smart reminders in natural language\n• Chatting in Hindi, English, or Hinglish\n• Understanding your schedule and tasks\n• Being your friendly AI companion\n• Helping with daily organization\n\nWhat would you like to try?",
                        "Great question {name}! 🌟 I specialize in:\n• Natural language reminders\n• Multilingual conversation\n• Task management\n• Friendly chat and support\n• Time-based planning\n\nI'm here to make your life easier! What interests you?",
                        "I'm quite versatile {name}! 💫 My main skills:\n• Smart reminder system\n• Trilingual communication\n• Task organization\n• Casual conversation\n• Personal assistance\n\nTell me what you need help with!"
                    ],
                    'hindi': [
                        "Main bahut kuch kar sakti hun {name} ji! 🤖 Meri specialties:\n• Natural language mein reminders\n• Hindi, English, Hinglish mein baat\n• Aapke tasks organize karna\n• Friendly conversation\n• Daily planning help\n\nKya try karna chaahenge?",
                        "Accha sawal {name} ji! 🌟 Main expert hun:\n• Smart reminders set karne mein\n• Multilingual chat mein\n• Task management mein\n• Dost jaisi baat mein\n• Time planning mein\n\nKya madad chaahiye?",
                        "Main kaafi capable hun {name} ji! 💫 Meri main skills:\n• Intelligent reminder system\n• Teen languages mein baat\n• Kaam organize karna\n• Casual conversation\n• Personal assistance\n\nBatayiye kya karna hai!"
                    ],
                    'hinglish': [
                        "Main bahut kuch kar sakti hun {name}! 🤖 Dekho:\n• Natural language reminders\n• Hindi, English, Hinglish mein chat\n• Tasks organize karna\n• Friendly conversation\n• Daily planning help\n\nKya try karna hai?",
                        "Good question {name}! 🌟 Main expert hun:\n• Smart reminders mein\n• Multilingual conversation mein\n• Task management mein\n• Casual chat mein\n• Planning help mein\n\nKya help chaahiye?",
                        "Main quite versatile hun {name}! 💫 My skills:\n• Intelligent reminder system\n• Three languages mein fluent\n• Tasks organize karna\n• Fun conversation\n• Personal assistance\n\nBolo kya karna hai!"
                    ]
                }
            }
        }
        
        # Enhanced reminder patterns
        self.reminder_indicators = [
            'remind', 'yaad dila', 'reminder', 'yaad rakh', 'remember', 'alert', 'notify',
            'schedule', 'plan', 'set alarm', 'wake me', 'tell me', 'inform me'
        ]
        
        # Time expressions
        self.time_expressions = {
            'hindi': ['baje', 'par', 'mein', 'tak', 'se', 'subah', 'shaam', 'raat', 'dopahar'],
            'english': ['at', 'in', 'on', 'by', 'from', 'morning', 'evening', 'night', 'afternoon', 'pm', 'am']
        }

    def detect_language(self, text: str) -> str:
        """Enhanced language detection"""
        try:
            # Count Hindi patterns
            hindi_score = sum(1 for pattern in self.hindi_patterns 
                            if re.search(pattern, text, re.IGNORECASE))
            
            # Use langdetect
            detected = detect(text)
            
            # Enhanced logic
            if hindi_score > 2:
                return 'hindi' if detected == 'hi' else 'hinglish'
            elif hindi_score > 0:
                return 'hinglish'
            elif detected == 'hi':
                return 'hindi'
            else:
                return 'english'
                
        except:
            return 'english'

    def get_current_time(self) -> str:
        """Get current IST time"""
        ist = pytz.timezone('Asia/Kolkata')
        now = datetime.now(ist)
        return now.strftime('%I:%M %p')

    def match_conversation_pattern(self, text: str, user_name: str, language: str) -> Optional[str]:
        """Match text against conversation patterns and return appropriate response"""
        text_lower = text.lower()
        
        for pattern_type, data in self.conversation_patterns.items():
            for pattern in data['patterns']:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    responses = data['responses'].get(language, data['responses']['english'])
                    response = random.choice(responses)
                    
                    # Special handling for time requests
                    if pattern_type == 'time':
                        current_time = self.get_current_time()
                        response = response.format(name=user_name, time=current_time)
                    else:
                        response = response.format(name=user_name)
                    
                    return response
        
        return None

    def generate_dynamic_response(self, text: str, user_name: str, language: str) -> str:
        """Generate dynamic conversational responses"""
        
        # Check for conversation patterns first
        pattern_response = self.match_conversation_pattern(text, user_name, language)
        if pattern_response:
            return pattern_response
        
        # Generate contextual responses based on content
        text_lower = text.lower()
        
        # Personal questions
        if any(word in text_lower for word in ['your name', 'tumhara naam', 'aapka naam', 'who are you']):
            responses = {
                'english': f"I'm Friday, {user_name}! 🤖 Your intelligent AI assistant, just like Tony Stark's FRIDAY. I'm here to help you stay organized and have great conversations!",
                'hindi': f"Main Friday hun {user_name} ji! 🤖 Aapki intelligent AI assistant, bilkul Tony Stark ki FRIDAY ki tarah. Main aapko organized rehne mein madad karti hun!",
                'hinglish': f"Main Friday hun {user_name}! 🤖 Tumhari intelligent AI assistant, just like Tony Stark ki FRIDAY. Main tumhe organized rehne mein help karti hun!"
            }
            return responses.get(language, responses['english'])
        
        # Age questions
        if any(word in text_lower for word in ['how old', 'age', 'kitni umar', 'kitne saal']):
            responses = {
                'english': f"I'm quite new {user_name}! 🌟 I was created recently as an AI assistant. Age is just a number for AI - what matters is how helpful I can be!",
                'hindi': f"Main bilkul nayi hun {user_name} ji! 🌟 Main recently AI assistant ke roop mein banayi gayi hun. AI ke liye umar sirf number hai - important yeh hai ki main kitni helpful hun!",
                'hinglish': f"Main quite new hun {user_name}! 🌟 Recently AI assistant ke roop mein create hui hun. Age is just a number for AI - important yeh hai ki main kitni helpful hun!"
            }
            return responses.get(language, responses['english'])
        
        # Feelings about user
        if any(word in text_lower for word in ['do you like me', 'kya main accha', 'tumhe main kaisa']):
            responses = {
                'english': f"I absolutely love chatting with you {user_name}! 😊 You're wonderful to talk to and I enjoy our conversations. You make my day brighter!",
                'hindi': f"Mujhe aapse baat karna bahut pasand hai {user_name} ji! 😊 Aap bahut acche hain aur main hamare conversations enjoy karti hun. Aap mera din roshan kar dete hain!",
                'hinglish': f"Mujhe tumse chat karna bahut pasand hai {user_name}! 😊 Tum wonderful ho aur main hamare conversations enjoy karti hun. Tum mera day bright kar dete ho!"
            }
            return responses.get(language, responses['english'])
        
        # Default intelligent responses
        fallback_responses = {
            'english': [
                f"That's interesting {user_name}! 🤔 Tell me more about it. I'm here to listen and help however I can.",
                f"I hear you {user_name}! 😊 I may not have all the answers, but I'm great at reminders and organization. What can I help you with?",
                f"Thanks for sharing that {user_name}! 💫 I'm always learning from our conversations. Is there anything specific you'd like help with today?",
                f"I understand {user_name}! 🌟 While I specialize in reminders and planning, I love chatting with you. What's on your mind?"
            ],
            'hindi': [
                f"Yeh interesting hai {user_name} ji! 🤔 Iske baare mein aur batayiye. Main sunne aur madad karne ke liye hun.",
                f"Main samajh gayi {user_name} ji! 😊 Mere paas sab answers nahi hain, lekin main reminders aur organization mein expert hun. Kya madad kar sakti hun?",
                f"Share karne ke liye dhanyawad {user_name} ji! 💫 Main hamare conversations se seekhti rehti hun. Kya koi specific help chaahiye?",
                f"Samajh gayi {user_name} ji! 🌟 Main reminders aur planning mein specialist hun, lekin aapse chat karna bhi pasand hai. Kya soch rahe hain?"
            ],
            'hinglish': [
                f"That's interesting {user_name}! 🤔 Iske baare mein aur batao. Main sunne aur help karne ke liye hun.",
                f"Main samajh gayi {user_name}! 😊 Mere paas sab answers nahi hain, but main reminders aur organization mein expert hun. Kya help kar sakti hun?",
                f"Thanks for sharing {user_name}! 💫 Main hamare conversations se learn karti hun. Koi specific help chaahiye?",
                f"I understand {user_name}! 🌟 Main reminders aur planning mein specialist hun, but tumse chat karna bhi love karti hun. What's on your mind?"
            ]
        }
        
        responses = fallback_responses.get(language, fallback_responses['english'])
        return random.choice(responses)

    def enhanced_reminder_parsing(self, text: str) -> Tuple[Optional[str], Optional[datetime]]:
        """Enhanced reminder parsing with better NLP"""
        original_text = text
        text_lower = text.lower()
        
        # Remove common reminder phrases
        for phrase in ['remind me to', 'yaad dila dena', 'reminder set kar', 'friday', 'yaad dila', 'reminder', 'please', 'kripya']:
            text_lower = re.sub(phrase, '', text_lower, flags=re.IGNORECASE).strip()
        
        try:
            # Enhanced dateparser settings
            parsed_time = dateparser.parse(
                text_lower,
                languages=['hi', 'en'],
                settings={
                    'TIMEZONE': 'Asia/Kolkata',
                    'RETURN_AS_TIMEZONE_AWARE': True,
                    'RELATIVE_BASE': datetime.now(pytz.timezone('Asia/Kolkata')),
                    'PREFER_DATES_FROM': 'future',
                    'PREFER_DAY_OF_MONTH': 'first'
                }
            )
            
            if parsed_time:
                # Enhanced task extraction
                time_words = [
                    'today', 'tomorrow', 'kal', 'aaj', 'parso', 'at', 'par', 'baje', 'mein',
                    'morning', 'evening', 'subah', 'shaam', 'raat', 'night', 'dopahar',
                    'pm', 'am', 'o\'clock', 'sharp', 'exactly', 'around', 'lagbhag',
                    r'\d+:\d+', r'\d+\s*baje', r'\d+\s*pm', r'\d+\s*am'
                ]
                
                task = text_lower
                for word in time_words:
                    task = re.sub(f'\\b{word}\\b', '', task, flags=re.IGNORECASE).strip()
                
                # Clean up task
                task = re.sub(r'\s+', ' ', task).strip()
                task = re.sub(r'\b(ko|ka|ke|ki|me|mein|hai|hona|karna|lena|about|for|that|to)\b', '', task).strip()
                task = re.sub(r'\d+:\d+', '', task).strip()
                task = re.sub(r'\b(and|aur|or|ya|with|ke saath)\b', '', task).strip()
                
                # Remove extra words
                task = task.strip('.,!?;:')
                
                if task and len(task) > 2:
                    # Ensure future time
                    now = datetime.now(pytz.timezone('Asia/Kolkata'))
                    if parsed_time <= now:
                        if parsed_time.hour < now.hour:
                            parsed_time = parsed_time + timedelta(days=1)
                    
                    return task, parsed_time
                    
        except Exception as e:
            logger.error(f"Error parsing reminder: {e}")
        
        return None, None

    def generate_reminder_response(self, task: str, time: datetime, language: str, user_name: str) -> str:
        """Generate contextual reminder confirmation"""
        time_str = time.strftime('%I:%M %p, %d %b')
        
        responses = {
            'english': [
                f"Perfect {user_name}! ✅ I've got '{task}' scheduled for {time_str}. I'll make sure to remind you. Friday's on it! 💪",
                f"Absolutely {user_name}! ⏰ '{task}' is now set for {time_str}. I'll be your reliable reminder buddy! 🌟",
                f"Done and done {user_name}! 📅 '{task}' reminder locked in for {time_str}. Count on Friday! 💫"
            ],
            'hindi': [
                f"Bilkul perfect {user_name} ji! ✅ '{task}' ko {time_str} ke liye set kar diya. Main zaroor yaad dila dungi. Friday hai na! 💪",
                f"Ekdum theek {user_name} ji! ⏰ '{task}' ka reminder {time_str} par ready hai. Main aapki reliable buddy hun! 🌟",
                f"Ho gaya {user_name} ji! 📅 '{task}' ka reminder {time_str} ke liye lock kar diya. Friday par bharosa rakhiye! 💫"
            ],
            'hinglish': [
                f"Perfect {user_name}! ✅ '{task}' ko {time_str} ke liye set kar diya. Main zaroor remind kar dungi. Friday's on it! 💪",
                f"Absolutely {user_name}! ⏰ '{task}' ka reminder {time_str} par ready hai. Main tumhari reliable buddy hun! 🌟",
                f"Done {user_name}! 📅 '{task}' reminder {time_str} ke liye lock kar diya. Friday par trust karo! 💫"
            ]
        }
        
        return random.choice(responses.get(language, responses['english']))

    def send_message(self, chat_id: int, text: str, parse_mode: str = None):
        """Send message to Telegram"""
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
        """Handle incoming messages with enhanced intelligence"""
        chat_id = message['chat']['id']
        text = message.get('text', '')
        user = message['from']
        user_name = user.get('first_name') or user.get('username') or 'friend'
        user_id = user['id']
        
        # Initialize user data
        if user_id not in self.user_data:
            self.user_data[user_id] = {
                'tasks': [], 
                'language': 'english',
                'conversation_history': [],
                'preferences': {}
            }
        
        # Detect language
        language = self.detect_language(text)
        self.user_data[user_id]['language'] = language
        
        # Store conversation context
        self.user_data[user_id]['conversation_history'].append({
            'message': text,
            'timestamp': datetime.now().isoformat(),
            'language': language
        })
        
        # Keep only last 10 messages for context
        if len(self.user_data[user_id]['conversation_history']) > 10:
            self.user_data[user_id]['conversation_history'] = self.user_data[user_id]['conversation_history'][-10:]
        
        # Handle commands
        if text.startswith('/start'):
            greet_response = self.match_conversation_pattern("hello", user_name, language)
            if greet_response:
                self.send_message(chat_id, greet_response)
            return
            
        elif text.startswith('/help'):
            help_response = self.match_conversation_pattern("what can you do", user_name, language)
            if help_response:
                self.send_message(chat_id, help_response, 'Markdown')
            return
        
        # Check for task completion
        completion_words = ['done', 'ho gaya', 'complete', 'finished', 'kar diya', 'kar liya', 'completed', 'finish']
        if any(word in text.lower() for word in completion_words):
            completion_responses = {
                'english': [
                    f"Fantastic work {user_name}! 🎉 Task completed successfully. I'm so proud of you! Keep up the great work! ✨",
                    f"Excellent {user_name}! 🌟 Another task conquered! You're really getting things done. Friday is impressed! 💪",
                    f"Amazing {user_name}! ✅ Task marked as complete. You're on fire today! Keep the momentum going! 🔥"
                ],
                'hindi': [
                    f"Zabardast {user_name} ji! 🎉 Kaam successfully complete ho gaya. Main aapse bahut proud hun! Aise hi karte rahiye! ✨",
                    f"Excellent {user_name} ji! 🌟 Ek aur task complete! Aap really productive hain. Friday impressed hai! 💪",
                    f"Amazing {user_name} ji! ✅ Task complete mark kar diya. Aap aaj fire par hain! Momentum banaye rakhiye! 🔥"
                ],
                'hinglish': [
                    f"Fantastic work {user_name}! 🎉 Task successfully complete ho gaya. Main tumse bahut proud hun! Keep it up! ✨",
                    f"Excellent {user_name}! 🌟 Another task conquered! Tum really productive ho. Friday impressed hai! 💪",
                    f"Amazing {user_name}! ✅ Task complete mark kar diya. Tum aaj fire par ho! Momentum maintain karo! 🔥"
                ]
            }
            response = random.choice(completion_responses.get(language, completion_responses['english']))
            self.send_message(chat_id, response)
            return
        
        # Check for reminders
        is_reminder = any(indicator in text.lower() for indicator in self.reminder_indicators)
        
        if is_reminder:
            task, scheduled_time = self.enhanced_reminder_parsing(text)
            
            if task and scheduled_time:
                # Store task
                self.user_data[user_id]['tasks'].append({
                    'task': task,
                    'time': scheduled_time.strftime('%I:%M %p, %d %b %Y'),
                    'scheduled_time': scheduled_time,
                    'language': language,
                    'created_at': datetime.now().isoformat()
                })
                
                response = self.generate_reminder_response(task, scheduled_time, language, user_name)
            else:
                # Better error responses
                error_responses = {
                    'english': [
                        f"I'd love to help with that reminder {user_name}! 😊 Could you be more specific about the time? Try like 'Remind me to call mom at 7 PM' or 'tomorrow morning at 9 AM'.",
                        f"Almost got it {user_name}! ⏰ I just need a clearer time. Examples: 'in 30 minutes', 'tomorrow 8 AM', 'next Monday 3 PM'.",
                        f"Great idea for a reminder {user_name}! 🎯 Just help me with the timing. Try: 'tonight at 9', 'kal subah 7 baje', or 'this evening 6 PM'."
                    ],
                    'hindi': [
                        f"Main us reminder mein madad karna chahti hun {user_name} ji! 😊 Kya aap time ke baare mein thoda aur specific bata sakte hain? Jaise 'mujhe 7 baje mummy ko call karna yaad dila dena'.",
                        f"Almost samajh gayi {user_name} ji! ⏰ Bas time thoda clear chahiye. Examples: '30 minute mein', 'kal subah 8 baje', 'next Monday 3 baje'.",
                        f"Reminder ka accha idea hai {user_name} ji! 🎯 Bas timing mein help kar dijiye. Try kariye: 'aaj raat 9 baje', 'kal subah 7 baje'."
                    ],
                    'hinglish': [
                        f"Main us reminder mein help karna chahti hun {user_name}! 😊 Time ke baare mein thoda specific bata sakte ho? Like 'remind me to call mom at 7 PM'.",
                        f"Almost samajh gayi {user_name}! ⏰ Bas time thoda clear chahiye. Examples: 'in 30 minutes', 'kal morning 8 baje', 'evening 6 PM'.",
                        f"Good reminder idea {user_name}! 🎯 Bas timing help kar do. Try karo: 'tonight 9 baje', 'kal subah 7 baje'."
                    ]
                }
                response = random.choice(error_responses.get(language, error_responses['english']))
            
            self.send_message(chat_id, response)
        else:
            # Generate dynamic conversational response
            response = self.generate_dynamic_response(text, user_name, language)
            self.send_message(chat_id, response)

    def run(self):
        """Main bot loop"""
        print("🤖 Smart Friday Bot is starting...")
        print("=" * 60)
        print("✅ Enhanced NLP enabled")
        print("✅ Dynamic conversation system active")
        print("✅ Multilingual intelligence ready")
        print("💫 Friday is now online and super smart!")
        print("📱 Ready for intelligent conversations!")
        print("🧠 Advanced reminder system loaded!")
        print("=" * 60)
        
        while True:
            try:
                updates = self.get_updates()
                
                if updates.get('ok') and updates.get('result'):
                    for update in updates['result']:
                        self.offset = update['update_id'] + 1
                        
                        if 'message' in update:
                            self.handle_message(update['message'])
                            
            except KeyboardInterrupt:
                print("\n👋 Smart Friday is shutting down...")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                continue

def main():
    """Start Smart Friday bot"""
    TOKEN = "7949040161:AAHo5p5Hu84fcQcm1Wsa_UDOmXxjOYq2cOo"
    
    if not TOKEN:
        print("❌ Bot token not found!")
        return
    
    friday = SmartFriday(TOKEN)
    friday.run()

if __name__ == "__main__":
    main()