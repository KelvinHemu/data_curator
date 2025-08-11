#!/usr/bin/env python3
import pytesseract
from pdf2image import convert_from_path
import sys
import os
import re
import argparse
from datetime import datetime
from PIL import Image, ImageEnhance, ImageFilter
import requests
import json
import time

# Import configuration
try:
    from config import GEMINI_API_KEY, DEFAULT_OUTPUT_DIR, GEMINI_API_URL, MAX_RETRIES, REQUEST_TIMEOUT
except ImportError:
    # Fallback if config.py doesn't exist
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
    DEFAULT_OUTPUT_DIR = "Markdown"
    GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    MAX_RETRIES = 3
    REQUEST_TIMEOUT = 60

def ensure_output_directory(directory):
    """Ensure the output directory exists, create if it doesn't"""
    if not os.path.exists(directory):
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"✅ Created output directory: {directory}")
        except Exception as e:
            print(f"❌ Error creating directory {directory}: {e}")
            print("💡 Using current directory instead")
            return "."
    return directory

def get_current_date():
    """Get current date in Swahili format"""
    return datetime.now().strftime("%d/%m/%Y")

def preprocess_image(image):
    """
    Preprocess image to improve OCR accuracy
    """
    try:
        # Convert to grayscale if needed
        if image.mode != 'L':
            image = image.convert('L')
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.5)
        
        # Enhance sharpness
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(2.0)
        
        # Apply a slight blur to reduce noise, then sharpen
        image = image.filter(ImageFilter.MedianFilter(size=3))
        
        return image
    except Exception as e:
        print(f"   Warning: Image preprocessing failed: {e}")
        return image

def clean_and_format_text(text):
    """
    Clean and format extracted text for better markdown presentation
    """
    if not text.strip():
        return ""
    
    # Remove watermarks and unwanted text
    text = re.sub(r'Find this and other free resources at:\s*https://maktaba\.tetea\.org\s*CS\s*CamScanner', '', text, flags=re.IGNORECASE)
    text = re.sub(r'https://maktaba\.tetea\.org\s*CS\s*CamScanner', '', text, flags=re.IGNORECASE)
    text = re.sub(r'CS\s*CamScanner', '', text, flags=re.IGNORECASE)
    text = re.sub(r'maktaba\.tetea\.org', '', text, flags=re.IGNORECASE)
    
    # Split into lines and clean
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        line = line.strip()
        if line:  # Only add non-empty lines
            # Skip lines that contain watermark remnants
            if any(keyword in line.lower() for keyword in ['maktaba', 'tetea', 'camscanner', 'free resources']):
                continue
                
            # Fix common OCR issues with numbers and punctuation
            line = re.sub(r'(\d+)\.(\s*[A-Z])', r'\1. \2', line)  # Fix "1.A" to "1. A"
            line = re.sub(r'(\d+)\s*\.\s*', r'\1. ', line)  # Fix number formatting
            line = re.sub(r'\s+', ' ', line)  # Replace multiple spaces with single space
            line = re.sub(r'([A-Z])\s+([A-Z])\s+([A-Z])', r'\1 \2 \3', line)  # Fix spaced letters
            
            # Fix common OCR mistakes for Swahili/English text
            line = re.sub(r'\bJe,?\s*', 'Je, ', line)  # Fix "Je" formatting
            line = re.sub(r'\bIpi\b', 'Ipi', line)  # Common Swahili word
            line = re.sub(r'\bKwa\s+nini\b', 'Kwa nini', line)  # Fix spacing
            line = re.sub(r'(\d+)\s*°\s*C', r'\1°C', line)  # Fix temperature notation
            line = re.sub(r'(\d+)\s*:\s*(\d+)', r'\1:\2', line)  # Fix time notation
            
            # Fix multiple choice options formatting
            line = re.sub(r'^([A-E])\s+([A-Z])', r'\1 \2', line)  # Fix option spacing
            
            # Check if line looks like a question number (starts with number and period)
            if re.match(r'^\d+\.\s*', line):
                cleaned_lines.append(f"\n{line}")  # Add extra space before questions
            # Check if line looks like a title (all caps, reasonable length)
            elif len(line) < 100 and line.isupper() and len(line) > 10:
                cleaned_lines.append(f"\n**{line}**")  # Make titles bold with spacing
            # Check if line looks like options (A, B, C, D, E at start)
            elif re.match(r'^[A-E]\s+', line):
                cleaned_lines.append(f"   {line}")  # Indent options more
            # Check for sub-questions or parts (like "41.", "42.", etc.)
            elif re.match(r'^\d{2,3}\.\s*\([a-z]\)', line):
                cleaned_lines.append(f"\n{line}")  # Format sub-questions
            # Check for section headers (SEHEMU, SECTION, etc.)
            elif re.match(r'^(SEHEMU|SECTION|PART)\s+[A-Z]', line, re.IGNORECASE):
                cleaned_lines.append(f"\n## {line}")  # Make section headers
            else:
                cleaned_lines.append(line)
    
    # Join lines and create clean paragraphs
    text_content = '\n'.join(cleaned_lines)
    
    # Clean up extra newlines (more than 3 become 2)
    text_content = re.sub(r'\n{4,}', '\n\n', text_content)
    
    # Fix common formatting issues
    text_content = re.sub(r'(\d+)\s*\.\s*\n\s*([A-Z])', r'\1. \2', text_content)  # Join broken questions
    text_content = re.sub(r'([a-z])\s*\n\s*([a-z])', r'\1 \2', text_content)  # Join broken words
    
    # Create proper paragraphs
    paragraphs = text_content.split('\n\n')
    formatted_paragraphs = []
    
    for para in paragraphs:
        para = para.strip()
        if para:
            formatted_paragraphs.append(para)
    
    return '\n\n'.join(formatted_paragraphs)

