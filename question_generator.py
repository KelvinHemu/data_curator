#!/usr/bin/env python3
"""
Question Generator for Tetea Exam Papers
Specialized data preparation tool that reads markdown exam files and generates:
1. 5-20 questions extracted from the exam content
2. A single prompt that students/teachers can use to get similar questions

Uses Google Gemini API for intelligent question generation.
"""

import os
import json
import random
import requests
import argparse
from pathlib import Path

# Import configuration
try:
    from question_config import *
    print("✅ Configuration loaded from question_config.py")
except ImportError:
    # Fallback configuration
    GEMINI_API_KEY = "AIzaSyB0xMJvzkoJBeE0hHSzzbCgLsBUYFMd7cU"
    GEMINI_MODEL = "gemini-2.0-flash"
    GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
    DEFAULT_EXAM_DIR = "tetea_exam_papers"
    REQUEST_TIMEOUT = 60
    MIN_CONTENT_LENGTH = 100
    AI_QUESTIONS_SUFFIX = "_ai_questions.md"
    QUESTIONS_SUFFIX = "_questions.md"
    print("⚠️ Using fallback configuration")

def read_markdown_file(file_path):
    """Read content from a markdown file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        return content
    except Exception as e:
        print(f"❌ Error reading file {file_path}: {e}")
        return None

def call_gemini_api(prompt_text):
    """Call Google Gemini API to generate questions and prompt"""
    headers = {
        'Content-Type': 'application/json',
        'X-goog-api-key': GEMINI_API_KEY
    }
    
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt_text
                    }
                ]
            }
        ]
    }
    
    try:
        print("🤖 Calling Gemini API...")
        response = requests.post(GEMINI_API_URL, headers=headers, json=payload, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        
        result = response.json()
        
        # Extract the generated text from the response
        if 'candidates' in result and len(result['candidates']) > 0:
            if 'content' in result['candidates'][0] and 'parts' in result['candidates'][0]['content']:
                generated_text = result['candidates'][0]['content']['parts'][0]['text']
                return generated_text.strip()
        
        print("❌ Unexpected API response format")
        return None
        
    except requests.exceptions.RequestException as e:
        print(f"❌ API request failed: {e}")
        return None
    except Exception as e:
        print(f"❌ Error calling Gemini API: {e}")
        return None

def generate_questions_from_exam(exam_content, exam_filename):
    """Generate questions and prompt from exam content using Gemini AI"""
    
    # Create the specialized prompt for question generation
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

{exam_content}"""

    # Call Gemini API
    generated_content = call_gemini_api(question_prompt)
    
    if generated_content:
        return generated_content
    else:
        return None

def process_single_file(file_path, output_dir=None):
    """Process a single markdown exam file"""
    print(f"\n📄 Processing: {file_path}")
    
    # Read the exam content
    exam_content = read_markdown_file(file_path)
    if not exam_content:
        print(f"❌ Failed to read file: {file_path}")
        return False
    
    # Skip if file is too short (probably not a proper exam)
    if len(exam_content.strip()) < MIN_CONTENT_LENGTH:
        print(f"⚠️ File too short, skipping: {file_path}")
        return False
    
    # Skip if it's already a questions file
    if QUESTIONS_SUFFIX in str(file_path) or AI_QUESTIONS_SUFFIX in str(file_path):
        print(f"🔄 Skipping questions file: {file_path}")
        return False
    
    # Generate questions and prompt
    filename = Path(file_path).name
    questions_content = generate_questions_from_exam(exam_content, filename)
    
    if not questions_content:
        print(f"❌ Failed to generate questions for: {file_path}")
        return False
    
    # Determine output file path
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"{Path(file_path).stem}{AI_QUESTIONS_SUFFIX}")
    else:
        # Save in the same directory as the original file
        output_file = str(file_path).replace('.md', AI_QUESTIONS_SUFFIX)
    
    # Create the final output with header
    final_output = f"""# Maswali ya Mtihani ya AI
*Maswali yametengenezwa na AI kutoka kwa mtihani: {filename}*

---

{questions_content}

---
*Maswali haya yametengenezwa kwa kutumia Google Gemini AI kutoka kwenye mtihani halisi.*
"""
    
    # Save the generated questions
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(final_output)
        print(f"✅ Questions generated: {output_file}")
        return True
    except Exception as e:
        print(f"❌ Error saving questions: {e}")
        return False

def find_exam_files(directory):
    """Find all exam markdown files (excluding question files)"""
    exam_files = []
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if (file.endswith('.md') and 
                QUESTIONS_SUFFIX not in file and 
                AI_QUESTIONS_SUFFIX not in file):
                exam_files.append(os.path.join(root, file))
    
    return exam_files

def process_directory(directory, output_dir=None):
    """Process all exam files in a directory"""
    print(f"\n🔍 Searching for exam files in: {directory}")
    
    exam_files = find_exam_files(directory)
    
    if not exam_files:
        print(f"📭 No exam files found in: {directory}")
        return
    
    print(f"📚 Found {len(exam_files)} exam files")
    
    successful = 0
    failed = 0
    
    for file_path in exam_files:
        try:
            if process_single_file(file_path, output_dir):
                successful += 1
            else:
                failed += 1
        except KeyboardInterrupt:
            print(f"\n⏹️ Processing interrupted by user")
            break
        except Exception as e:
            print(f"❌ Unexpected error processing {file_path}: {e}")
            failed += 1
    
    print(f"\n📊 PROCESSING SUMMARY")
    print("=" * 40)
    print(f"✅ Successfully processed: {successful} files")
    print(f"❌ Failed: {failed} files")
    print(f"📁 Output location: {output_dir if output_dir else 'Same as source files'}")

def main():
    """Main function with command line argument support"""
    parser = argparse.ArgumentParser(description='Generate questions from Tetea exam markdown files using Google Gemini AI')
    parser.add_argument('--file', '-f', help='Process a single markdown file')
    parser.add_argument('--directory', '-d', default=DEFAULT_EXAM_DIR, 
                       help=f'Process all exam files in directory (default: {DEFAULT_EXAM_DIR})')
    parser.add_argument('--output', '-o', help='Output directory for generated questions (optional)')
    parser.add_argument('--list', '-l', action='store_true', help='List available exam files without processing')
    
    args = parser.parse_args()
    
    print("🧠 Tetea Exam Question Generator")
    print("=" * 50)
    print(f"🤖 Using Google Gemini API for question generation")
    print(f"🔑 API Key: {GEMINI_API_KEY[:20]}...")
    
    if args.list:
        # List available files
        if os.path.exists(args.directory):
            exam_files = find_exam_files(args.directory)
            print(f"\n📚 Available exam files in {args.directory}:")
            for i, file_path in enumerate(exam_files, 1):
                rel_path = os.path.relpath(file_path, args.directory)
                print(f"  {i}. {rel_path}")
            print(f"\nTotal: {len(exam_files)} exam files")
        else:
            print(f"❌ Directory not found: {args.directory}")
        return
    
    if args.file:
        # Process single file
        if os.path.exists(args.file):
            process_single_file(args.file, args.output)
        else:
            print(f"❌ File not found: {args.file}")
    else:
        # Process directory
        if os.path.exists(args.directory):
            process_directory(args.directory, args.output)
        else:
            print(f"❌ Directory not found: {args.directory}")
            print(f"💡 Make sure you have run the main scraper first to create exam files")

if __name__ == "__main__":
    main()
