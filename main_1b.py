#!/usr/bin/env python3
"""
Round 1B Main Entry Point - Persona-Driven Document Intelligence
Processes document collections with persona and job context
"""

import sys
import os
import json
from pathlib import Path
from typing import List, Dict, Any

from src.persona_intelligence import PersonaIntelligenceEngine

def load_input_specification(spec_file: str) -> Dict[str, Any]:
    """Load input specification (documents, persona, job)"""
    try:
        with open(spec_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Failed to load specification: {e}")
        return {}

def main():
    """
    Main execution for Round 1B
    Expected input: JSON file with documents, persona, and job specification
    """
    if len(sys.argv) != 3:
        print("Usage: python main_1b.py <input_spec.json> <output_dir>")
        sys.exit(1)
    
    spec_file = sys.argv[1]
    output_dir = Path(sys.argv[2])
    
    # Load input specification
    spec = load_input_specification(spec_file)
    if not spec:
        sys.exit(1)
    
    # Extract parameters
    pdf_paths = spec.get("documents", [])
    persona = spec.get("persona", "")
    job_to_be_done = spec.get("job_to_be_done", "")
    
    if not pdf_paths or not persona or not job_to_be_done:
        print("❌ Invalid specification: missing documents, persona, or job_to_be_done")
        sys.exit(1)
    
    # Validate PDF files exist
    valid_pdfs = []
    for pdf_path in pdf_paths:
        if os.path.exists(pdf_path):
            valid_pdfs.append(pdf_path)
        else:
            print(f"⚠️ PDF not found: {pdf_path}")
    
    if not valid_pdfs:
        print("❌ No valid PDF files found")
        sys.exit(1)
    
    print(f"🚀 Starting Round 1B Analysis")
    print(f"📄 Documents: {len(valid_pdfs)}")
    print(f"👤 Persona: {persona}")
    print(f"🎯 Job: {job_to_be_done}")
    
    # Initialize intelligence engine
    engine = PersonaIntelligenceEngine()
    
    # Perform analysis
    try:
        result = engine.analyze_document_collection(
            valid_pdfs, persona, job_to_be_done
        )
        
        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save result
        output_file = output_dir / "challenge1b_output.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Analysis complete: {output_file}")
        print(f"📊 Extracted {len(result['extracted_sections'])} sections")
        print(f"🔍 Analyzed {len(result['subsection_analysis'])} subsections")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()