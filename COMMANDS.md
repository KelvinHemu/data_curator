## Commands Reference

A concise list of runnable commands in this repository.

### OCR Text Extractor — `scan.py`
Extracts text from PDFs via Tesseract OCR, optionally cleaned by Gemini AI, and saves Markdown.

Usage examples:

```bash
# Single PDF (positional)
python scan.py document.pdf

# Single PDF (explicit flag)
python scan.py -f document.pdf

# Process an entire directory (recursive)
python scan.py -d /path/to/pdfs

# Language selection
python scan.py document.pdf -l swa+eng   # mixed (default)
python scan.py document.pdf -l swa       # Swahili only
python scan.py document.pdf -l eng       # English only

# Quality selection
python scan.py document.pdf -q fast      # faster, lower DPI
python scan.py document.pdf -q balanced  # default
python scan.py document.pdf -q high      # slower, higher DPI

# Output controls
python scan.py document.pdf -o custom.md                  # custom filename
python scan.py document.pdf --output-dir Markdown         # custom directory

# Disable AI cleaning
python scan.py document.pdf --no-ai

# List PDF files under a directory (no processing)
python scan.py -d /path/to/pdfs --list
```

Options:
- `pdf_file` (positional): PDF to process (omit when using `--directory`)
- `-f, --file`: PDF file to process (alternative to positional)
- `-d, --directory`: Process all PDFs within a directory (recursive)
- `-l, --language {swa, eng, swa+eng}`: OCR language (default: `swa+eng`)
- `-q, --quality {fast, balanced, high}`: OCR quality vs speed (default: `balanced`)
- `-o, --output`: Output markdown filename (single-file mode only)
- `--output-dir`: Output directory (default comes from config; typically `Markdown`)
- `--no-ai`: Disable Gemini AI cleaning/formatting
- `--api-key`: Override API key for this run
- `--list`: List PDFs in the provided directory without processing

Environment:
- `GEMINI_API_KEY`: Gemini API key (overrides config fallback)

---

### Maktaba Tetea Scraper — `Test/tetea_scraper.py`
Scrapes exam PDFs from Maktaba Tetea, verifies they are exam papers, OCRs them using `scan.py` logic, and saves Markdown under `tetea_exam_papers/<level>/<subject>/`.

Usage:

```bash
python Test/tetea_scraper.py
```

Notes:
- Requires Tesseract OCR and Swahili/English language packs installed
- Imports OCR from `Scan.py`; ensure OCR extraction works locally first
- Targets Form 1–4 levels and filters likely exam PDFs
- Output is markdown-only (no PDFs saved)

---

### AI Question Generator — `question_generator.py`
Generates AI-created study questions from existing exam Markdown files.

Usage examples:

```bash
# Process a single markdown file
python question_generator.py --file path/to/exam.md

# Process all exam files in a directory (default dir if omitted)
python question_generator.py --directory tetea_exam_papers

# Choose output directory for generated questions
python question_generator.py --directory tetea_exam_papers --output out/questions

# List available exam files without processing
python question_generator.py --directory tetea_exam_papers --list
```

Options:
- `-f, --file`: Single markdown file to process
- `-d, --directory`: Directory containing exam markdown files (default per config)
- `-o, --output`: Output directory for generated question files
- `-l, --list`: List available exam files without processing

Environment:
- `GEMINI_API_KEY`: Gemini API key used by the generator

---

### Utilities and Tests
Quick commands to verify API connectivity and helper flows.

```bash
# Test Gemini API connectivity for OCR cleaner
python Test/test_api.py

# Test Gemini API connectivity and sample question generation
python Test/test_question_api.py

# Scrape Maktaba Tetea and OCR to markdown (depends on OCR setup)
python Test/tetea_scraper.py

# Test question generation on existing markdown files (requires unified_pipeline + data)
python Test/test_pipeline_questions.py
```

Notes:
- Some test utilities depend on the presence of prior outputs or additional modules referenced in comments/docstrings. If a command references a missing module, consult `README.md` and the code for setup details.
