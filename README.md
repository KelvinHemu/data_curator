# PDF Text Extraction Pipeline with Gemini AI

A complete pipeline for extracting text from PDF documents using OCR and cleaning it with Google Gemini AI. Supports Swahili and English languages.

**🔑 Pre-configured with API Key** - Ready to use out of the box!

**🆕 NEW: Unified Pipeline** - Complete PDF to AI Questions workflow! See [Unified Pipeline Guide](README_unified_pipeline.md)

## 🌟 Features

- **OCR Text Extraction**: Extract text from PDF files using Tesseract OCR
- **Multi-language Support**: Swahili, English, or both languages simultaneously
- **AI Cleaning**: Automatic text cleaning and formatting using Google Gemini AI
- **Quality Control**: Multiple quality settings for OCR processing
- **Markdown Output**: Clean, formatted markdown files ready for use
- **Comparison Files**: Saves both raw OCR and AI-cleaned versions for comparison
- **Windows-Friendly**: Includes batch files for easy execution
- **🆕 Unified Pipeline**: Complete PDF → Questions workflow in one command

## 🚀 Quick Start

### Option 1: Unified Pipeline (NEW - Recommended)
Complete PDF to AI Questions workflow:
```bash
# Check dependencies
./tesseract-env/bin/python3 unified_pipeline.py --check-deps

# Process single PDF
./tesseract-env/bin/python3 unified_pipeline.py document.pdf

# Process entire directory
./tesseract-env/bin/python3 unified_pipeline.py folder_with_pdfs/
```
📚 **[Complete Unified Pipeline Guide](README_unified_pipeline.md)**

### Option 2: Individual OCR Processing
Basic text extraction only:

### 1. Test the API Connection
```bash
python test_api.py
```

### 2. Extract text from PDF
```bash
# Windows batch file (easiest)
run_pipeline.bat your_document.pdf

# Direct Python command
python markdown.py document.pdf

# Custom settings
python markdown.py document.pdf -l eng -q high
```

### 3. Check Output
Look for these files in the `Markdown` folder:
- `document_ai_cleaned.md` - AI-processed version
- `document_raw_ocr.md` - Original OCR output
```

## 📋 Usage Examples

```bash
# Windows batch files (recommended for Windows)
run_pipeline.bat exam_paper.pdf                    # Default: Swahili + English
run_pipeline.bat document.pdf eng                  # English only  
run_pipeline.bat document.pdf swa+eng high         # High quality

# Direct Python commands
python markdown.py exam_paper.pdf                  # Swahili + English with AI
python markdown.py document.pdf -l eng -q high     # English only, high quality
python markdown.py document.pdf -l swa --no-ai     # Swahili only, no AI
python markdown.py document.pdf -d custom_output   # Custom output directory
```

## 🔧 Files in This Package

### Core OCR Pipeline
- **`Scan.py`** - Main OCR extraction script (previously `markdown.py`)
- **`config.py`** - Configuration with your API key
- **`test_api.py`** - Test script to verify API connectivity

### 🆕 Unified Pipeline (NEW)
- **`unified_pipeline.py`** - Complete PDF to Questions pipeline
- **`question_generator.py`** - AI question generation from markdown
- **`question_config.py`** - Question generator configuration
- **`test_question_api.py`** - Test Gemini API for questions
- **`run_unified_pipeline.sh`** - Bash script for easy execution

### Additional Tools
- **`questions.py`** - Tetea exam scraper with OCR
- **`setup_pipeline.py`** - Dependency installation script
- **`README_unified_pipeline.md`** - Complete unified pipeline guide
- **`README.md`** - This documentation

## 🔧 Command Line Options

```
positional arguments:
  pdf_file              PDF file to process

options:
  -h, --help            show this help message and exit
  -l {swa,eng,swa+eng}, --language {swa,eng,swa+eng}
                        Language for OCR (default: swa+eng)
  -q {fast,balanced,high}, --quality {fast,balanced,high}
                        OCR quality vs speed (default: balanced)
  -o OUTPUT, --output OUTPUT
                        Output markdown filename (auto-generated if not specified)
  -d DIRECTORY, --directory DIRECTORY
                        Output directory (default: Markdown)
  --no-ai               Disable Gemini AI cleaning and formatting
  --api-key API_KEY     Google Gemini API key (overrides config.py)
