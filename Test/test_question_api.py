#!/usr/bin/env python3
"""
Quick test script to verify Google Gemini API connection
and question generation functionality
"""

import requests
import json
from question_config import GEMINI_API_KEY, GEMINI_API_URL

def test_api_connection():
    """Test basic API connectivity"""
    print("🧪 Testing Google Gemini API connection...")
    
    headers = {
        'Content-Type': 'application/json',
        'X-goog-api-key': GEMINI_API_KEY
    }
    
    # Simple test prompt
    test_payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": "Andika 'Habari' kwa Kiswahili na 'Hello' kwa Kiingereza."
                    }
                ]
            }
        ]
    }
    
    try:
        response = requests.post(GEMINI_API_URL, headers=headers, json=test_payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        print("✅ API connection successful!")
        
        # Extract response text
        if 'candidates' in result and len(result['candidates']) > 0:
            if 'content' in result['candidates'][0] and 'parts' in result['candidates'][0]['content']:
                response_text = result['candidates'][0]['content']['parts'][0]['text']
                print(f"📝 API Response: {response_text.strip()}")
                return True
        
        print("⚠️ Unexpected response format")
        return False
        
    except requests.exceptions.RequestException as e:
        print(f"❌ API connection failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_question_generation():
    """Test question generation with sample exam content"""
    print("\n🧪 Testing question generation...")
    
    # Sample exam content
    sample_exam = """
MTIHANI WA HISABATI - DARASA LA SABA

Muda: Masaa 2:30
Alama: 100

SEHEMU A: Chagua jibu sahihi (Alama 40)

1. Tafuta thamani ya 45 + 67 - 23
   a) 89  b) 99  c) 79  d) 69

2. Ikiwa mzunguko wa duara ni 44cm, kipimo cha nusu kipenyo ni:
   a) 7cm  b) 14cm  c) 21cm  d) 28cm

SEHEMU B: Tatua maswali yafuatayo (Alama 60)

3. Duka la Juma lilimpata faida ya Tsh. 450,000 mwezi Januari na Tsh. 350,000 mwezi Februari. 
   Je, jumla ya faida ni kiasi gani?

4. Eneo la bustani ya mraba ambayo urefu wake ni mita 15 ni:
"""

    headers = {
        'Content-Type': 'application/json',
        'X-goog-api-key': GEMINI_API_KEY
    }
    
    # Question generation prompt
    question_prompt = f"""Tumia hati niliyokupa ya mtihani kama rejea pekee.

Tengeneza maswali **(kati ya 5 to 20** choose a random number) kutoka kwenye document hiyo.

Pia, toa **prompt moja tu (swali ambalo mwanafunzi au mwalimu anaweza kumuuliza AI ili kupata maswali kama hayo)**.

**Jibu lazima lianze moja kwa moja na namba ya swali. Usiongeze maelezo yoyote ya ziada, maelekezo, wala maneno ya utangulizi.**

Mfano sahihi wa jibu ni:

```
1. Maswali...
2. Maswali...
...
Prompt: [Swali lolote ambalo mwanafunzi au mwalimu anaweza uliza, akiwa anasoma au anaandaa mtihani pia iendane na darasa na somo pia humanize it make it like how real student or teacher would ask]

```

**Usijibu chochote kingine nje ya muundo huo.**

**Important Rules:**

- Maswali yawe ya kueleweka na yachukuliwe tu kutoka kwenye hati ya mtihani.
- Epuka kuandika chochote nje ya maswali yenye namba na prompt ya mwisho.
- Hakikisha maswali yanahusiana na mtihani uliowekwa.

Hii ndio hati ya mtihani:

{sample_exam}"""

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": question_prompt
                    }
                ]
            }
        ]
    }
    
    try:
        response = requests.post(GEMINI_API_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        
        if 'candidates' in result and len(result['candidates']) > 0:
            if 'content' in result['candidates'][0] and 'parts' in result['candidates'][0]['content']:
                generated_questions = result['candidates'][0]['content']['parts'][0]['text']
                print("✅ Question generation successful!")
                print("\n📝 Generated Questions:")
                print("-" * 50)
                print(generated_questions.strip())
                print("-" * 50)
                return True
        
        print("⚠️ Unexpected response format")
        return False
        
    except Exception as e:
        print(f"❌ Question generation failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Question Generator API Test Suite")
    print("=" * 50)
    print(f"🔑 API Key: {GEMINI_API_KEY[:20]}...")
    print(f"🌐 API URL: {GEMINI_API_URL}")
    
    # Test 1: Basic API connection
    api_test = test_api_connection()
    
    if api_test:
        # Test 2: Question generation
        question_test = test_question_generation()
        
        if question_test:
            print("\n🎉 All tests passed! The question generator is ready to use.")
            print("\n💡 Next steps:")
            print("   1. Run the main scraper: python questions.py")
            print("   2. Generate questions: python question_generator.py")
        else:
            print("\n⚠️ API works but question generation needs adjustment")
    else:
        print("\n❌ API connection failed. Check your API key and internet connection.")
        print("\n🔧 Troubleshooting:")
        print("   1. Verify API key in question_config.py")
        print("   2. Check internet connection")
        print("   3. Ensure API key has proper permissions")

if __name__ == "__main__":
    main()
