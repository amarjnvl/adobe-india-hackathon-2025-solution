"""
Intelligent Heading Detection Module
Uses clustering and heuristic approaches for robust heading identification
Optimized for diverse PDF formats and multilingual content
"""

import numpy as np
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler
from collections import Counter, defaultdict
from typing import List, Dict, Any, Tuple, Optional
import re
import math

class HeadingDetector:
    """
    Advanced heading detection using multi-factor analysis
    Combines font clustering, positional analysis, and content heuristics
    """
    
    def __init__(self):
        """Initialize detector with optimized parameters"""
        self.font_size_threshold = 1.2  # Minimum ratio above median for heading consideration
        self.position_weight = 0.3      # Weight for positional scoring
        self.content_weight = 0.2       # Weight for content pattern scoring
        self.font_weight = 0.5          # Weight for font characteristics
        
        # Multilingual patterns for bonus points
        self.heading_patterns = {
            'english': [
                r'^[A-Z][A-Z\s]{2,}$',  # ALL CAPS headings
                r'^\d+\.?\s+[A-Z]',      # Numbered headings (1. Introduction)
                r'^[IVX]+\.?\s+[A-Z]',   # Roman numerals
                r'^Chapter\s+\d+',       # Chapter headings
                r'^Section\s+\d+'        # Section headings
            ],
            'multilingual': [
                r'^[\u4e00-\u9fff]+',    # Chinese/Japanese characters
                r'^[\u3040-\u309f]+',    # Hiragana
                r'^[\u30a0-\u30ff]+',    # Katakana
                r'^[\u0590-\u05ff]+',    # Hebrew
                r'^[\u0600-\u06ff]+',    # Arabic
            ]
        }
        
    def identify_headings(self, document_data: Dict[str, Any]) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Main method to identify title and hierarchical headings
        
        Args:
            document_data: Structured document data from PDF parser
            
        Returns:
            Tuple of (title, list of heading dictionaries)
        """
        # Extract title using multi-strategy approach
        title = self._extract_document_title(document_data)
        
        # Collect all text elements with formatting
        all_elements = self._collect_text_elements(document_data)
        
        if not all_elements:
            return title, []
        
        # Perform font analysis and clustering
        font_clusters = self._analyze_font_distribution(all_elements)
        
        # Score each element for heading likelihood
        scored_elements = self._score_heading_candidates(all_elements, font_clusters)
        
        # Filter and classify headings by hierarchy
        headings = self._classify_heading_hierarchy(scored_elements)
        
        return title, headings
    
    def _extract_document_title(self, document_data: Dict[str, Any]) -> str:
        """
        Multi-strategy title extraction with fallback mechanisms
        """
        # Strategy 1: Check metadata title
        metadata_title = document_data.get("title", "").strip()
        if metadata_title and len(metadata_title) > 3:
            return metadata_title
        
        # Strategy 2: Analyze first page for title-like content
        if document_data.get("pages"):
            first_page = document_data["pages"][0]
            title_candidate = self._extract_title_from_page(first_page)
            if title_candidate:
                return title_candidate
        
        # Strategy 3: Fallback to "Untitled Document"
        return "Untitled Document"
    
    def _extract_title_from_page(self, page_data: Dict[str, Any]) -> str:
        """
        Extract title from first page using position and font analysis
        """
        elements = page_data.get("text_elements", [])
        if not elements:
            return ""
        
        # Look for elements in top 25% of page
        page_height = page_data.get("height", 792)  # Default PDF height
        top_threshold = page_height * 0.75  # Y coordinates are often inverted
        
        title_candidates = []
        
        for element in elements[:10]:  # Check first 10 elements
            text = element.get("text", "").strip()
            font_info = element.get("font_info", {})
            
            if not text or len(text) < 5:
                continue
            
            # Score based on multiple factors
            score = self._calculate_title_score(text, font_info, page_height)
            
            if score > 0.6:  # Threshold for title consideration
                title_candidates.append((text, score))
        
        # Return highest scoring candidate
        if title_candidates:
            title_candidates.sort(key=lambda x: x[1], reverse=True)
            return title_candidates[0][0]
        
        return ""
    
    def _calculate_title_score(self, text: str, font_info: Dict, page_height: float) -> float:
        """
        Multi-factor scoring for title identification
        """
        score = 0.0
        
        # Font size factor (normalized)
        font_size = font_info.get("size", 12)
        if font_size > 16:
            score += 0.3 * min(font_size / 24.0, 1.0)  # Cap at 24pt
        
        # Position factor (top of page gets higher score)
        y_pos = font_info.get("y0", 0)
        position_score = max(0, (y_pos / page_height) * 0.3)
        score += position_score
        
        # Text characteristics
        if text.isupper() and len(text) > 5:
            score += 0.2  # ALL CAPS titles
        
        if len(text.split()) >= 2 and len(text) < 100:
            score += 0.2  # Reasonable title length
        
        # Bold/weight detection (for PyMuPDF flags)
        flags = font_info.get("flags", 0)
        if flags & 2**4:  # Bold flag
            score += 0.2
        
        return min(score, 1.0)
    
    def _collect_text_elements(self, document_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Collect all text elements with page context for analysis
        """
        all_elements = []
        
        for page in document_data.get("pages", []):
            page_num = page.get("page_number", 1)
            
            for element in page.get("text_elements", []):
                # Add page context to element
                enhanced_element = element.copy()
                enhanced_element["page_number"] = page_num
                enhanced_element["page_height"] = page.get("height", 792)
                enhanced_element["page_width"] = page.get("width", 612)
                
                # Clean and validate text
                text = element.get("text", "").strip()
                if text and len(text) >= 3:  # Minimum text length
                    all_elements.append(enhanced_element)
        
        return all_elements
    
    def _analyze_font_distribution(self, elements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Statistical analysis of font characteristics for clustering[3][6]
        """
        font_sizes = []
        font_names = []
        
        for element in elements:
            font_info = element.get("font_info", {})
            font_sizes.append(font_info.get("size", 12))
            font_names.append(font_info.get("fontname", ""))
        
        font_sizes = np.array(font_sizes)
        
        # Statistical analysis
        analysis = {
            "median_size": np.median(font_sizes),
            "mean_size": np.mean(font_sizes),
            "std_size": np.std(font_sizes),
            "size_distribution": Counter(font_sizes.astype(int)),
            "font_name_counts": Counter(font_names)
        }
        
        # Identify significant font sizes (potential headings)[10]
        significant_sizes = []
        for size, count in analysis["size_distribution"].items():
            if size > analysis["median_size"] * self.font_size_threshold:
                if count >= 2:  # Must appear at least twice
                    significant_sizes.append(size)
        
        analysis["significant_sizes"] = sorted(significant_sizes, reverse=True)
        
        # Clustering approach for font characteristics
        if len(elements) > 10:
            analysis["clusters"] = self._perform_font_clustering(elements)
        else:
            analysis["clusters"] = {"labels": [0] * len(elements), "centers": []}
        
        return analysis
    
    def _perform_font_clustering(self, elements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        K-means clustering of font attributes for heading detection[10][16]
        """
        # Prepare feature vectors
        features = []
        for element in elements:
            font_info = element.get("font_info", {})
            
            feature_vector = [
                font_info.get("size", 12),                    # Font size
                len(element.get("text", "")),                 # Text length
                font_info.get("x0", 0),                       # X position
                font_info.get("y0", 0),                       # Y position
                font_info.get("flags", 0) & 16,              # Bold flag
            ]
            features.append(feature_vector)
        
        features = np.array(features)
        
        # Normalize features
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)
        
        # Perform clustering (3-5 clusters for different heading levels)
        n_clusters = min(5, max(3, len(elements) // 10))
        
        try:
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(features_scaled)
            
            return {
                "labels": cluster_labels.tolist(),
                "centers": kmeans.cluster_centers_.tolist(),
                "n_clusters": n_clusters
            }
        except Exception:
            # Fallback to simple grouping
            return {"labels": [0] * len(elements), "centers": []}
    
    def _score_heading_candidates(self, elements: List[Dict[str, Any]], 
                                font_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Score each text element for heading likelihood using multi-factor approach[8]
        """
        scored_elements = []
        median_size = font_analysis.get("median_size", 12)
        significant_sizes = font_analysis.get("significant_sizes", [])
        
        for i, element in enumerate(elements):
            text = element.get("text", "")
            font_info = element.get("font_info", {})
            
            # Calculate comprehensive heading score
            score = self._calculate_heading_score(
                element, font_info, median_size, significant_sizes, font_analysis
            )
            
            if score > 0.3:  # Threshold for heading consideration
                scored_element = element.copy()
                scored_element["heading_score"] = score
                scored_element["cluster_id"] = font_analysis.get("clusters", {}).get("labels", [0])[i]
                scored_elements.append(scored_element)
        
        return scored_elements
    
    def _calculate_heading_score(self, element: Dict[str, Any], font_info: Dict[str, Any],
                               median_size: float, significant_sizes: List[float],
                               font_analysis: Dict[str, Any]) -> float:
        """
        Multi-factor heading score calculation
        """
        text = element.get("text", "")
        font_size = font_info.get("size", 12)
        
        # Font size factor
        size_score = 0.0
        if font_size in significant_sizes:
            size_score = min(font_size / (median_size * 2), 1.0) * self.font_weight
        
        # Position factor (left alignment, whitespace)
        position_score = self._calculate_position_score(element, font_info) * self.position_weight
        
        # Content pattern factor (numbering, capitalization, etc.)
        content_score = self._calculate_content_score(text) * self.content_weight
        
        # Bold/formatting factor
        format_score = 0.0
        flags = font_info.get("flags", 0)
        if flags & 16:  # Bold flag in fitz
            format_score = 0.2
        elif "bold" in font_info.get("fontname", "").lower():
            format_score = 0.15
        
        total_score = size_score + position_score + content_score + format_score
        
        # Penalty for very long text (likely paragraphs)
        if len(text) > 200:
            total_score *= 0.5
        
        return min(total_score, 1.0)
    
    def _calculate_position_score(self, element: Dict[str, Any], font_info: Dict[str, Any]) -> float:
        """
        Calculate score based on positioning characteristics
        """
        score = 0.0
        
        # Left alignment (headings often start at left margin)
        x_pos = font_info.get("x0", 0)
        if x_pos < 100:  # Near left margin
            score += 0.5
        
        # Isolation (surrounded by whitespace)
        text_length = len(element.get("text", ""))
        if text_length < 100:  # Short text more likely to be heading
            score += 0.3
        
        # Top of page bonus
        page_height = element.get("page_height", 792)
        y_pos = font_info.get("y0", 0)
        if y_pos > page_height * 0.8:  # Top 20% of page
            score += 0.2
        
        return min(score, 1.0)
    
    def _calculate_content_score(self, text: str) -> float:
        """
        Score based on textual patterns that indicate headings[8]
        """
        score = 0.0
        
        # Check English patterns
        for pattern in self.heading_patterns['english']:
            if re.match(pattern, text):
                score += 0.3
                break
        
        # Check multilingual patterns (bonus points)
        for pattern in self.heading_patterns['multilingual']:
            if re.search(pattern, text):
                score += 0.4  # Higher score for multilingual detection
                break
        
        # Capitalization patterns
        if text.isupper() and len(text.split()) <= 10:
            score += 0.2
        elif text.istitle() and len(text.split()) <= 8:
            score += 0.15
        
        # Length characteristics
        word_count = len(text.split())
        if 2 <= word_count <= 8:
            score += 0.1
        
        # Avoid common body text patterns
        if any(phrase in text.lower() for phrase in ['however', 'therefore', 'moreover', 'furthermore']):
            score -= 0.2
        
        return max(score, 0.0)
    
    def _classify_heading_hierarchy(self, scored_elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Classify headings into H1, H2, H3 hierarchy based on font sizes and scores
        """
        if not scored_elements:
            return []
        
        # Sort by heading score (descending)
        scored_elements.sort(key=lambda x: x["heading_score"], reverse=True)
        
        # Group by font size for hierarchical classification
        size_groups = defaultdict(list)
        for element in scored_elements:
            font_size = element.get("font_info", {}).get("size", 12)
            size_groups[font_size].append(element)
        
        # Sort font sizes (largest first for H1, H2, H3)
        sorted_sizes = sorted(size_groups.keys(), reverse=True)
        
        headings = []
        
        # Assign heading levels based on font size hierarchy
        for i, font_size in enumerate(sorted_sizes[:3]):  # Limit to 3 levels
            level = f"H{i+1}"
            
            for element in size_groups[font_size]:
                # Apply additional filters
                if element["heading_score"] > 0.4:  # Higher threshold for final selection
                    heading = {
                        "level": level,
                        "text": element.get("text", "").strip(),
                        "page": element.get("page_number", 1)
                    }
                    headings.append(heading)
        
        # Sort by page number for final output
        headings.sort(key=lambda x: (x["page"], x["level"]))
        
        # Remove duplicates and clean up
        return self._deduplicate_headings(headings)
    
    def _deduplicate_headings(self, headings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate headings and clean up the final list
        """
        seen_texts = set()
        unique_headings = []
        
        for heading in headings:
            text_key = heading["text"].lower().strip()
            
            # Skip if already seen or too short
            if text_key in seen_texts or len(text_key) < 3:
                continue
            
            # Skip if it looks like page numbers or references
            if re.match(r'^\d+$', text_key) or text_key.startswith('page '):
                continue
            
            seen_texts.add(text_key)
            unique_headings.append(heading)
        
        return unique_headings[:50]  # Limit total headings to reasonable number

    def validate_headings(self, headings: List[Dict[str, Any]]) -> bool:
        """
        Validate that detected headings are reasonable
        """
        if not headings:
            return True  # Empty is valid
        
        # Check for reasonable distribution
        level_counts = Counter(h["level"] for h in headings)
        
        # Should have some H1 headings
        if "H1" not in level_counts and len(headings) > 5:
            return False
        
        # Check page distribution
        pages = [h["page"] for h in headings]
        if max(pages) - min(pages) < 0:  # All on same page might be suspicious
            return len(headings) <= 10
        
        return True
