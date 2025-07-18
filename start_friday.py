#!/usr/bin/env python3
"""
Startup script for Friday bot with validation
"""
import sys
import os

def validate_dependencies():
    """Validate all required dependencies are installed"""
    try:
        import telegram
        import dateparser
        import langdetect
        import apscheduler
        import pytz
        import regex
        print("✅ All dependencies validated successfully!")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False

def main():
    print("🤖 Starting Friday Bot...")
    print("=" * 50)
    
    # Validate dependencies
    if not validate_dependencies():
        print("❌ Please install missing dependencies with: pip install -r requirements.txt")
        sys.exit(1)
    
    # Import and start the bot
    try:
        from friday_bot import FridayBot
        
        # Bot token
        BOT_TOKEN = "7949040161:AAHo5p5Hu84fcQcm1Wsa_UDOmXxjOYq2cOo"
        
        if not BOT_TOKEN:
            print("❌ Bot token not found!")
            sys.exit(1)
        
        print("✅ Dependencies validated")
        print("✅ Bot token configured")
        print("🚀 Initializing Friday...")
        
        # Create and start bot
        friday = FridayBot(BOT_TOKEN)
        print("💫 Friday is now online and ready to help!")
        print("📱 Message your bot on Telegram to start using Friday")
        print("=" * 50)
        
        # Start the bot
        friday.run()
        
    except Exception as e:
        print(f"❌ Error starting Friday: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()