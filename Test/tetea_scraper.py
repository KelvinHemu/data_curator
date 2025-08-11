#!/usr/bin/env python3
"""
Comprehensive PDF Scraper for Maktaba Tetea
Downloads exam papers and organizes them by subject across all education levels
"""

import os
import requests
import tempfile
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from PyPDF2 import PdfReader

# Import OCR functionality from Scan.py
try:
    from Scan import extract_text_from_pdf, check_tesseract_setup
    OCR_AVAILABLE = True
    print("✅ OCR functionality imported from Scan.py")
except ImportError:
    OCR_AVAILABLE = False
    print("⚠️ Could not import OCR functionality from Scan.py")

# Base configuration
BASE_URL = "https://maktaba.tetea.org"
RESOURCE_PATH = "/resources/"

# Education levels to scrape (excluding Standard 1-7 - primary levels, focusing on Form 1-4 only)
EDUCATION_LEVELS = [
    "form-1-2",
    "form-3-4"
]

# Valid file extensions
VALID_EXTENSIONS = [".pdf"]

# Keywords to identify exam papers
EXAM_KEYWORDS = [
    "exam", "mtihani", "mock", "necta", "psle", "csee", "acsee", "ftna", 
    "paper", "karatasi", "test", "trial", "maswali", "question"
]

# Keywords to exclude non-exam content
EXCLUDE_KEYWORDS = [
    "syllabus", "scheme", "notes", "lesson", "ratiba", "mfumo", "maelezo"
]

# Subject mapping for better organization
SUBJECT_MAPPING = {
    # Mathematics subjects
    "mathematics": ["mathematics", "math", "hisabati", "hesabu"],
    "basic_mathematics": ["basic maths", "basic mathematics"],
    "advanced_mathematics": ["advanced mathematics", "advanced math"],
    "basic_applied_mathematics": ["basic applied math", "basic applied mathematics", "bam"],
    
    # Languages
    "kiswahili": ["kiswahili", "swahili"],
    "english": ["english", "kiingereza", "lugha ya kiingereza"],
    "arabic": ["arabic", "kiarabu"],
    "french": ["french", "kifaransa", "francais"],
    
    # Sciences
    "physics": ["physics", "fizikia"],
    "chemistry": ["chemistry", "kemia"],
    "biology": ["biology", "biolojia", "mazingira"],
    "geography": ["geography", "jiografia"],
    "science": ["science", "sayansi"],
    "science_and_technology": ["science and technology", "sayansi na teknolojia"],
    
    # Social subjects
    "history": ["history", "historia"],
    "civics": ["civics", "uraia", "uraia na maadili", "civic and moral education"],
    "social_studies": ["social studies", "maarifa ya jamii"],
    "social_studies_and_vocational": ["social studies and vocational skills", "maarifa ya jamii na stadi za kazi"],
    "religious_studies": ["bible knowledge", "islamic knowledge", "dini", "dini ya kiislamu", "islamic religion"],
    "islamic_knowledge": ["islamic knowledge", "islamic studies"],
    "divinity": ["divinity", "theology"],
    "general_studies": ["general studies"],
    
    # Education and General
    "basic_education": ["basic education", "elimu ya msingi"],
    "education": ["education", "elimu"],
    
    # Arts and Skills
    "art": ["art", "sanaa", "sanaa na ufundi"],
    "fine_arts": ["fine arts", "fine art"],
    "music": ["music", "muziki"],
    "physical_education": ["physical education", "michezo", "sports"],
    "vocational_skills": ["vocational", "stadi za kazi", "vocational skills"],
    
    # Technology and Business
    "computer_studies": ["computer", "kompyuta", "ict", "teknolojia ya habari na mawasiliano", "information and communication technology", "information & communication technology"],
    "computer_science": ["computer science"],
    "information_computer_studies": ["information & computer studies", "information and computer studies"],
    "bookkeeping": ["bookkeeping", "uwongozi", "uhifadhi"],
    "accountancy": ["accountancy", "accounting"],
    "commerce": ["commerce", "biashara"],
    "economics": ["economics", "uchumi"],
    
    # Specialized subjects
    "agriculture": ["agriculture", "kilimo"],
    "food_nutrition": ["food & nutrition", "food and nutrition", "nutrition"],
}

DOWNLOAD_DIR = "tetea_exam_papers"
OUTPUT_FORMAT = "markdown"  # Store as markdown files instead of PDFs
LANGUAGE = "swa+eng"  # OCR language setting
QUALITY = "balanced"  # OCR quality setting
USE_AI_CLEANING = True  # Use Gemini AI for cleaning extracted text

def clean_filename(filename):
    """Clean filename to be filesystem-safe"""
    # Remove or replace invalid characters
    cleaned = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove multiple spaces and replace with single underscore
    cleaned = re.sub(r'\s+', '_', cleaned)
    # Remove leading/trailing underscores and dots
    cleaned = cleaned.strip('_.')
    return cleaned