def get_output_filename(input_file, language, output_dir):
    """Generate output filename based on input file and language with custom directory"""
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    lang_suffix = f"_{language}" if language != "swa+eng" else "_multilang"
    filename = f"{base_name}_extracted{lang_suffix}.md"
    
    # Ensure output directory exists
    output_dir = ensure_output_directory(output_dir)
    
    return os.path.join(output_dir, filename)

def send_to_gemini_ai(text_content, max_retries=None):
    """
    Send extracted text to Google Gemini AI for cleaning and formatting
    
    Args:
        text_content (str): The extracted text to be processed
        max_retries (int): Maximum number of retry attempts (uses config default if None)
        
    Returns:
        str: Cleaned and formatted text from Gemini AI, or original text if API fails
    """
    if max_retries is None:
        max_retries = MAX_RETRIES
        
    if not GEMINI_API_KEY:
        print("⚠️  GEMINI_API_KEY not found in config.py or environment variables")
        print("💡 Skipping AI processing, returning original text")
        return text_content
    
    if not text_content.strip():
        print("⚠️  No content to send to Gemini AI")
        return text_content
    
    print("🤖 Sending text to Google Gemini AI for cleaning and formatting...")
    
    # Create the prompt for Gemini AI
    prompt = f"""
Please clean and format the following text that was extracted from a PDF using OCR. The text contains educational content, likely exam questions in Swahili and/or English.

Your task is to:
1. Fix OCR errors and typos
2. Improve formatting and structure
3. Ensure proper question numbering and formatting
4. Fix spacing and punctuation
5. Make multiple choice options clear and properly formatted
6. Preserve the original language (Swahili/English)
7. Return the result in clean markdown format
8. Remove any remaining watermarks or irrelevant content
9. Ensure proper section headers and organization

Here is the text to clean:

{text_content}

Please return only the cleaned and formatted markdown text without any additional comments or explanations.
"""
    
    # Prepare the API request
    headers = {
        'Content-Type': 'application/json',
        'X-goog-api-key': GEMINI_API_KEY
    }
    
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.1,  # Low temperature for more consistent formatting
            "topK": 40,
            "topP": 0.95,
            "maxOutputTokens": 8192
        }
    }
    
    # Try to send request with retries
    for attempt in range(max_retries):
        try:
            print(f"   🔄 Attempt {attempt + 1}/{max_retries}...")
            
            response = requests.post(
                GEMINI_API_URL,
                headers=headers,
                json=data,
                timeout=REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract the generated text
                if 'candidates' in result and len(result['candidates']) > 0:
                    if 'content' in result['candidates'][0]:
                        generated_text = result['candidates'][0]['content']['parts'][0]['text']
                        print("   ✅ Successfully processed by Gemini AI")
                        print(f"   📊 Input length: {len(text_content)} chars")
                        print(f"   📊 Output length: {len(generated_text)} chars")
                        return generated_text.strip()
                
                print("   ⚠️  Unexpected response format from Gemini AI")
                
            elif response.status_code == 429:  # Rate limit
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"   ⏳ Rate limited, waiting {wait_time} seconds...")
                time.sleep(wait_time)
                continue
                
            else:
                print(f"   ❌ API request failed with status {response.status_code}")
                print(f"   📋 Response: {response.text[:200]}...")
                
        except requests.RequestException as e:
            print(f"   ❌ Network error: {e}")
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"   ⏳ Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
        
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")
            break
    
    print("   ⚠️  Failed to process with Gemini AI, returning original text")
    return text_content