```

## 📁 Output Files

### OCR Processing
When AI cleaning is enabled, the pipeline creates:

1. **`document_ai_cleaned.md`** - Final AI-cleaned and formatted version
2. **`document_raw_ocr.md`** - Raw OCR output for comparison
3. **`document_extracted_multilang.md`** - Original filename format (points to AI-cleaned version)

### 🆕 Unified Pipeline Output
Complete pipeline creates organized structure:
```
pipeline_output/
├── markdown_files/     # OCR-extracted text files
└── ai_questions/       # AI-generated question files
```

📚 **[See complete output examples](README_unified_pipeline.md)**

## 🔑 API Key Configuration

✅ **Your API key is already configured in `config.py`!**

The pipeline is pre-configured with your Gemini API key. You can:

1. **Use as-is** - Everything should work out of the box
2. **Change API key** - Edit the `GEMINI_API_KEY` in `config.py`
3. **Use environment variable** - Set `GEMINI_API_KEY` environment variable to override

### Test Your Setup
```bash
python test_api.py
```
This will verify your API key is working correctly.

## 📦 Dependencies

### System Requirements
- **Tesseract OCR**: For text extraction
  - Ubuntu/Debian: `sudo apt install tesseract-ocr tesseract-ocr-swa tesseract-ocr-eng`
  - Windows: Download from [UB-Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
  - macOS: `brew install tesseract tesseract-lang`

### Python Packages
- `pytesseract` - Tesseract OCR wrapper
- `pdf2image` - PDF to image conversion
- `Pillow` - Image processing
- `requests` - HTTP requests for Gemini API

## 🤖 AI Processing

The Gemini AI stage:
1. Fixes OCR errors and typos
2. Improves formatting and structure
3. Ensures proper question numbering
4. Fixes spacing and punctuation
5. Makes multiple choice options clear
6. Preserves original language
7. Removes watermarks and irrelevant content

## 🛠️ Installation

### Quick Setup (Windows)
```bash
# Double-click setup.bat or run:
setup.bat
```

### Manual Setup
```bash
# Install Python packages
pip install pytesseract pdf2image Pillow requests

# Install Tesseract OCR (Windows)
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
# Add to PATH environment variable

# Test the setup
python test_api.py
```

### Alternative Setup
```bash
python install_dependencies.py
```

## 🔍 Quality Settings

- **fast**: 200 DPI, faster processing, lower accuracy
- **balanced**: 300 DPI, good balance of speed and accuracy (default)
- **high**: 400 DPI, slower processing, highest accuracy

## 💡 Tips

1. **For exam papers**: Use default settings (swa+eng with AI cleaning)
2. **For English documents**: Use `-l eng` for better accuracy
3. **For poor quality scans**: Use `-q high` for better OCR
4. **For quick testing**: Use `--no-ai` to skip AI processing
5. **Large files**: Consider splitting PDFs for better processing

## 🐛 Troubleshooting

### OCR Issues
- Install language packs: `sudo apt install tesseract-ocr-swa tesseract-ocr-eng`
- Check Tesseract installation: `tesseract --version`

### API Issues
- Verify API key: Check at https://makersuite.google.com/app/apikey
- Rate limits: The script includes automatic retry with backoff
- Network issues: Check internet connection

### Permission Issues
- Ensure write permissions in output directory
- Use absolute paths when specifying custom directories

## 📊 Output Quality

The pipeline provides quality indicators:
- Number of pages successfully processed
- Character count comparison (before/after AI cleaning)
- Success/failure status for each processing stage

## 🔄 Pipeline Stages

1. **PDF to Images**: Convert PDF pages to images
2. **Image Preprocessing**: Enhance images for better OCR
3. **OCR Extraction**: Extract text using Tesseract
4. **Initial Cleaning**: Basic formatting and cleanup
5. **AI Processing**: Advanced cleaning with Gemini AI
6. **Output Generation**: Save formatted markdown files

## 📝 License

This project is open source. Feel free to modify and distribute.

## 🤝 Contributing

Contributions welcome! Please feel free to submit pull requests or open issues.
