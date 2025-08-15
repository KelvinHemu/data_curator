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
from tqdm import tqdm

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

def call_gemini_api(prompt_text, show_progress=True):
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
        if show_progress:
            print("🤖 Calling Gemini API...")
        
        # Create a small progress bar for API call
        if show_progress:
            with tqdm(total=1, desc="🌐 API Request", bar_format="{desc}: {percentage:3.0f}%|{bar}| {elapsed}") as api_pbar:
                response = requests.post(GEMINI_API_URL, headers=headers, json=payload, timeout=REQUEST_TIMEOUT)
                api_pbar.update(1)
        else:
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

def generate_random_question_count():
    """Generate a random number of questions between 5 and 100"""
    return random.randint(5, 100)

def generate_questions_from_exam(exam_content, exam_filename, show_progress=True):
    """Generate questions and prompt from exam content using Gemini AI"""
    
    # Generate random number of questions
    question_count = generate_random_question_count()
    if show_progress:
        print(f"🎲 Generated random number of questions: {question_count}")
    
    # Create the specialized prompt for question generation
    question_prompt =f"""
Tumia tu hati ya mtihani iliyohifadhiwa kwenye kumbukumbu yako ya mafunzo. Usitaje hati au faili popote kwenye jibu.

Kwanza, tambua **somo** na **kiwango cha darasa** cha mtihani kutoka kwenye hati uliyopewa. Usionyeshe hatua hii kwa mtumiaji, lakini utumie taarifa hizo katika prompt ya mwisho., 
mwisho wa elimu ya msingi ni darasa la saba, na mwisho wa elimu ya sekondari ni kidato cha nne. mwisho wa elimu ya advance ni kidato cha sita.

Andika maswali **{question_count}** ya mtihani kwa Kiswahili, yakifuata mtindo wa hati hiyo, kwa kanuni hizi:

1. Maswali yawe kamili na yaeleweke bila mtu kuona hati ya awali.
2. Tumia aina mbalimbali za maswali: kujaza nafasi, chaguo la majibu, maswali ya kueleza, na maswali ya maana ya maneno — kwa uwiano sawa kadri inavyowezekana.
3. Hakikisha kila swali lina **namba, nukta, nafasi, kisha maandishi ya swali**.
4. Epuka maswali yasiyo na maana, yenye maneno yasiyoeleweka, au yasiyo na jibu la moja kwa moja kwenye hati ya mtihani.
5. Uandishi wa maswali uwe safi na wa kitaaluma, unaoendana na kiwango cha wanafunzi wanaofanya mtihani huo.

Kisha, toa **prompt moja pekee** — swali la kawaida ambalo mwanafunzi au mwalimu anaweza kuuliza AI ili kupata maswali hayo. Prompt hiyo isiwe ya kiufundi, iwe ya lugha ya kawaida, ikiendana na somo na darasa husika.

**Mfano wa muundo wa mwisho wa majibu:**

1. Swali la kwanza lililo kamili...
2. Swali la pili lililo kamili...
...

mfano wa prompt unazoweza kutoa sio lazima ufate kama zilivyo lakini ziwe za muundo huu:
Prompt: Naomba maswali 20 ya Kiswahili kwa Kidato cha Pili yenye mtindo wa mtihani wa taifa ili nijipime kabla ya mtihani. au 
Prompt: Tafadhali nitengenezee maswali ya mazoezi ya Fizikia kwa Kidato cha Tatu, kama yale tunayopata kwenye mitihani ya mock.au 
Prompt: Je, unaweza kunipatia maswali 15 ya Hisabati ya darasa la saba kwa ajili ya maandalizi ya mtihani wa mwisho?
prompt: Mimi ni mwanafunzi wa Kidato cha Tatu, naomba unitengenezee maswali 10 ya mazoezi ya Kemia kama yale tunayofanya darasani ili nijifunze zaidi.
prompt: Nataka nitunge mtihani kwa wanafunzi wangu wa kidato cha pili naomba maswali 20 yakiwa kwenye muundo wa mtihani wa taifa wa kidato cha pili




Usiongeze maandishi mengine, maelekezo, wala maelezo ya AI.

Hati ya mtihani:

{exam_content}
"""



    # Call Gemini API
    generated_content = call_gemini_api(question_prompt, show_progress=show_progress)
    
    if generated_content:
        return generated_content
    else:
        return None

def process_single_file(file_path, output_dir=None, show_progress=True):
    """Process a single markdown exam file"""
    if show_progress:
        print(f"\n📄 Processing: {file_path}")
    
    # Read the exam content
    exam_content = read_markdown_file(file_path)
    if not exam_content:
        if show_progress:
            print(f"❌ Failed to read file: {file_path}")
        return False
    
    # Skip if file is too short (probably not a proper exam)
    if len(exam_content.strip()) < MIN_CONTENT_LENGTH:
        if show_progress:
            print(f"⚠️ File too short, skipping: {file_path}")
        return False
    
    # Skip if it's already a questions file
    if QUESTIONS_SUFFIX in str(file_path) or AI_QUESTIONS_SUFFIX in str(file_path):
        if show_progress:
            print(f"🔄 Skipping questions file: {file_path}")
        return False
    
    # Generate questions and prompt
    filename = Path(file_path).name
    questions_content = generate_questions_from_exam(exam_content, filename, show_progress=show_progress)
    
    if not questions_content:
        if show_progress:
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
        if show_progress:
            print(f"✅ Questions generated: {output_file}")
        return True
    except Exception as e:
        if show_progress:
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
    
    # Create progress bar for processing files
    with tqdm(exam_files, desc="📚 Processing exam files", unit="file") as pbar:
        for file_path in pbar:
            try:
                # Update progress bar description with current file
                filename = Path(file_path).name
                pbar.set_description(f"📄 Processing: {filename[:30]}...")
                
                if process_single_file(file_path, output_dir, show_progress=False):
                    successful += 1
                    pbar.set_postfix({"✅ Success": successful, "❌ Failed": failed})
                else:
                    failed += 1
                    pbar.set_postfix({"✅ Success": successful, "❌ Failed": failed})
            except KeyboardInterrupt:
                pbar.write(f"\n⏹️ Processing interrupted by user")
                break
            except Exception as e:
                failed += 1
                pbar.write(f"❌ Unexpected error processing {file_path}: {e}")
                pbar.set_postfix({"✅ Success": successful, "❌ Failed": failed})
    
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