def get_output_filename(input_file, language, output_dir, source_dir=None):
    """Generate output filename based on input file and language with organized directory structure"""
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    lang_suffix = f"_{language}" if language != "swa+eng" else "_multilang"
    filename = f"{base_name}_extracted{lang_suffix}.md"
    
    # If we have a source directory, create organized subdirectories
    if source_dir:
        # Get the relative path from source directory to the file
        try:
            rel_path = os.path.relpath(os.path.dirname(input_file), source_dir)
            
            # If the file is directly in source_dir, use the source_dir name as subfolder
            if rel_path == '.':
                subfolder = os.path.basename(source_dir.rstrip('/'))
            else:
                # Use the relative path structure
                subfolder = rel_path.replace(os.sep, '_')
            
            # Create organized output directory
            organized_output_dir = os.path.join(output_dir, subfolder)
            
        except (ValueError, OSError):
            # Fallback: use source directory name
            subfolder = os.path.basename(source_dir.rstrip('/'))
            organized_output_dir = os.path.join(output_dir, subfolder)
    else:
        # No source directory provided, use default
        organized_output_dir = output_dir
    
    # Ensure output directory exists
    organized_output_dir = ensure_output_directory(organized_output_dir)
    
    return os.path.join(organized_output_dir, filename)

def get_language_display(lang_code):
    """Convert language code to display name"""
    lang_map = {
        'swa': 'Kiswahili',
        'eng': 'English', 
        'swa+eng': 'Kiswahili + English'
    }
    return lang_map.get(lang_code, lang_code)

