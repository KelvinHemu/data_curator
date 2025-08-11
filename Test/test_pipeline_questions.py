#!/usr/bin/env python3
"""
Test the unified pipeline question generation on existing markdown files
"""

import os
import sys

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from unified_pipeline import UnifiedPipeline

def test_question_generation():
    """Test question generation on existing markdown files"""
    
    # Look for existing markdown files
    markdown_files = []
    base_dir = "tetea_exam_papers"
    
    if os.path.exists(base_dir):
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                if file.endswith('.md') and '_ai_questions.md' not in file and '_questions.md' not in file:
                    markdown_files.append(os.path.join(root, file))
    
    if not markdown_files:
        print("❌ No markdown files found to test with")
        print("💡 Run the main scraper first: python3 questions.py")
        return False
    
    print(f"🧪 Testing question generation on {len(markdown_files)} markdown files")
    
    # Initialize pipeline for question generation only
    pipeline = UnifiedPipeline(
        output_dir="test_pipeline_output",
        generate_questions=True
    )
    
    # Setup directories
    pipeline.setup_directories()
    
    # Test on first few files
    test_files = markdown_files[:3]  # Test on first 3 files
    
    for i, markdown_file in enumerate(test_files, 1):
        print(f"\n📄 Test {i}/{len(test_files)}: {os.path.basename(markdown_file)}")
        
        try:
            # Import question generation function
            from question_generator import process_single_file as generate_questions_for_file
            
            success = generate_questions_for_file(markdown_file, pipeline.questions_dir)
            
            if success:
                print(f"✅ Question generation successful")
                pipeline.stats['questions_generated'] += 1
            else:
                print(f"❌ Question generation failed")
                pipeline.stats['questions_failed'] += 1
                
        except Exception as e:
            print(f"❌ Error: {e}")
            pipeline.stats['questions_failed'] += 1
    
    pipeline.print_summary()
    return True

if __name__ == "__main__":
    print("🧪 Unified Pipeline - Question Generation Test")
    print("=" * 50)
    
    test_question_generation()
