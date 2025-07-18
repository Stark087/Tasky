# 🤖 Friday - Your Multilingual AI Assistant

Friday is a smart Telegram bot inspired by Iron Man's FRIDAY AI assistant. She understands natural Hindi, English, and Hinglish input and helps you manage reminders and tasks with a friendly, intelligent personality.

## ✨ Features

### 🗣️ Multilingual Support
- **Hindi**: "Kal 8 baje tuition jaana hai yaad dila dena"
- **English**: "Remind me to take medicine at 9 PM"
- **Hinglish**: "Friday yaar, kal morning 7 baje gym jana hai reminder set kar"

### 🧠 Smart Natural Language Processing
- Understands casual, natural language
- Automatically detects your preferred language
- Replies in the same language you used
- Uses your name in all responses for personalization

### ⏰ Intelligent Reminders
- Natural time parsing: "tomorrow 8 AM", "kal shaam 6 baje", "next Monday"
- Task completion tracking: Say "done" or "ho gaya" when finished
- Snooze functionality: Say "snooze" or "baad me" to postpone by 15 minutes
- Daily morning summary at 8 AM with pending tasks

### 👩‍💼 Friday's Personality
- Calm, intelligent, and friendly
- Uses natural emojis
- Maintains consistent female AI assistant persona
- Not robotic - speaks like a helpful friend

## 🚀 Quick Start

### Installation

1. **Clone or download the bot files**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the bot:**
   ```bash
   python friday_bot.py
   ```

### Bot Commands

- `/start` - Initialize Friday and get started
- `/help` - See all available features
- `/tasks` - List your pending reminders
- `/clear` - Clear all pending tasks

## 💬 Usage Examples

### Setting Reminders

**English:**
- "Remind me to call mom at 7 PM"
- "Set reminder for doctor appointment tomorrow 3 PM"
- "Friday, remind me to take vitamins every morning"

**Hindi:**
- "Mujhe kal 9 baje meeting yaad dila dena"
- "Subah 6 baje exercise karna hai yaad dila Friday"
- "Shaam ko 8 baje dinner banana hai reminder set kar"

**Hinglish:**
- "Kal morning 7 baje gym jana hai yaad dila"
- "Friday, aaj evening 5 baje client call hai reminder de"
- "Weekend pe shopping karna hai yaad rakhna"

### Task Management

**Completing Tasks:**
- "Done" / "Ho gaya" / "Complete" / "Kar diya"

**Snoozing Tasks:**
- "Snooze" / "Baad me" / "Later" / "Abhi nahi"

### Daily Greetings

Friday automatically sends you a good morning message at 8 AM with your pending tasks, using your preferred language.

## 🔧 Technical Features

### Natural Language Processing
- Uses `dateparser` with Hindi and English language support
- Implements custom language detection combining script analysis and `langdetect`
- Smart task extraction from natural language input

### Scheduling System
- Built with `APScheduler` for reliable reminder delivery
- Timezone-aware scheduling (Asia/Kolkata)
- Automatic cleanup of completed tasks

### User Experience
- Personalized responses using user's first name or username
- Language preference learning and adaptation
- Consistent personality across all interactions

## 🛡️ Privacy & Security

- User data is stored locally in memory (not persistent across restarts)
- Only essential user information is collected (name, language preference, tasks)
- No data is shared with third parties

## 🎯 Example Conversations

### Setting a Medicine Reminder
**User:** "Friday, remind me to take blood pressure medicine at 8 PM daily"
**Friday:** "Perfect Aditi! ✅ I'll remind you about 'take blood pressure medicine' at 08:00 PM, 15 Dec. Friday's got your back! 💪"

### Hinglish Interaction
**User:** "Kal subah 7 baje yoga class jana hai yaad dila"
**Friday:** "Done Rahul! ✅ 'yoga class jana' ka reminder 07:00 AM, 16 Dec par set kar diya. Friday sambhal legi! 💪"

### Task Completion
**User:** "Done"
**Friday:** "Excellent work Priya! ✨ Task marked as completed. Friday is proud of you! 🌟"

## 🔮 Advanced Features

- **Smart Time Detection**: Understands relative times like "kal", "tomorrow", "next week"
- **Context Awareness**: Remembers your language preference and adapts accordingly
- **Error Handling**: Provides helpful suggestions when time parsing fails
- **Emoji Integration**: Uses contextually appropriate emojis naturally

## 🤝 Contributing

Feel free to enhance Friday with additional features:
- More language support
- Advanced NLP capabilities
- Integration with calendar apps
- Voice message support

## 📄 License

This project is open source. Feel free to modify and distribute.

---

**Friday Bot** - Making your daily life organized, one reminder at a time! 🌟