def identify_subject(text):
    """Identify subject from text content"""
    text_lower = text.lower()
    
    for subject, keywords in SUBJECT_MAPPING.items():
        if any(keyword in text_lower for keyword in keywords):
            return subject
    
    # Try to extract subject from first word if no match found
    words = text.split()
    if words:
        first_word = words[0].lower()
        return clean_filename(first_word)
    
    return "miscellaneous"

def is_exam_paper(pdf_path):
    """Check if PDF is an exam paper by analyzing content"""
    try:
        reader = PdfReader(pdf_path)
        content = ""
        
        # Read first 2-3 pages to get enough context
        pages_to_check = min(3, len(reader.pages))
        for i in range(pages_to_check):
            page_text = reader.pages[i].extract_text()
            if page_text:
                content += page_text.lower()
        
        # Check for exclusion keywords first
        if any(exclude_word in content for exclude_word in EXCLUDE_KEYWORDS):
            return False
        
        # Check for exam keywords
        if any(exam_word in content for exam_word in EXAM_KEYWORDS):
            return True
        
        # Additional heuristics for exam papers
        exam_patterns = [
            r'time\s*:\s*\d+\s*(hour|minute)',  # Time allocation
            r'marks\s*:\s*\d+',                 # Marks allocation
            r'alama\s*:\s*\d+',                 # Marks in Swahili
            r'section\s*[a-z]',                 # Section divisions
            r'sehemu\s*[a-z]',                  # Sections in Swahili
            r'question\s*\d+',                  # Question numbers
            r'swali\s*\d+',                     # Questions in Swahili
        ]
        
        for pattern in exam_patterns:
            if re.search(pattern, content):
                return True
                
        return False
        
    except Exception as e:
        print(f"⚠️ Error analyzing PDF: {e}")
        return False

def download_and_process_pdf(url, link_text, education_level):
    """Download PDF, verify it's an exam paper, process with OCR, and save ONLY as markdown (NO PDF FALLBACK)"""
    try:
        print(f"📥 Downloading: {link_text}")
        
        # PRE-FILTER: Check filename before downloading
        filename_lower = link_text.lower()
        filename_exclusions = [
            'syllabus', 'curriculum', 'scheme', 'solution', 'answer', 'marking',
            'guide', 'notes', 'lesson', 'teaching', 'mwongozo', 'maelekezo'
        ]
        
        if any(exclude in filename_lower for exclude in filename_exclusions):
            print(f"🚫 Pre-filtered (filename): {link_text}")
            return False
        
        # Check if OCR is available - if not, skip entirely
        if not OCR_AVAILABLE:
            print(f"⚠️ OCR not available, skipping: {link_text}")
            return False
        
        # Download PDF to temporary file
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(response.content)
            temp_path = temp_file.name
        
        # Check if it's an exam paper
        if not is_exam_paper(temp_path):
            os.remove(temp_path)
            print(f"🗑️ Skipped (not an exam paper): {link_text}")
            return False
        
        # Identify subject from link text and PDF content
        subject = identify_subject(link_text)
        
        # If we can't identify subject from filename, try to identify from PDF content
        if subject == "miscellaneous":
            try:
                reader = PdfReader(temp_path)
                content = ""
                for page in reader.pages[:2]:
                    page_text = page.extract_text()
                    if page_text:
                        content += page_text.lower()
                subject = identify_subject(content)
            except:
                pass
        
        # Create directory structure: base_dir/education_level/subject/
        level_dir = os.path.join(DOWNLOAD_DIR, education_level)
        subject_dir = os.path.join(level_dir, subject)
        os.makedirs(subject_dir, exist_ok=True)
        
        # Create clean filename for markdown output
        clean_name = clean_filename(link_text)
        markdown_filename = f"{clean_name}.md"
        
        # Ensure unique filename
        final_path = os.path.join(subject_dir, markdown_filename)
        counter = 1
        while os.path.exists(final_path):
            name_without_ext = os.path.splitext(markdown_filename)[0]
            final_path = os.path.join(subject_dir, f"{name_without_ext}_{counter}.md")
            counter += 1
        
        # Process PDF with OCR - MANDATORY (no fallback to PDF)
        print(f"🔍 Processing with OCR: {link_text}")
        print(f"📂 Target directory: {subject_dir}")
        print(f"📝 Target file: {final_path}")
        
        try:
            # Process with OCR
            success = extract_text_from_pdf(
                pdf_path=temp_path,
                language=LANGUAGE,
                output_file=os.path.basename(final_path),  # Just filename, not full path
                output_dir=subject_dir,  # Directory only
                quality=QUALITY,
                use_ai_cleaning=USE_AI_CLEANING
            )
            
            # Clean up temporary PDF file regardless of success
            os.remove(temp_path)
            
            if success:
                print(f"✅ OCR processed and saved: {final_path}")
                return True
            else:
                print(f"❌ OCR processing failed, file discarded: {link_text}")
                return False
                
        except Exception as ocr_error:
            print(f"❌ OCR error: {ocr_error}")
            print(f"❌ File discarded: {link_text}")
            # Clean up temporary PDF file
            os.remove(temp_path)
            return False
        
    except Exception as e:
        print(f"❌ Error processing {url}: {e}")
        # Clean up temp file if it exists
        try:
            if 'temp_path' in locals():
                os.remove(temp_path)
        except:
            pass
        return False

