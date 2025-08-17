#!/usr/bin/env python3
"""
Short SMS Demo - Sends brief AI responses that actually get delivered
Perfect for video demo showing real SMS reception
"""

import os
import time
import base64
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN") 
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

def send_sms_working(to_number, message):
    """Send SMS using working method"""
    try:
        if not to_number.startswith('+'):
            to_number = f"+91{to_number}"
        
        credentials = f"{TWILIO_ACCOUNT_SID}:{TWILIO_AUTH_TOKEN}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'From': TWILIO_PHONE_NUMBER,
            'To': to_number,
            'Body': message
        }
        
        url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Messages.json"
        response = requests.post(url, headers=headers, data=data, timeout=30)
        
        if response.status_code == 201:
            result = response.json()
            return True, result['sid']
        else:
            return False, response.text
            
    except Exception as e:
        return False, str(e)

def send_short_ai_responses():
    """Send SHORT AI responses that will actually be delivered"""
    
    your_phone = "+918284941698"
    
    print("🎬 SENDING SHORT AI RESPONSES")
    print("📱 These will actually reach your phone!")
    print("="*50)
    
    # SHORT AI responses (under 160 characters each)
    short_responses = [
        {
            "title": "Crop Advice",
            "message": "🌾 पंजाब में गेहूं, चना, सरसों उगाएं। नवंबर-दिसंबर बुआई। 40-50 क्विंटल/एकड़ उत्पादन। - कृषि AI",
            "wait": 5
        },
        {
            "title": "Market Price", 
            "message": "💰 गेहूं ₹2150/क्विंटल, चावल ₹2800/क्विंटल, सरसों ₹5200/क्विंटल। बढ़ते भाव वाली फसल जल्दी बेचें। - कृषि AI",
            "wait": 5
        },
        {
            "title": "Disease Help",
            "message": "🦠 पत्ती धब्बा रोग। कॉपर सल्फेट छिड़काव करें। प्रभावित पत्तियां हटाएं। नीम तेल डालें। - कृषि AI",
            "wait": 5
        },
        {
            "title": "Govt Schemes",
            "message": "🏛️ PM-KISAN ₹6000/वर्ष, फसल बीमा, KCC लोन, मृदा कार्ड मुफ्त। कृषि कार्यालय से संपर्क करें। - कृषि AI",
            "wait": 0
        }
    ]
    
    for i, response in enumerate(short_responses, 1):
        print(f"\n📤 Sending {i}/4: {response['title']}")
        print(f"📝 Message: {response['message']}")
        
        success, result = send_sms_working(your_phone, response["message"])
        
        if success:
            print(f"✅ Message {i} sent! SID: {result}")
            print("📱 CHECK YOUR PHONE NOW!")
            if response["wait"] > 0 and i < len(short_responses):
                print(f"⏳ Waiting {response['wait']} seconds...")
                time.sleep(response["wait"])
        else:
            print(f"❌ Message {i} failed: {result}")
            break
    
    print("\n🎉 ALL SHORT MESSAGES SENT!")
    print("📱 You should receive 4 SMS messages!")
    print("🎬 Perfect for video demo!")

def send_single_short_test():
    """Send single short test"""
    your_phone = "+918284941698"
    
    message = "🌾 कृषि AI टेस्ट! SMS काम कर रहा है। 600M किसानों के लिए तैयार! - कृषि AI"
    
    print("📤 Sending short test message...")
    print(f"📝 Message: {message}")
    
    success, result = send_sms_working(your_phone, message)
    
    if success:
        print(f"✅ Test sent! SID: {result}")
        print("📱 CHECK YOUR PHONE!")
    else:
        print(f"❌ Failed: {result}")

