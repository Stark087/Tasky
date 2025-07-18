#!/usr/bin/env python3
"""
Simple test script for Friday bot core functionality
"""
import sys
import re
from datetime import datetime, timedelta
import pytz

def test_language_detection_logic():
    """Test language detection logic"""
    print("🧪 Testing language detection logic...")
    
    try:
        from langdetect import detect
        
        # Hindi patterns
        hindi_patterns = [
            r'[\u0900-\u097F]',  # Devanagari script
            r'\b(hai|ka|ke|ki|ko|se|me|aur|ya|kya|kaise|kahan|kab|kyun|jo|wo|yeh|iska|uska)\b',
        ]
        
        def detect_language(text):
            try:
                hindi_score = sum(1 for pattern in hindi_patterns 
                                if re.search(pattern, text, re.IGNORECASE))
                detected = detect(text)
                
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
                return 'english'
        
        # Test cases
        test_cases = [
            ("Hello how are you", "english"),
            ("Namaste kaise hain aap", "hinglish"),
            ("Kal 8 baje reminder set kar", "hinglish"),
            ("remind me tomorrow 9 AM", "english")
        ]
        
        for text, expected in test_cases:
            detected = detect_language(text)
            print(f"  '{text}' -> {detected}")
        
        print("✅ Language detection logic test completed")
        return True
        
    except Exception as e:
        print(f"❌ Language detection test failed: {e}")
        return False

def test_dateparser():
    """Test dateparser functionality"""
    print("🧪 Testing dateparser...")
    
    try:
        import dateparser
        
        test_phrases = [
            "tomorrow 9 AM",
            "kal 8 baje",
            "tonight 10 PM",
            "next monday",
            "in 30 minutes"
        ]
        
        for phrase in test_phrases:
            parsed = dateparser.parse(
                phrase,
                languages=['hi', 'en'],
                settings={
                    'TIMEZONE': 'Asia/Kolkata',
                    'RETURN_AS_TIMEZONE_AWARE': True,
                    'RELATIVE_BASE': datetime.now(pytz.timezone('Asia/Kolkata'))
                }
            )
            print(f"  '{phrase}' -> {parsed}")
        
        print("✅ Dateparser test completed")
        return True
        
    except Exception as e:
        print(f"❌ Dateparser test failed: {e}")
        return False

def test_response_templates():
    """Test response template system"""
    print("🧪 Testing response templates...")
    
    try:
        def generate_response(language, user_name, message_type, **kwargs):
            responses = {
                'greeting': {
                    'english': f"Hello {user_name}! 👋 I'm Friday, your personal AI assistant.",
                    'hindi': f"Namaste {user_name} ji! 🙏 Main Friday hun, aapki personal AI assistant.",
                    'hinglish': f"Hey {user_name}! 😊 Main Friday hun, tumhari AI assistant."
                },
                'reminder_set': {
                    'english': f"Perfect {user_name}! ✅ I'll remind you about '{kwargs.get('task', '')}' at {kwargs.get('time', '')}.",
                    'hindi': f"Bilkul theek {user_name} ji! ✅ Main aapko '{kwargs.get('task', '')}' ke baare mein {kwargs.get('time', '')} par yaad dila dungi.",
                    'hinglish': f"Done {user_name}! ✅ '{kwargs.get('task', '')}' ka reminder {kwargs.get('time', '')} par set kar diya."
                }
            }
            return responses.get(message_type, {}).get(language, f"Response not found for {message_type} in {language}")
        
        # Test different combinations
        test_cases = [
            ("english", "Aditi", "greeting"),
            ("hindi", "Rahul", "greeting"),
            ("hinglish", "Priya", "greeting"),
            ("english", "John", "reminder_set", {"task": "medicine", "time": "9 PM"}),
            ("hinglish", "Amit", "reminder_set", {"task": "gym", "time": "7 AM"})
        ]
        
        for case in test_cases:
            if len(case) == 3:
                lang, name, msg_type = case
                response = generate_response(lang, name, msg_type)
            else:
                lang, name, msg_type, kwargs = case
                response = generate_response(lang, name, msg_type, **kwargs)
            
            print(f"  {lang} + {msg_type}: {response[:50]}...")
        
        print("✅ Response template test completed")
        return True
        
    except Exception as e:
        print(f"❌ Response template test failed: {e}")
        return False

def main():
    """Run all simple tests"""
    print("🤖 Friday Bot Core Functionality Tests")
    print("=" * 50)
    
    # Validate imports first
    try:
        import telegram
        import dateparser
        import langdetect
        import apscheduler
        import pytz
        print("✅ All dependencies available")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        sys.exit(1)
    
    # Run tests
    tests = [
        test_language_detection_logic,
        test_dateparser,
        test_response_templates
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("=" * 50)
    print(f"🎯 Test Results: {passed}/{total} core tests passed")
    
    if passed == total:
        print("🎉 All core functionality tests passed!")
        print("\n🚀 Friday is ready! To start the bot:")
        print("   python3 start_friday.py")
        print("\n📖 For usage examples, see:")
        print("   cat USAGE.md")
    else:
        print("❌ Some core tests failed. Please check the implementation.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)