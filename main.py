"""
Adobe Hackathon 2025 - Round 1A: PDF Outline Extractor
Extracts structured outlines (Title + H1/H2/H3) from PDFs
"""

import sys
import os
import time
import json
from pathlib import Path
from typing import List, Dict, Any

from src.pdf_parser import PDFParser
from src.heading_detector import HeadingDetector  
from src.json_formatter import JSONFormatter

def process_single_pdf(input_path: str, output_path: str, 
                      parser: PDFParser, detector: HeadingDetector, 
                      formatter: JSONFormatter) -> bool:
    """Process a single PDF file and generate JSON outline"""
    try:
        start_time = time.time()
        
        # Parse PDF structure
        print(f"Processing: {os.path.basename(input_path)}")
        document_data = parser.extract_text_with_formatting(input_path)
        
        # Detect headings using clustering and heuristics
        title, headings = detector.identify_headings(document_data)
        
        # Format output according to required JSON schema
        output_json = formatter.create_outline_json(title, headings)
        
        # Write output file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_json, f, indent=2, ensure_ascii=False)
            
        elapsed = time.time() - start_time
        print(f"✅ Completed in {elapsed:.2f}s: {os.path.basename(output_path)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error processing {input_path}: {str(e)}")
        return False

def main():
    """Main execution function following Docker requirements"""
    if len(sys.argv) != 3:
        print("Usage: python main.py <input_dir> <output_dir>")
        sys.exit(1)
        
    input_dir = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])
    
    # Validate directories
    if not input_dir.exists():
        print(f"❌ Input directory does not exist: {input_dir}")
        sys.exit(1)
        
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize components
    parser = PDFParser()
    detector = HeadingDetector()
    formatter = JSONFormatter()
    
    # Find all PDF files
    pdf_files = list(input_dir.glob("*.pdf"))
    if not pdf_files:
        print("⚠️  No PDF files found in input directory")
        return
    
    print(f"Found {len(pdf_files)} PDF file(s) to process")
    
    # Process each PDF
    success_count = 0
    for pdf_file in pdf_files:
        output_file = output_dir / f"{pdf_file.stem}.json"
        
        if process_single_pdf(str(pdf_file), str(output_file), 
                            parser, detector, formatter):
            success_count += 1
    
    print(f"\n🎯 Successfully processed {success_count}/{len(pdf_files)} files")

if __name__ == "__main__":
    main()
