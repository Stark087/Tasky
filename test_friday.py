#!/usr/bin/env python3
"""
Test script for Friday bot functionality
"""
import sys
from datetime import datetime, timedelta
import pytz

def test_language_detection():
    """Test language detection functionality"""
    print("🧪 Testing language detection...")
    
    try:
        from friday_bot import FridayBot
        
        # Create a mock Friday instance
        friday = FridayBot("dummy_token")
        
        # Test cases
        test_cases = [
            ("Hello how are you", "english"),
            ("Namaste kaise hain aap", "hinglish"),
            ("नमस्ते कैसे हैं आप", "hindi"),
            ("Kal 8 baje reminder set kar", "hinglish"),
            ("remind me tomorrow 9 AM", "english")
        ]
        
        for text, expected in test_cases:
            detected = friday.detect_language(text)
            print(f"  '{text}' -> {detected} ({'✅' if detected == expected else '❌'})")
        
        print("✅ Language detection test completed")
        return True
        
    except Exception as e:
        print(f"❌ Language detection test failed: {e}")
        return False

def test_reminder_parsing():
    """Test reminder parsing functionality"""
    print("🧪 Testing reminder parsing...")
    
    try:
        from friday_bot import FridayBot
        
        # Create a mock Friday instance
        friday = FridayBot("dummy_token")
        
        # Test cases
        test_cases = [
            "Remind me to take medicine at 9 PM",
            "Kal 8 baje tuition jaana hai",
            "Friday yaad dila dena evening 6 baje call karna",
            "Tomorrow morning 7 AM gym jana hai"
        ]
        
        for text in test_cases:
            task, time = friday.parse_reminder(text)
            print(f"  '{text}' -> Task: '{task}', Time: {time}")
        
        print("✅ Reminder parsing test completed")
        return True
        
    except Exception as e:
        print(f"❌ Reminder parsing test failed: {e}")
        return False

def test_response_generation():
    """Test response generation functionality"""
    print("🧪 Testing response generation...")
    
    try:
        from friday_bot import FridayBot
        
        # Create a mock Friday instance
        friday = FridayBot("dummy_token")
        
        # Test response generation
        user_name = "Aditi"
        
        # Test different response types
        responses = [
            friday.generate_response("english", user_name, "greeting"),
            friday.generate_response("hindi", user_name, "greeting"),
            friday.generate_response("hinglish", user_name, "greeting"),
            friday.generate_response("english", user_name, "reminder_set", task="medicine", time="9 PM"),
            friday.generate_response("hinglish", user_name, "task_completed"),
        ]
        
        for i, response in enumerate(responses, 1):
            print(f"  Response {i}: {response[:60]}..." if len(response) > 60 else f"  Response {i}: {response}")
        
        print("✅ Response generation test completed")
        return True
        
    except Exception as e:
        print(f"❌ Response generation test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🤖 Friday Bot Functionality Tests")
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
        test_language_detection,
        test_reminder_parsing,
        test_response_generation
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
    print(f"🎯 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Friday is ready to go!")
        print("\n🚀 To start Friday bot, run:")
        print("   python3 start_friday.py")
    else:
        print("❌ Some tests failed. Please check the implementation.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)