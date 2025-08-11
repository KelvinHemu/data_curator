#!/usr/bin/env python3
"""
Test script to verify Gemini API key is working
"""

import requests
import json
from config import GEMINI_API_KEY, GEMINI_API_URL

def test_gemini_api():
    """Test the Gemini API with a simple request"""
    
    print("🔍 Testing Google Gemini API...")
    print(f"🔑 API Key: {GEMINI_API_KEY[:10]}...{GEMINI_API_KEY[-4:]}")
    print(f"🌐 API URL: {GEMINI_API_URL}")
    print()
    
    if not GEMINI_API_KEY:
        print("❌ No API key found!")
        return False
    
    # Simple test prompt
    test_prompt = "Please clean and format this text: 'Hello    world.   This  is a    test.'"
    
    headers = {
        'Content-Type': 'application/json',
        'X-goog-api-key': GEMINI_API_KEY
    }
    
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": test_prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.1,
            "topK": 40,
            "topP": 0.95,
            "maxOutputTokens": 1024
        }
    }
    
    try:
        print("📡 Sending test request...")
        response = requests.post(
            GEMINI_API_URL,
            headers=headers,
            json=data,
            timeout=30
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            if 'candidates' in result and len(result['candidates']) > 0:
                if 'content' in result['candidates'][0]:
                    generated_text = result['candidates'][0]['content']['parts'][0]['text']
                    print("✅ API is working correctly!")
                    print(f"🤖 Response: {generated_text}")
                    return True
            
            print("⚠️  Unexpected response format")
            print(f"📋 Full response: {json.dumps(result, indent=2)}")
            
        elif response.status_code == 400:
            print("❌ Bad request - check API key or request format")
            print(f"📋 Error: {response.text}")
            
        elif response.status_code == 403:
            print("❌ Forbidden - API key may be invalid or quota exceeded")
            print(f"📋 Error: {response.text}")
            
        elif response.status_code == 429:
            print("❌ Rate limited - try again later")
            print(f"📋 Error: {response.text}")
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"📋 Error: {response.text}")
        
        return False
        
    except requests.RequestException as e:
        print(f"❌ Network error: {e}")
        return False
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    print("🧪 Gemini API Test Tool")
    print("=" * 50)
    
    success = test_gemini_api()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 API test successful! Your pipeline is ready to use.")
        print("\n💡 Next steps:")
        print("   1. Place a PDF file in this directory")
        print("   2. Run: python markdown.py your_document.pdf")
        print("   3. Check the generated markdown files")
    else:
        print("❌ API test failed. Please check:")
        print("   1. Your API key in config.py")
        print("   2. Internet connection")
        print("   3. API quotas and billing")
        print("   4. Visit: https://makersuite.google.com/app/apikey")

if __name__ == "__main__":
    main()