def extract_text_from_pdf(pdf_path, language='swa+eng', output_file=None, output_dir=DEFAULT_OUTPUT_DIR, quality='balanced', use_ai_cleaning=True, source_dir=None):
    """
    Extract text from PDF using Tesseract OCR with specified language(s) and format as Markdown
    
    Args:
        pdf_path (str): Path to the PDF file
        language (str): Language code(s) for OCR (swa, eng, or swa+eng)
        output_file (str): Output filename (auto-generated if None)
        output_dir (str): Directory to save the output file
        quality (str): OCR quality setting (fast, balanced, high)
        use_ai_cleaning (bool): Whether to use Gemini AI for cleaning and formatting
        source_dir (str): Source directory for organizing output structure (optional)
    """
    try:
        # Check if PDF file exists
        if not os.path.exists(pdf_path):
            print(f"❌ Error: File '{pdf_path}' not found!")
            return False
        
        # Generate output filename if not provided
        if output_file is None:
            output_file = get_output_filename(pdf_path, language, output_dir, source_dir)
        else:
            # If custom output file is provided, ensure it's in the correct directory
            if not os.path.isabs(output_file):  # If not absolute path
                if source_dir:
                    # Use organized structure even for custom filenames
                    subfolder = os.path.basename(source_dir.rstrip('/'))
                    organized_output_dir = ensure_output_directory(os.path.join(output_dir, subfolder))
                    output_file = os.path.join(organized_output_dir, output_file)
                else:
                    output_dir = ensure_output_directory(output_dir)
                    output_file = os.path.join(output_dir, output_file)
        
        print(f"📄 Processing: {pdf_path}")
        print(f"🌐 Language(s): {get_language_display(language)}")
        print(f"📁 Output directory: {os.path.dirname(output_file)}")
        print(f"💾 Output file: {output_file}")
        print(f"🤖 AI cleaning: {'Enabled' if use_ai_cleaning else 'Disabled'}")
        print()
        
        print("Converting PDF to images...")
        print("This may take a while depending on the PDF size...")
        
        # Set DPI based on quality setting
        dpi_settings = {'fast': 200, 'balanced': 300, 'high': 400}
        dpi = dpi_settings.get(quality, 300)
        
        print(f"🎯 Quality setting: {quality} (DPI: {dpi})")
        
        # Convert PDF to images
        pages = convert_from_path(pdf_path, dpi=dpi)
        
        # Initialize clean markdown content (no headers or metadata)
        markdown_content = []
        successful_pages = 0
        
        for i, page in enumerate(pages):
            print(f"🔄 Processing page {i+1}/{len(pages)}...")
            
            # Preprocess image for better OCR
            processed_page = preprocess_image(page)
            
            # Extract text with specified language(s)
            try:
                # Use simple OCR configuration (like the working version)
                text = pytesseract.image_to_string(processed_page, lang=language)
                
                # If text is very short and we're using single language, try mixed approach
                if len(text.strip()) < 50 and language in ['swa', 'eng']:
                    print(f"   📝 Short text detected, trying mixed-language approach...")
                    mixed_text = pytesseract.image_to_string(processed_page, lang='swa+eng')
                    if len(mixed_text.strip()) > len(text.strip()):
                        text = mixed_text
                        print(f"   ✅ Mixed-language extraction provided better results")
                
                if text.strip():
                    successful_pages += 1
                    print(f"   ✅ Extracted {len(text.strip())} characters")
                else:
                    print(f"   ⚠️  No text found on this page")
                
            except Exception as lang_error:
                print(f"⚠️  OCR error on page {i+1}: {lang_error}")
                
                # Try different fallback strategies (like the working version)
                fallback_langs = ['swa+eng', 'eng', 'swa']
                text = ""
                
                for fallback in fallback_langs:
                    if fallback != language:  # Don't repeat the same language
                        try:
                            print(f"   🔄 Trying fallback: {get_language_display(fallback)}")
                            text = pytesseract.image_to_string(processed_page, lang=fallback)
                            if text.strip():  # If we got some text, break
                                print(f"   ✅ Fallback successful with {get_language_display(fallback)}")
                                successful_pages += 1
                                break
                        except:
                            continue
                
                if not text.strip():
                    print(f"   ⚠️  All extraction methods failed for page {i+1}")
                    text = ""  # Keep empty instead of error message
            
            # Clean up the text and add to content (no page headers)
            if text.strip():  # Only add if there's actual content
                cleaned_text = clean_and_format_text(text)
                if cleaned_text.strip():
                    markdown_content.append(cleaned_text + "\n\n")
        
        print(f"\n📊 Processing complete: {successful_pages}/{len(pages)} pages successfully processed")
        
        # Combine all content
        raw_content = ''.join(markdown_content).strip()
        
        # Process with Gemini AI if enabled
        if use_ai_cleaning and raw_content:
            print(f"\n🤖 AI Processing Stage...")
            print("="*50)
            final_content = send_to_gemini_ai(raw_content)
            
            # Save AI-processed version with different suffix
            if final_content != raw_content:
                ai_output_file = output_file.replace('.md', '_ai_cleaned.md')
                print(f"💾 Saving AI-cleaned version to: {ai_output_file}")
                
                with open(ai_output_file, 'w', encoding='utf-8') as f:
                    f.write(final_content)
                
                # Also save the raw OCR version for comparison
                raw_output_file = output_file.replace('.md', '_raw_ocr.md')
                print(f"💾 Saving raw OCR version to: {raw_output_file}")
                
                with open(raw_output_file, 'w', encoding='utf-8') as f:
                    f.write(raw_content)
                
                # Use AI-cleaned version as the main output
                output_file = ai_output_file
            else:
                final_content = raw_content
        else:
            final_content = raw_content
        
        # Save final extracted text to markdown file
        print(f"\n💾 Saving final text to {output_file}...")
        
        if final_content:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(final_content)
        else:
            print("⚠️  No text content extracted from the PDF")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("No text content could be extracted from this PDF.")
            return False
        
        print(f"✅ Markdown text extraction completed successfully!")
        print(f"📄 Output saved to: {output_file}")
        print(f"📊 Total pages processed: {len(pages)}")
        
        # Show first few lines as preview
        print("\n" + "="*60)
        print("PREVIEW (first 15 lines):")
        print("="*60)
        with open(output_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for i, line in enumerate(lines[:15]):
                print(line.rstrip())
                if i == 14 and len(lines) > 15:
                    print("... (truncated)")
        
        return True
        
    except ImportError as e:
        print("❌ Missing required packages!")
        print("Please install required packages:")
        print("sudo apt install poppler-utils")
        print("pip install pdf2image pytesseract")
        return False
        
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        return False

def check_tesseract_setup():
    """Check if Tesseract and required languages are available"""
    try:
        version = pytesseract.get_tesseract_version()
        print(f"✅ Tesseract OCR found (version {version})")
    except:
        print("❌ Tesseract OCR not found!")
        print("Please install: sudo apt install tesseract-ocr")
        return False
    
    # Check available languages
    try:
        langs = pytesseract.get_languages()
        
        # Check for Swahili
        if 'swa' in langs:
            print("✅ Swahili language pack found")
        else:
            print("⚠️  Swahili language pack not found!")
            print("Install it with: sudo apt install tesseract-ocr-swa")
        
        # Check for English (usually included by default)
        if 'eng' in langs:
            print("✅ English language pack found")
        else:
            print("⚠️  English language pack not found!")
            print("Install it with: sudo apt install tesseract-ocr-eng")
            
        print(f"📋 Available languages: {', '.join(sorted(langs))}")
        
    except Exception as e:
        print(f"⚠️  Could not check language packs: {e}")
    
    return True

def find_pdf_files(directory):
    """Find all PDF files in a directory and subdirectories"""
    pdf_files = []
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_files.append(os.path.join(root, file))
    
    return pdf_files

def process_directory(directory, language='swa+eng', output_dir=DEFAULT_OUTPUT_DIR, quality='balanced', use_ai_cleaning=True):
    """Process all PDF files in a directory with organized output structure"""
    print(f"\n🔍 Searching for PDF files in: {directory}")
    
    pdf_files = find_pdf_files(directory)
    
    if not pdf_files:
        print(f"📭 No PDF files found in: {directory}")
        return
    
    print(f"📚 Found {len(pdf_files)} PDF files")
    
    # Organize output by source directory
    source_dir_name = os.path.basename(directory.rstrip('/'))
    organized_output_dir = os.path.join(output_dir, source_dir_name)
    
    print(f"📁 Files will be organized in: {organized_output_dir}")
    
    successful = 0
    failed = 0
    
    for i, pdf_file in enumerate(pdf_files, 1):
        try:
            print(f"\n{'='*60}")
            print(f"📄 Processing file {i}/{len(pdf_files)}: {os.path.basename(pdf_file)}")
            print(f"{'='*60}")
            
            if extract_text_from_pdf(pdf_file, language, None, output_dir, quality, use_ai_cleaning, directory):
                successful += 1
                print(f"✅ Successfully processed: {os.path.basename(pdf_file)}")
            else:
                failed += 1
                print(f"❌ Failed to process: {os.path.basename(pdf_file)}")
                
        except KeyboardInterrupt:
            print(f"\n⏹️ Processing interrupted by user")
            break
        except Exception as e:
            print(f"❌ Unexpected error processing {pdf_file}: {e}")
            failed += 1
    
    print(f"\n📊 PROCESSING SUMMARY")
    print("=" * 40)
    print(f"✅ Successfully processed: {successful} files")
    print(f"❌ Failed: {failed} files")
    print(f"📁 Output directory: {organized_output_dir}")
    
    if successful > 0:
        print(f"\n💡 Next steps:")
        print(f"   📖 View processed files: ls -la {organized_output_dir}/")
        print(f"   🧠 Generate questions: python question_generator.py -d {organized_output_dir}")
        print(f"   🔍 Count files: find {organized_output_dir} -name '*.md' | wc -l")

def main():
    parser = argparse.ArgumentParser(
        description='Extract text from PDF files using OCR with Swahili and English support',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  python3 Scan.py document.pdf                           # Process single file
  python3 Scan.py -f document.pdf                        # Process single file (explicit)
  python3 Scan.py -d /path/to/pdfs/                      # Process entire directory
  python3 Scan.py document.pdf -l swa+eng               # Explicit mixed-language mode with AI
  python3 Scan.py document.pdf -l swa                   # Swahili only with AI cleaning
  python3 Scan.py document.pdf -l eng                   # English only with AI cleaning
  python3 Scan.py document.pdf -o custom.md             # Custom output filename
  python3 Scan.py document.pdf --output-dir /custom/path # Custom output directory
  python3 Scan.py document.pdf --no-ai                  # Disable AI cleaning (raw OCR only)
  python3 Scan.py -d /path/to/pdfs/ --list              # List PDF files without processing

Environment Variables:
  GEMINI_API_KEY    Your Google Gemini API key for AI cleaning

Default output directory: {DEFAULT_OUTPUT_DIR}
        """
    )
    
    parser.add_argument('pdf_file', nargs='?', 
                       help='PDF file to process (optional if using --directory)')
    parser.add_argument('-f', '--file', 
                       help='PDF file to process (alternative to positional argument)')
    parser.add_argument('-d', '--directory', 
                       help='Process all PDF files in directory (recursive)')
    parser.add_argument('-l', '--language', 
                       choices=['swa', 'eng', 'swa+eng'], 
                       default='swa+eng',
                       help='Language for OCR (default: swa+eng)')
    parser.add_argument('-q', '--quality', 
                       choices=['fast', 'balanced', 'high'], 
                       default='balanced',
                       help='OCR quality vs speed (default: balanced)')
    parser.add_argument('-o', '--output', 
                       help='Output markdown filename (only for single file processing)')
    parser.add_argument('--output-dir', 
                       default=DEFAULT_OUTPUT_DIR,
                       help=f'Output directory (default: {DEFAULT_OUTPUT_DIR})')
    parser.add_argument('--no-ai', 
                       action='store_true',
                       help='Disable Gemini AI cleaning and formatting (use raw OCR output only)')
    parser.add_argument('--api-key', 
                       help='Google Gemini API key (can also be set via GEMINI_API_KEY environment variable)')
    parser.add_argument('--list', 
                       action='store_true',
                       help='List PDF files in directory without processing (use with --directory)')
    
    # If no arguments provided, show help
    if len(sys.argv) == 1:
        print("🔍 PDF Text Extractor with OCR (Swahili + English Support)")
        print("="*70)
        print(f"📁 Default output directory: {DEFAULT_OUTPUT_DIR}")
        print()
        parser.print_help()
        print()
        print("💡 Quick start:")
        print("   Single file: python3 Scan.py your_document.pdf")
        print("   Whole folder: python3 Scan.py -d /path/to/pdf/folder/")
        return
    
    args = parser.parse_args()
    
    # Determine the PDF file or directory to process
    pdf_input = args.pdf_file or args.file
    
    # Validate arguments
    if not pdf_input and not args.directory:
        print("❌ Error: You must specify either a PDF file or a directory to process")
        print("💡 Use 'python3 Scan.py --help' for usage examples")
        return
    
    if pdf_input and args.directory:
        print("❌ Error: Cannot specify both a file and directory. Choose one.")
        return
    
    if args.output and args.directory:
        print("❌ Error: Custom output filename (-o) can only be used with single file processing")
        return
    
    # Set API key if provided via command line
    if args.api_key:
        global GEMINI_API_KEY
        GEMINI_API_KEY = args.api_key
    
    print("🔍 PDF Text Extractor with OCR (Swahili + English Support)")
    print("="*70)
    print(f"📁 Default output directory: {DEFAULT_OUTPUT_DIR}")
    
    # Show AI status
    if not args.no_ai:
        if GEMINI_API_KEY:
            print("🤖 AI cleaning: Enabled (Gemini AI)")
        else:
            print("🤖 AI cleaning: Disabled (no API key found)")
    else:
        print("🤖 AI cleaning: Disabled (--no-ai flag)")
    
    print()
    
    # Check Tesseract setup
    if not check_tesseract_setup():
        return
    
    print()
    
    # Process directory or single file
    use_ai = not args.no_ai and bool(GEMINI_API_KEY)
    
    if args.directory:
        # Directory processing mode
        if not os.path.exists(args.directory):
            print(f"❌ Error: Directory '{args.directory}' not found!")
            return
        
        if args.list:
            # List files only
            pdf_files = find_pdf_files(args.directory)
            print(f"\n📚 PDF files found in {args.directory}:")
            for i, pdf_file in enumerate(pdf_files, 1):
                rel_path = os.path.relpath(pdf_file, args.directory)
                print(f"  {i}. {rel_path}")
            print(f"\nTotal: {len(pdf_files)} PDF files")
            return
        
        # Process all PDFs in directory
        process_directory(args.directory, args.language, args.output_dir, args.quality, use_ai)
    
    else:
        # Single file processing mode
        if not os.path.exists(pdf_input):
            print(f"❌ Error: File '{pdf_input}' not found!")
            return
            
        success = extract_text_from_pdf(pdf_input, args.language, args.output, args.output_dir, args.quality, use_ai)
        
        if success:
            output_file = args.output or get_output_filename(pdf_input, args.language, args.output_dir, None)
            if not os.path.isabs(args.output or ""):
                output_file = os.path.join(ensure_output_directory(args.output_dir), os.path.basename(args.output or get_output_filename(pdf_input, args.language, args.output_dir, None).split('/')[-1]))
            
            print(f"\n🎉 Process completed successfully!")
            print("\n📋 What you can do now:")
            print(f"   📖 View markdown: cat '{output_file}'")
            print(f"   🔍 Search content: grep 'term' '{output_file}'")
            print(f"   📝 Edit file: nano '{output_file}'")
            print(f"   🌐 Convert to HTML: pandoc '{output_file}' -o output.html")
            print(f"   📄 Convert to PDF: pandoc '{output_file}' -o output.pdf")
            print(f"   📝 Convert to Word: pandoc '{output_file}' -o output.docx")

if __name__ == "__main__":
    main()