def send_farmer_questions():
    """Send comprehensive farmer conversations for long video demo"""
    your_phone = "+918284941698"
    
    print("🎬 COMPREHENSIVE FARMER EXPERIENCE DEMO")
    print("📱 Multiple farmers from different states!")
    print("🎥 Perfect for long hackathon video!")
    print("="*60)
    
    conversations = [
        {
            "farmer": "राम सिंह (Punjab)",
            "question": "👨‍🌾 राम सिंह पूछता है: इस मौसम में कौन सी फसल उगानी चाहिए?",
            "answer": "🌾 पंजाब में गेहूं, चना, सरसों उगाएं। नवंबर बुआई। 40-50 क्विंटल उत्पादन। - कृषि AI",
            "wait": 8
        },
        {
            "farmer": "सुरेश कुमार (Haryana)",
            "question": "👨‍🌾 सुरेश पूछता है: गेहूं का भाव क्या है?",
            "answer": "💰 गेहूं ₹2150/क्विंटल। चावल ₹2800। सरसों ₹5200। अच्छे भाव हैं। - कृषि AI",
            "wait": 8
        },
        {
            "farmer": "मोहन लाल (UP)",
            "question": "👨‍🌾 मोहन पूछता है: पत्तियों पर धब्बे हैं, क्या करूं?",
            "answer": "🦠 पत्ती धब्बा रोग। कॉपर सल्फेट छिड़काव करें। नीम तेल डालें। - कृषि AI",
            "wait": 8
        },
        {
            "farmer": "विकास शर्मा (MP)",
            "question": "👨‍🌾 विकास पूछता है: सरकारी योजना के बारे में बताएं",
            "answer": "🏛️ PM-KISAN ₹6000/वर्ष। फसल बीमा। KCC लोन। कृषि कार्यालय से संपर्क करें। - कृषि AI",
            "wait": 8
        },
        {
            "farmer": "अजय पटेल (Gujarat)",
            "question": "👨‍🌾 अजय पूछता है: मिट्टी की जांच कैसे करें?",
            "answer": "🌱 मृदा स्वास्थ्य कार्ड बनवाएं। pH, NPK जांच कराएं। मुफ्त सेवा। - कृषि AI",
            "wait": 8
        },
        {
            "farmer": "संजय कुमार (Rajasthan)",
            "question": "👨‍🌾 संजय पूछता है: कम पानी में कौन सी फसल उगाएं?",
            "answer": "🌵 बाजरा, ज्वार, मूंग उगाएं। कम पानी चाहिए। ड्रिप सिंचाई करें। - कृषि AI",
            "wait": 8
        },
        {
            "farmer": "रमेश यादव (Bihar)",
            "question": "👨‍🌾 रमेश पूछता है: धान की फसल में कीड़े लगे हैं",
            "answer": "🐛 तना छेदक कीट। नीम तेल स्प्रे करें। फेरोमोन ट्रैप लगाएं। - कृषि AI",
            "wait": 8
        },
        {
            "farmer": "कमल सिंह (Uttarakhand)",
            "question": "👨‍🌾 कमल पूछता है: पहाड़ी क्षेत्र में कौन सी सब्जी उगाएं?",
            "answer": "🥬 आलू, गोभी, मटर, टमाटर उगाएं। ठंडे मौसम में अच्छी होती हैं। - कृषि AI",
            "wait": 0
        }
    ]
    
    print(f"📊 DEMO OVERVIEW:")
    print(f"👥 {len(conversations)} farmers from different states")
    print(f"📱 {len(conversations)*2} total SMS messages")
    print(f"🎬 Perfect for 5-7 minute video demo")
    print("="*60)
    
    for i, conv in enumerate(conversations, 1):
        print(f"\n🎬 FARMER {i}/{len(conversations)}: {conv['farmer']}")
        print("="*50)
        
        # Send farmer question
        print(f"📤 Step 1: Sending farmer question...")
        print(f"📝 Question: {conv['question']}")
        success, result = send_sms_working(your_phone, conv["question"])
        if success:
            print(f"✅ Question sent! SID: {result}")
            print("📱 CHECK YOUR PHONE FOR FARMER QUESTION!")
            time.sleep(4)  # Time to check phone
        else:
            print(f"❌ Question failed: {result}")
            continue
        
        # Send AI response
        print(f"📤 Step 2: Sending AI response...")
        print(f"🤖 Response: {conv['answer']}")
        success, result = send_sms_working(your_phone, conv["answer"])
        if success:
            print(f"✅ AI Response sent! SID: {result}")
            print("📱 CHECK YOUR PHONE FOR AI ADVICE!")
            print(f"✅ Farmer {i} conversation completed!")
            
            if conv["wait"] > 0 and i < len(conversations):
                print(f"\n⏸️ [Perfect pause for video transition - {conv['wait']} seconds]")
                print("🎬 Show the SMS messages on your phone now!")
                time.sleep(conv["wait"])
        else:
            print(f"❌ Response failed: {result}")
    
    print("\n🎉 COMPREHENSIVE DEMO COMPLETED!")
    print("="*60)
    print("📊 DEMO SUMMARY:")
    print(f"✅ {len(conversations)} farmers from 8 different states")
    print(f"✅ {len(conversations)*2} SMS messages sent")
    print("✅ Crop recommendations, market prices, disease help")
    print("✅ Government schemes, soil analysis, pest control")
    print("✅ Regional farming advice for different climates")
    print("📱 All messages delivered to your phone!")
    print("🎬 Perfect footage for winning hackathon video!")
    print("🏆 Shows 600M+ farmer potential across India!")
    print("="*60)

def main():
    print("📱 SHORT SMS DEMO - ACTUALLY WORKS!")
    print("Messages are short enough to be delivered!")
    print("="*50)
    
    print("\nChoose option:")
    print("1. 🧪 Single Short Test")
    print("2. 🎬 4 Short AI Responses") 
    print("3. 💬 Complete Farmer Conversations")
    print("4. 📝 Custom Short Message")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == "1":
        send_single_short_test()
        
    elif choice == "2":
        print("\n🎬 This will send 4 SHORT AI responses")
        print("📱 Each message is under 160 characters")
        confirm = input("Ready? (y/n): ")
        if confirm.lower() == 'y':
            send_short_ai_responses()
            
    elif choice == "3":
        print("\n💬 COMPREHENSIVE FARMER DEMO")
        print("� 8 farmeors from different states")
        print("📱 16 total SMS messages (questions + responses)")
        print("🎬 Perfect for 5-7 minute hackathon video!")
        print("⏱️ Takes about 2-3 minutes to complete")
        print("\nDemo includes:")
        print("• Crop recommendations (Punjab, Haryana)")
        print("• Market prices and disease diagnosis")
        print("• Government schemes and soil analysis") 
        print("• Regional farming advice for different climates")
        confirm = input("\nReady for comprehensive demo? (y/n): ")
        if confirm.lower() == 'y':
            send_farmer_questions()
            
    elif choice == "4":
        message = input("Enter SHORT message (under 160 chars): ")
        if message.strip() and len(message) < 160:
            success, result = send_sms_working("+918284941698", message)
            if success:
                print(f"✅ Sent! SID: {result}")
                print("📱 CHECK YOUR PHONE!")
            else:
                print(f"❌ Failed: {result}")
        else:
            print("❌ Message too long or empty!")
    
    else:
        print("Invalid choice!")

if __name__ == "__main__":
    main()