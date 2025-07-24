#!/usr/bin/env python3
"""
Optimized Main Entry Point for Adobe Hackathon
Implements all performance optimizations and monitoring
"""

import sys
import os
import time
import json
from pathlib import Path
from typing import List, Dict, Any

# Import optimized components
from src.performance_optimizer import FastPDFProcessor, ResourceMonitor
from src.pdf_parser import PDFParser
from src.heading_detector import HeadingDetector
from src.json_formatter import JSONFormatter

def main():
    """
    Optimized main execution with performance monitoring
    """
    if len(sys.argv) != 3:
        print("Usage: python main.py <input_dir> <output_dir>")
        sys.exit(1)
    
    input_dir = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])
    
    # Initialize performance monitoring
    monitor = ResourceMonitor()
    monitor.start_monitoring()
    
    # Validate directories
    if not input_dir.exists():
        print(f"❌ Input directory does not exist: {input_dir}")
        sys.exit(1)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find PDF files
    pdf_files = list(input_dir.glob("*.pdf"))
    if not pdf_files:
        print("⚠️ No PDF files found in input directory")
        return
    
    print(f"🚀 Processing {len(pdf_files)} PDF file(s) with optimizations")
    
    # Initialize optimized processor
    processor = FastPDFProcessor()
    
    # Process each PDF with optimizations
    success_count = 0
    total_pages = 0
    
    for pdf_file in pdf_files:
        try:
            start_time = time.time()
            
            # Stream process for optimal performance
            result = processor.stream_process_pdf(str(pdf_file))
            
            # Write output
            output_file = output_dir / f"{pdf_file.stem}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            elapsed = time.time() - start_time
            pages = len(result.get('outline', [])) or 1  # Estimate pages
            total_pages += pages
            
            print(f"✅ {pdf_file.name}: {elapsed:.2f}s ({pages} pages)")
            success_count += 1
            
            # Quick performance check
            if elapsed > 10 and pages <= 50:
                print(f"⚠️ Performance warning: {elapsed:.2f}s for {pages} pages")
            
        except Exception as e:
            print(f"❌ Error processing {pdf_file.name}: {e}")
    
    # Performance report
    performance_report = monitor.get_performance_report()
    performance_report['pages_processed'] = total_pages
    
    print(f"\n🎯 Processing Complete:")
    print(f"   ✅ Success: {success_count}/{len(pdf_files)} files")
    print(f"   📊 Total pages: {total_pages}")
    print(f"   ⏱️ Total time: {performance_report['elapsed_time']:.2f}s")
    print(f"   💾 Peak memory: {performance_report['peak_memory_mb']:.1f} MB")
    print(f"   🏃 Avg time/page: {performance_report['time_per_page']:.3f}s")
    
    # Compliance check
    if performance_report['memory_compliant'] and performance_report['time_per_page'] < 0.2:
        print("✅ Performance constraints satisfied!")
    else:
        print("⚠️ Performance constraints may be violated")

if __name__ == "__main__":
    main()
