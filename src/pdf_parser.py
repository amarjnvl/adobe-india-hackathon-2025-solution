"""
PDF Parser Module - Extracts text with formatting metadata
Optimized for speed and accuracy within competition constraints
"""

import fitz  # PyMuPDF
import pdfplumber
from typing import List, Dict, Any, Tuple, Optional
import logging
from pathlib import Path

class PDFParser:
    """
    Robust PDF parser that extracts text with formatting metadata
    Uses dual-library approach for maximum compatibility
    """
    
    def __init__(self):
        """Initialize parser with optimized settings"""
        self.logger = logging.getLogger(__name__)
        
        # Performance optimization flags
        self.use_ocr = False  # Only enable if no text layer detected
        self.max_pages_preview = 5  # Preview pages to detect text availability
        
    def extract_text_with_formatting(self, pdf_path: str) -> Dict[str, Any]:
        """
        Main extraction method that returns structured document data
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary containing pages with text and formatting metadata
        """
        try:
            # First, determine best extraction strategy
            extraction_method = self._determine_extraction_method(pdf_path)
            
            if extraction_method == "pdfplumber":
                return self._extract_with_pdfplumber(pdf_path)
            elif extraction_method == "fitz":
                return self._extract_with_fitz(pdf_path)
            else:
                # Fallback: try both and merge results
                return self._extract_hybrid_approach(pdf_path)
                
        except Exception as e:
            self.logger.error(f"Failed to extract from {pdf_path}: {e}")
            return self._create_empty_document()
    
    def _determine_extraction_method(self, pdf_path: str) -> str:
        """
        Analyze PDF to choose optimal extraction method
        Prioritizes speed while maintaining accuracy
        """
        try:
            # Quick preview with pdfplumber to check text availability
            with pdfplumber.open(pdf_path) as pdf:
                # Check first few pages for text content
                text_ratio = 0
                preview_pages = min(len(pdf.pages), self.max_pages_preview)
                
                for i in range(preview_pages):
                    page = pdf.pages[i]
                    text = page.extract_text()
                    
                    if text and len(text.strip()) > 50:
                        text_ratio += 1
                
                text_ratio = text_ratio / preview_pages
                
                # Decision logic based on text availability
                if text_ratio > 0.8:
                    return "pdfplumber"  # High text content - use pdfplumber
                elif text_ratio > 0.3:
                    return "fitz"        # Mixed content - use fitz
                else:
                    return "hybrid"      # Low text - need OCR or hybrid
                    
        except Exception:
            return "fitz"  # Safe fallback
    
    def _extract_with_pdfplumber(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract using pdfplumber - best for text-heavy documents
        Provides precise positioning and formatting data
        """
        document_data = {
            "title": "",
            "total_pages": 0,
            "pages": [],
            "extraction_method": "pdfplumber"
        }
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                document_data["total_pages"] = len(pdf.pages)
                
                # Extract title from metadata or first page
                document_data["title"] = self._extract_title_from_metadata(pdf)
                
                # Process each page
                for page_num, page in enumerate(pdf.pages, 1):
                    page_data = self._extract_page_pdfplumber(page, page_num)
                    document_data["pages"].append(page_data)
                    
        except Exception as e:
            self.logger.error(f"pdfplumber extraction failed: {e}")
            return self._create_empty_document()
            
        return document_data
    
    def _extract_page_pdfplumber(self, page, page_num: int) -> Dict[str, Any]:
        """Extract detailed information from a single page using pdfplumber"""
        page_data = {
            "page_number": page_num,
            "text_elements": [],
            "raw_text": "",
            "width": page.width,
            "height": page.height
        }
        
        try:
            # Extract characters with formatting details
            chars = page.chars
            page_data["raw_text"] = page.extract_text()
            
            # Group characters into text elements by font and position
            text_elements = self._group_chars_into_elements(chars)
            page_data["text_elements"] = text_elements
            
        except Exception as e:
            self.logger.warning(f"Page {page_num} extraction partial failure: {e}")
            page_data["raw_text"] = page.extract_text() or ""
            
        return page_data
    
    def _group_chars_into_elements(self, chars: List[Dict]) -> List[Dict[str, Any]]:
        """
        Group individual characters into text elements based on formatting
        This is crucial for heading detection
        """
        if not chars:
            return []
            
        elements = []
        current_element = None
        
        for char in chars:
            # Extract formatting attributes
            font_info = {
                "fontname": char.get("fontname", ""),
                "size": char.get("size", 12),
                "x0": char.get("x0", 0),
                "y0": char.get("y0", 0),
                "x1": char.get("x1", 0),
                "y1": char.get("y1", 0)
            }
            
            # Check if this character continues current element
            if (current_element and 
                self._same_formatting(current_element["font_info"], font_info) and
                self._same_line(current_element["font_info"], font_info)):
                
                # Extend current element
                current_element["text"] += char.get("text", "")
                current_element["font_info"]["x1"] = font_info["x1"]
                
            else:
                # Start new element
                if current_element:
                    elements.append(current_element)
                    
                current_element = {
                    "text": char.get("text", ""),
                    "font_info": font_info.copy()
                }
        
        # Add final element
        if current_element:
            elements.append(current_element)
            
        return elements
    
    def _same_formatting(self, font1: Dict, font2: Dict) -> bool:
        """Check if two font configurations are the same"""
        return (font1["fontname"] == font2["fontname"] and 
                abs(font1["size"] - font2["size"]) < 0.1)
    
    def _same_line(self, font1: Dict, font2: Dict, tolerance: float = 2.0) -> bool:
        """Check if two text elements are on the same line"""
        return abs(font1["y0"] - font2["y0"]) < tolerance
    
    def _extract_with_fitz(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract using PyMuPDF (fitz) - good for complex layouts
        Provides font details and handles various PDF formats
        """
        document_data = {
            "title": "",
            "total_pages": 0,
            "pages": [],
            "extraction_method": "fitz"
        }
        
        try:
            doc = fitz.open(pdf_path)
            document_data["total_pages"] = len(doc)
            
            # Extract title from metadata
            metadata = doc.metadata
            document_data["title"] = metadata.get("title", "") or self._extract_title_from_first_page_fitz(doc)
            
            # Process each page
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_data = self._extract_page_fitz(page, page_num + 1)
                document_data["pages"].append(page_data)
                
            doc.close()
            
        except Exception as e:
            self.logger.error(f"fitz extraction failed: {e}")
            return self._create_empty_document()
            
        return document_data
    
    def _extract_page_fitz(self, page, page_num: int) -> Dict[str, Any]:
        """Extract detailed information from a single page using fitz"""
        page_data = {
            "page_number": page_num,
            "text_elements": [],
            "raw_text": "",
            "width": page.rect.width,
            "height": page.rect.height
        }
        
        try:
            # Get text with formatting details
            blocks = page.get_text("dict")
            page_data["raw_text"] = page.get_text()
            
            # Extract formatted text elements
            text_elements = self._extract_fitz_text_elements(blocks)
            page_data["text_elements"] = text_elements
            
        except Exception as e:
            self.logger.warning(f"Page {page_num} fitz extraction error: {e}")
            page_data["raw_text"] = page.get_text() or ""
            
        return page_data
    
    def _extract_fitz_text_elements(self, blocks: Dict) -> List[Dict[str, Any]]:
        """Extract text elements from fitz text blocks"""
        elements = []
        
        for block in blocks.get("blocks", []):
            if "lines" not in block:
                continue
                
            for line in block["lines"]:
                for span in line.get("spans", []):
                    element = {
                        "text": span.get("text", ""),
                        "font_info": {
                            "fontname": span.get("font", ""),
                            "size": span.get("size", 12),
                            "flags": span.get("flags", 0),  # Bold, italic flags
                            "x0": span.get("bbox", [0])[0] if span.get("bbox") else 0,
                            "y0": span.get("bbox", [0, 0])[1] if span.get("bbox") else 0,
                            "x1": span.get("bbox", [0, 0, 0])[2] if span.get("bbox") else 0,
                            "y1": span.get("bbox", [0, 0, 0, 0])[3] if span.get("bbox") else 0
                        }
                    }
                    
                    if element["text"].strip():  # Only add non-empty elements
                        elements.append(element)
        
        return elements
    
    def _extract_title_from_metadata(self, pdf) -> str:
        """Extract title from PDF metadata"""
        try:
            if hasattr(pdf, 'metadata') and pdf.metadata:
                return pdf.metadata.get('Title', '') or ""
            return ""
        except:
            return ""
    
    def _extract_title_from_first_page_fitz(self, doc) -> str:
        """Fallback: extract likely title from first page"""
        try:
            if len(doc) > 0:
                first_page = doc[0]
                text = first_page.get_text()
                
                # Simple heuristic: first non-empty line might be title
                lines = text.split('\n')
                for line in lines:
                    line = line.strip()
                    if line and len(line) > 5 and len(line) < 200:
                        return line
            return ""
        except:
            return ""
    
    def _extract_hybrid_approach(self, pdf_path: str) -> Dict[str, Any]:
        """
        Hybrid approach: combine both libraries for maximum accuracy
        Used when document has mixed content or extraction challenges
        """
        # Try pdfplumber first, fallback to fitz
        result = self._extract_with_pdfplumber(pdf_path)
        
        if not result["pages"] or not any(page["raw_text"] for page in result["pages"]):
            self.logger.info("Falling back to fitz extraction")
            result = self._extract_with_fitz(pdf_path)
            
        result["extraction_method"] = "hybrid"
        return result
    
    def _create_empty_document(self) -> Dict[str, Any]:
        """Create empty document structure for failed extractions"""
        return {
            "title": "",
            "total_pages": 0,
            "pages": [],
            "extraction_method": "failed"
        }

    def validate_extraction(self, document_data: Dict[str, Any]) -> bool:
        """
        Validate that extraction produced usable results
        Returns False if document appears to be image-only or corrupt
        """
        if not document_data or not document_data.get("pages"):
            return False
            
        # Check if any page has readable text 
        total_text_length = 0
        for page in document_data["pages"]:
            total_text_length += len(page.get("raw_text", ""))
            
        # Require minimum text content (adjust threshold as needed)
        min_text_threshold = 100  # characters
        return total_text_length >= min_text_threshold
