# Question Generator for Tetea Exam Papers

This tool generates intelligent questions from exam markdown files using Google Gemini AI. It's designed to work with the markdown files created by the main Tetea scraper.

## Features

- **Smart Question Generation**: Creates 5-20 questions per exam file using AI
- **Prompt Generation**: Creates reusable prompts for students/teachers
- **Batch Processing**: Can process entire directories of exam files
- **Flexible Output**: Save questions alongside original files or in separate directory
- **Configurable**: Easy configuration through `question_config.py`

## Requirements

- Python 3.6+
- `requests` library
- Google Gemini API key
- Markdown exam files (from the main scraper)

## Installation

1. Ensure you have the required dependencies:
```bash
pip install requests
```

2. Make sure you have exam markdown files (run the main scraper first):
```bash
python questions.py
```

## Usage

### Process all exam files in default directory
```bash
python question_generator.py
```

### Process a specific file
```bash
python question_generator.py --file "tetea_exam_papers/standard_5_7/mathematics/2019_exam.md"
```

### Process files from custom directory
```bash
python question_generator.py --directory "my_exam_files"
```

### Save generated questions to specific output directory
```bash
python question_generator.py --output "generated_questions"
```

### List available exam files without processing
```bash
python question_generator.py --list
```

### Combine options
```bash
python question_generator.py --directory "tetea_exam_papers" --output "ai_questions" --list
```

## Command Line Options

- `--file` or `-f`: Process a single markdown file
- `--directory` or `-d`: Process all exam files in directory (default: tetea_exam_papers)
- `--output` or `-o`: Output directory for generated questions (optional)
- `--list` or `-l`: List available exam files without processing

## Configuration

Edit `question_config.py` to customize:

- **GEMINI_API_KEY**: Your Google Gemini API key
- **GEMINI_MODEL**: AI model to use (default: gemini-2.0-flash)
- **DEFAULT_EXAM_DIR**: Default directory to search for exam files
- **REQUEST_TIMEOUT**: API request timeout in seconds
- **MIN_CONTENT_LENGTH**: Minimum file size to process
- **File naming conventions**: Suffixes for generated files

## Output Format

Generated question files follow this structure:

```markdown
# Maswali ya Mtihani ya AI
*Maswali yametengenezwa na AI kutoka kwa mtihani: original_file.md*

---

1. [Question 1]
2. [Question 2]
...
[5-20 questions total]

Prompt: [A prompt that students/teachers can use to get similar questions]

---
*Maswali haya yametengenezwa kwa kutumia Google Gemini AI kutoka kwenye mtihani halisi.*
```

## Examples

### Example 1: Process Mathematics Files
```bash
# Process all mathematics exam files
python question_generator.py --directory "tetea_exam_papers/standard_5_7/mathematics"
```

### Example 2: Generate Questions for Specific Subject
```bash
# Process English exam and save to custom location
python question_generator.py --file "tetea_exam_papers/form_1_2/english/2020_exam.md" --output "english_questions"
```

## Output Files

- Original exam: `2019_exam.md`
- Generated questions: `2019_exam_ai_questions.md`

## Tips

1. **Large Batches**: For processing many files, the tool automatically handles rate limiting and errors
2. **Quality Control**: Review generated questions - AI output may vary in quality
3. **Backup**: Keep original exam files safe before batch processing
4. **Customization**: Modify the Swahili prompt in the code for different question styles

## Troubleshooting

### Common Issues

1. **API Key Error**: Make sure your Gemini API key is valid in `question_config.py`
2. **No Files Found**: Ensure you've run the main scraper first to create exam files
3. **Network Issues**: Check internet connection for API calls
4. **File Permissions**: Ensure write permissions in output directories

### Error Messages

- `❌ No exam files found`: Run the main scraper first
- `❌ API request failed`: Check API key and internet connection
- `⚠️ File too short`: File doesn't contain enough content to be a valid exam

## Integration with Main Scraper

This tool is designed to work with the main `questions.py` scraper:

1. Run main scraper: `python questions.py`
2. Generate AI questions: `python question_generator.py`
3. Both tools create complementary question files

## API Usage

The tool uses Google Gemini API with these specifications:
- **Model**: gemini-2.0-flash
- **Timeout**: 60 seconds per request
- **Format**: JSON request/response
- **Language**: Supports Swahili and English content

## File Structure After Processing

```
tetea_exam_papers/
├── standard_5_7/
│   ├── mathematics/
│   │   ├── 2019_exam.md                    # Original exam
│   │   ├── 2019_exam_questions.md          # From main scraper
│   │   └── 2019_exam_ai_questions.md       # From this tool
│   └── english/
│       ├── 2020_exam.md
│       ├── 2020_exam_questions.md
│       └── 2020_exam_ai_questions.md
```

## License

This tool is part of the Tetea Exam Paper processing suite.
