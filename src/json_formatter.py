"""
JSON Output Formatter - Creates structured outline JSON
Ensures compliance with competition requirements
"""

import json
from typing import List, Dict, Any
from datetime import datetime

class JSONFormatter:
    """
    Formats heading detection results into required JSON schema
    """
    
    def __init__(self):
        """Initialize formatter with validation schemas"""
        self.required_fields = ["level", "text", "page"]
        self.valid_levels = ["H1", "H2", "H3"]
    
    def create_outline_json(self, title: str, headings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create final JSON output according to competition schema
        
        Args:
            title: Document title
            headings: List of detected headings
            
        Returns:
            Dictionary matching required JSON format
        """
        # Validate and clean headings
        validated_headings = self._validate_headings(headings)
        
        # Create output structure
        output = {
            "title": self._clean_title(title),
            "outline": validated_headings
        }
        
        return output
    
    def _validate_headings(self, headings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Validate and clean heading entries
        """
        validated = []
        
        for heading in headings:
            # Check required fields
            if not all(field in heading for field in self.required_fields):
                continue
            
            # Validate level
            level = heading.get("level", "")
            if level not in self.valid_levels:
                continue
            
            # Clean and validate text
            text = self._clean_text(heading.get("text", ""))
            if not text or len(text) < 3:
                continue
            
            # Validate page number
            try:
                page = int(heading.get("page", 1))
                if page < 1:
                    page = 1
            except (ValueError, TypeError):
                page = 1
            
            validated.append({
                "level": level,
                "text": text,
                "page": page
            })
        
        return validated
    
    def _clean_title(self, title: str) -> str:
        """Clean and validate document title"""
        if not title or not isinstance(title, str):
            return "Untitled Document"
        
        # Remove excessive whitespace and newlines
        cleaned = " ".join(title.split())
        
        # Limit length
        if len(cleaned) > 200:
            cleaned = cleaned[:200] + "..."
        
        return cleaned or "Untitled Document"
    
    def _clean_text(self, text: str) -> str:
        """Clean heading text"""
        if not text or not isinstance(text, str):
            return ""
        
        # Remove excessive whitespace and newlines
        cleaned = " ".join(text.split())
        
        # Remove common artifacts
        cleaned = cleaned.replace('\x00', '').replace('\ufffd', '')
        
        # Limit length for headings
        if len(cleaned) > 150:
            cleaned = cleaned[:150] + "..."
        
        return cleaned.strip()
    
    def save_json(self, output_data: Dict[str, Any], filepath: str) -> bool:
        """
        Save JSON output to file with proper formatting
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving JSON: {e}")
            return False