def print_summary_report(stats):
    """Print summary report showing only markdown files"""
    print(f"\n📊 DOWNLOAD SUMMARY")
    print("=" * 50)
    
    total_markdown = 0
    total_failed = 0
    
    for level, subjects in stats.items():
        if subjects:
            print(f"\n📘 {level.upper().replace('_', '-')}:")
            level_markdown = 0
            level_failed = 0
            
            for subject, counts in subjects.items():
                markdown_count = counts.get('markdown', 0)
                failed_count = counts.get('failed', 0)
                
                if markdown_count > 0 or failed_count > 0:
                    print(f"  📚 {subject}: {markdown_count} markdown files ({'✅ success' if markdown_count > 0 else '❌ failed'})")
                    level_markdown += markdown_count
                    level_failed += failed_count
            
            print(f"  📊 Level total: {level_markdown} markdown files, {level_failed} failed")
            total_markdown += level_markdown
            total_failed += level_failed
    
    print(f"\n🎯 Total successful: {total_markdown} markdown files")
    print(f"❌ Total failed: {total_failed} files")
    print(f"📁 Files organized in: {os.path.abspath(DOWNLOAD_DIR)}")
    
    if total_markdown + total_failed > 0:
        success_rate = (total_markdown / (total_markdown + total_failed)) * 100
        print(f"🎯 OCR processing success rate: {success_rate:.1f}%")
    else:
        print(f"🎯 OCR processing success rate: 0.0%")

def scrape_education_level(level_slug):
    """Scrape all PDFs from a specific education level page (MARKDOWN ONLY)"""
    page_url = urljoin(BASE_URL, f"{RESOURCE_PATH}{level_slug}/")
    print(f"\n🌐 Scraping {level_slug}: {page_url}")
    
    try:
        response = requests.get(page_url, timeout=30)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Failed to load page {page_url}: {e}")
        return
    
    soup = BeautifulSoup(response.content, 'html.parser')
    pdf_links = []
    
    # Find all links to PDF files
    for link in soup.find_all('a', href=True):
        href = link['href']
        link_text = link.get_text(strip=True)
        
        # Check if it's a PDF link
        if any(href.lower().endswith(ext) for ext in VALID_EXTENSIONS):
            full_url = urljoin(page_url, href)
            pdf_links.append((full_url, link_text))
    
    print(f"📄 Found {len(pdf_links)} PDF files")
    
    if not OCR_AVAILABLE:
        print(f"⚠️ OCR not available - all files will be skipped")
        return
    
    # Process each PDF link with OCR (markdown only)
    processed_count = 0
    failed_count = 0
    
    for url, text in pdf_links:
        success = download_and_process_pdf(url, text, level_slug.replace('-', '_'))
        if success:
            processed_count += 1
        else:
            failed_count += 1
    
    print(f"📊 Successfully processed: {processed_count} markdown files")
    print(f"❌ Failed/Skipped: {failed_count} files")

# Update the main function to track stats properly
def main():
    """Main scraping function (MARKDOWN ONLY MODE)"""
    print("🚀 Starting Maktaba Tetea PDF Scraper (MARKDOWN ONLY)")
    print("=" * 50)
    
    if not OCR_AVAILABLE:
        print("❌ ERROR: OCR functionality not available!")
        print("   The scraper requires Scan.py to be working properly.")
        print("   Please ensure Tesseract and all dependencies are installed.")
        return
    
    # Check Tesseract setup
    print("🔧 Checking Tesseract setup...")
    if hasattr(check_tesseract_setup, '__call__'):
        try:
            check_tesseract_setup()
        except:
            print("⚠️ Tesseract setup check failed, but continuing...")
    
    print(f"📁 Output directory: {DOWNLOAD_DIR}")
    print(f"🌍 Language: {LANGUAGE}")
    print(f"🎯 Quality: {QUALITY}")
    print(f"🤖 AI Cleaning: {'Enabled' if USE_AI_CLEANING else 'Disabled'}")
    print(f"📝 Output format: MARKDOWN ONLY")
    
    try:
        # Create base download directory
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        
        # Scrape each education level
        for level in EDUCATION_LEVELS:
            scrape_education_level(level)
        
    except KeyboardInterrupt:
        print("\n⏹️ Scraping interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during scraping: {e}")
    
    print(f"\n🎉 Scraping completed!")
    print(f"📁 All markdown files saved in: {os.path.abspath(DOWNLOAD_DIR)}")

if __name__ == "__main__":
    main()
