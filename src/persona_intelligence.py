"""
Persona-Driven Document Intelligence Engine
Extracts and ranks relevant sections based on user persona and job-to-be-done
Optimized for diverse domains and multilingual content
"""

import json
import time
import numpy as np
from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple, Callable
from collections import defaultdict, Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
import re
import math

# Import our existing components
from src.pdf_parser import PDFParser
from src.heading_detector import HeadingDetector
from src.performance_optimizer import PerformanceOptimizer

class PersonaIntelligenceEngine:
    """
    Advanced persona-driven document analysis system
    Combines semantic understanding with domain-specific ranking
    """
    
    def __init__(self, max_model_size_gb: float = 1.0):
        """Initialize with competition constraints"""
        self.max_model_size = max_model_size_gb * 1024 * 1024 * 1024  # Convert to bytes
        self.processing_timeout = 60  # seconds
        
        # Initialize components
        self.pdf_parser = PDFParser()
        self.heading_detector = HeadingDetector()
        self.performance_optimizer = PerformanceOptimizer()
        
        # Lightweight semantic models (under 1GB constraint)
        self.tfidf_vectorizer = None
        self.svd_reducer = None
        
        # Domain-specific keywords for persona matching
        self.persona_keywords = {
            'researcher': ['research', 'methodology', 'findings', 'literature', 'study', 'analysis', 'experiment'],
            'student': ['concept', 'definition', 'example', 'summary', 'key', 'important', 'chapter'],
            'analyst': ['trend', 'data', 'performance', 'metric', 'revenue', 'growth', 'market'],
            'investor': ['financial', 'revenue', 'profit', 'growth', 'risk', 'investment', 'return'],
            'engineer': ['technical', 'implementation', 'system', 'design', 'architecture', 'specification'],
            'manager': ['strategy', 'planning', 'decision', 'team', 'process', 'outcome', 'objective']
        }
        
        # Job-specific importance weights
        self.job_weights = {
            'literature_review': {'methodology': 0.3, 'results': 0.25, 'discussion': 0.2, 'conclusion': 0.15},
            'exam_preparation': {'definition': 0.3, 'example': 0.25, 'summary': 0.2, 'exercise': 0.15},
            'financial_analysis': {'revenue': 0.3, 'expenses': 0.2, 'growth': 0.2, 'forecast': 0.15},
            'technical_review': {'specification': 0.3, 'implementation': 0.25, 'performance': 0.2}
        }
    
    def analyze_document_collection(self, 
                                  pdf_paths: List[str], 
                                  persona: str, 
                                  job_to_be_done: str) -> Dict[str, Any]:
        """
        Main analysis method for persona-driven document intelligence
        
        Args:
            pdf_paths: List of PDF file paths
            persona: User persona description
            job_to_be_done: Specific task to accomplish
            
        Returns:
            Structured analysis results matching competition format
        """
        start_time = time.time()
        
        try:
            # Step 1: Extract structured content from all documents
            print(f"📚 Extracting content from {len(pdf_paths)} documents...")
            document_contents = self._extract_all_documents(pdf_paths)
            
            # Step 2: Build semantic understanding models
            print("🧠 Building semantic models...")
            self._build_semantic_models(document_contents)
            
            # Step 3: Analyze persona and job requirements
            print("👤 Analyzing persona requirements...")
            persona_profile = self._analyze_persona(persona, job_to_be_done)
            
            # Step 4: Extract and rank relevant sections
            print("🎯 Extracting relevant sections...")
            extracted_sections = self._extract_relevant_sections(
                document_contents, persona_profile
            )
            
            # Step 5: Perform subsection analysis
            print("🔍 Analyzing subsections...")
            subsection_analysis = self._analyze_subsections(
                document_contents, extracted_sections, persona_profile
            )
            
            # Step 6: Format output
            result = self._format_output(
                pdf_paths, persona, job_to_be_done, 
                extracted_sections, subsection_analysis, start_time
            )
            
            processing_time = time.time() - start_time
            print(f"✅ Analysis completed in {processing_time:.2f}s")
            
            return result
            
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            return self._create_fallback_result(pdf_paths, persona, job_to_be_done)
    
    def _extract_all_documents(self, pdf_paths: List[str]) -> List[Dict[str, Any]]:
        """Extract structured content from all PDF documents"""
        document_contents = []
        
        for pdf_path in pdf_paths:
            try:
                # Use existing PDF parser
                document_data = self.pdf_parser.extract_text_with_formatting(pdf_path)
                
                # Get document outline
                title, headings = self.heading_detector.identify_headings(document_data)
                
                # Enhance with semantic sections
                enhanced_doc = self._enhance_document_structure(
                    pdf_path, document_data, title, headings
                )
                
                document_contents.append(enhanced_doc)
                
            except Exception as e:
                print(f"⚠️ Failed to extract {pdf_path}: {e}")
                continue
        
        return document_contents
    
    def _enhance_document_structure(self, pdf_path: str, document_data: Dict[str, Any], 
                                  title: str, headings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Enhance document with semantic section analysis"""
        
        # Extract full text by sections
        sections = []
        current_section = {"heading": None, "content": "", "page_start": 1, "page_end": 1}
        
        for page in document_data.get("pages", []):
            page_num = page.get("page_number", 1)
            page_text = page.get("raw_text", "")
            
            # Find headings on this page
            page_headings = [h for h in headings if h["page"] == page_num]
            
            if page_headings:
                # Save current section
                if current_section["content"].strip():
                    current_section["page_end"] = page_num - 1
                    sections.append(current_section.copy())
                
                # Start new section
                for heading in page_headings:
                    current_section = {
                        "heading": heading,
                        "content": page_text,
                        "page_start": page_num,
                        "page_end": page_num
                    }
            else:
                # Continue current section
                current_section["content"] += "\n" + page_text
                current_section["page_end"] = page_num
        
        # Add final section
        if current_section["content"].strip():
            sections.append(current_section)
        
        return {
            "filepath": pdf_path,
            "title": title,
            "headings": headings,
            "sections": sections,
            "total_pages": document_data.get("total_pages", 0),
            "word_count": sum(len(s["content"].split()) for s in sections)
        }
    
    def _build_semantic_models(self, document_contents: List[Dict[str, Any]]):
        """Build lightweight semantic models for similarity analysis"""
        
        # Collect all text content
        all_texts = []
        for doc in document_contents:
            for section in doc.get("sections", []):
                content = section.get("content", "")
                if content.strip():
                    all_texts.append(content)
        
        if not all_texts:
            return
        
        try:
            # TF-IDF vectorization (memory efficient)
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=5000,  # Limit features for speed
                stop_words='english',
                ngram_range=(1, 2),
                max_df=0.95,
                min_df=2
            )
            
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(all_texts)
            
            # Dimensionality reduction for efficiency
            if tfidf_matrix.shape[1] > 500:
                self.svd_reducer = TruncatedSVD(n_components=300, random_state=42)
                self.reduced_embeddings = self.svd_reducer.fit_transform(tfidf_matrix)
            else:
                self.reduced_embeddings = tfidf_matrix.toarray()
            
            print(f"🔧 Built semantic model: {len(all_texts)} texts, {self.reduced_embeddings.shape[1]} features")
            
        except Exception as e:
            print(f"⚠️ Semantic model building failed: {e}")
            self.tfidf_vectorizer = None
    
    def _analyze_persona(self, persona: str, job_to_be_done: str) -> Dict[str, Any]:
        """Analyze persona and job to create relevance profile"""
        
        # Extract persona type
        persona_type = self._identify_persona_type(persona.lower())
        
        # Extract job type
        job_type = self._identify_job_type(job_to_be_done.lower())
        
        # Get relevant keywords
        persona_keywords = self.persona_keywords.get(persona_type, [])
        job_keywords = self._extract_job_keywords(job_to_be_done)
        
        # Combine for query vector
        query_text = f"{persona} {job_to_be_done}"
        
        profile = {
            "persona_type": persona_type,
            "job_type": job_type,
            "persona_keywords": persona_keywords,
            "job_keywords": job_keywords,
            "query_text": query_text,
            "importance_weights": self.job_weights.get(job_type, {})
        }
        
        return profile
    
    def _identify_persona_type(self, persona_text: str) -> str:
        """Identify persona type from description"""
        for persona_type, keywords in self.persona_keywords.items():
            if any(keyword in persona_text for keyword in keywords[:3]):  # Check top 3 keywords
                return persona_type
        
        # Fallback: look for common role indicators
        if any(word in persona_text for word in ['phd', 'research', 'scientist']):
            return 'researcher'
        elif any(word in persona_text for word in ['student', 'undergraduate', 'graduate']):
            return 'student'
        elif any(word in persona_text for word in ['analyst', 'investment', 'financial']):
            return 'analyst'
        else:
            return 'general'
    
    def _identify_job_type(self, job_text: str) -> str:
        """Identify job type from description"""
        if any(word in job_text for word in ['literature review', 'review', 'survey']):
            return 'literature_review'
        elif any(word in job_text for word in ['exam', 'study', 'preparation', 'learn']):
            return 'exam_preparation'
        elif any(word in job_text for word in ['financial', 'revenue', 'analyze']):
            return 'financial_analysis'
        elif any(word in job_text for word in ['technical', 'implementation', 'system']):
            return 'technical_review'
        else:
            return 'general_analysis'
    
    def _extract_job_keywords(self, job_text: str) -> List[str]:
        """Extract important keywords from job description"""
        # Simple keyword extraction
        words = re.findall(r'\b[a-zA-Z]{3,}\b', job_text.lower())
        
        # Filter stop words and extract meaningful terms
        stop_words = {'the', 'and', 'for', 'are', 'with', 'this', 'that', 'from', 'they', 'been', 'have', 'has'}
        keywords = [word for word in words if word not in stop_words and len(word) > 3]
        
        # Return top keywords by frequency
        return list(Counter(keywords).keys())[:10]
    
    def _extract_relevant_sections(self, document_contents: List[Dict[str, Any]], 
                                 persona_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract and rank sections based on persona relevance"""
        
        scored_sections = []
        
        for doc in document_contents:
            doc_name = doc.get("filepath", "").split('/')[-1]
            
            for section in doc.get("sections", []):
                heading = section.get("heading")
                content = section.get("content", "")
                
                if not content.strip() or len(content) < 50:
                    continue
                
                # Calculate relevance score
                relevance_score = self._calculate_section_relevance(
                    content, heading, persona_profile
                )
                
                if relevance_score > 0.1:  # Threshold for inclusion
                    scored_sections.append({
                        "document": doc_name,
                        "page": section.get("page_start", 1),
                        "section_title": heading.get("text", "Untitled") if heading else "Content Section",
                        "relevance_score": relevance_score,
                        "content": content,
                        "heading_level": heading.get("level", "H1") if heading else "H1"
                    })
        
        # Sort by relevance score and assign importance ranks
        scored_sections.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        # Assign importance ranks
        for i, section in enumerate(scored_sections):
            section["importance_rank"] = i + 1
        
        # Return top sections (limit for output size)
        return scored_sections[:20]
    
    def _calculate_section_relevance(self, content: str, heading: Dict[str, Any], 
                                   persona_profile: Dict[str, Any]) -> float:
        """Calculate relevance score for a section"""
        score = 0.0
        
        # Keyword matching score
        content_lower = content.lower()
        
        # Persona keywords
        persona_matches = sum(1 for kw in persona_profile["persona_keywords"] if kw in content_lower)
        score += (persona_matches / max(len(persona_profile["persona_keywords"]), 1)) * 0.3
        
        # Job keywords
        job_matches = sum(1 for kw in persona_profile["job_keywords"] if kw in content_lower)
        score += (job_matches / max(len(persona_profile["job_keywords"]), 1)) * 0.4
        
        # Semantic similarity (if models available)
        if self.tfidf_vectorizer is not None:
            try:
                query_vector = self.tfidf_vectorizer.transform([persona_profile["query_text"]])
                content_vector = self.tfidf_vectorizer.transform([content])
                
                similarity = cosine_similarity(query_vector, content_vector)[0][0]
                score += similarity * 0.3
                
            except Exception:
                pass  # Skip if similarity calculation fails
        
        # Heading level importance (H1 > H2 > H3)
        if heading:
            level = heading.get("level", "H1")
            level_weights = {"H1": 0.1, "H2": 0.05, "H3": 0.02}
            score += level_weights.get(level, 0)
        
        # Content length factor (prefer substantial sections)
        word_count = len(content.split())
        if 100 <= word_count <= 1000:
            score += 0.05
        elif word_count > 1000:
            score += 0.02  # Slight penalty for very long sections
        
        return min(score, 1.0)
    
    def _analyze_subsections(self, document_contents: List[Dict[str, Any]], 
                           extracted_sections: List[Dict[str, Any]], 
                           persona_profile: Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Perform granular subsection analysis"""
        
        subsection_analysis = []
        
        for section in extracted_sections[:10]:  # Analyze top 10 sections
            content = section.get("content", "")
            
            # Split content into meaningful chunks (paragraphs/sentences)
            chunks = self._split_content_into_chunks(content)
            
            for chunk in chunks:
                if len(chunk.split()) < 20:  # Skip very short chunks
                    continue
                
                # Calculate chunk relevance
                chunk_score = self._calculate_chunk_relevance(chunk, persona_profile)
                
                if chunk_score > 0.2:  # Threshold for inclusion
                    refined_text = self._refine_text_chunk(chunk, persona_profile)
                    
                    subsection_analysis.append({
                        "document": section["document"],
                        "page": section["page"],
                        "refined_text": refined_text,
                        "relevance_score": chunk_score
                    })
        
        # Sort by relevance and limit output
        subsection_analysis.sort(key=lambda x: x["relevance_score"], reverse=True)
        return subsection_analysis[:15]
    
    def _split_content_into_chunks(self, content: str) -> List[str]:
        """Split content into meaningful chunks for analysis"""
        # Split by paragraphs first
        paragraphs = content.split('\n\n')
        
        chunks = []
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
                
            # If paragraph is very long, split by sentences
            if len(para.split()) > 150:
                sentences = re.split(r'[.!?]+', para)
                current_chunk = ""
                
                for sentence in sentences:
                    sentence = sentence.strip()
                    if not sentence:
                        continue
                        
                    if len((current_chunk + " " + sentence).split()) <= 100:
                        current_chunk += " " + sentence
                    else:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        current_chunk = sentence
                
                if current_chunk:
                    chunks.append(current_chunk.strip())
            else:
                chunks.append(para)
        
        return chunks
    
    def _calculate_chunk_relevance(self, chunk: str, persona_profile: Dict[str, Any]) -> float:
        """Calculate relevance score for a text chunk"""
        chunk_lower = chunk.lower()
        
        # Keyword density scoring
        persona_matches = sum(1 for kw in persona_profile["persona_keywords"] if kw in chunk_lower)
        job_matches = sum(1 for kw in persona_profile["job_keywords"] if kw in chunk_lower)
        
        keyword_density = (persona_matches + job_matches) / len(chunk.split())
        
        # Content quality indicators
        quality_score = 0.0
        
        # Prefer chunks with numbers, data, specific information
        if re.search(r'\d+\.?\d*%|\$\d+|\d+\.\d+', chunk):
            quality_score += 0.1
        
        # Prefer chunks with technical terms or definitions
        if any(indicator in chunk_lower for indicator in ['definition', 'method', 'result', 'analysis', 'conclusion']):
            quality_score += 0.1
        
        return keyword_density * 0.8 + quality_score
    
    def _refine_text_chunk(self, chunk: str, persona_profile: Dict[str, Any]) -> str:
        """Refine and clean text chunk for output"""
        # Clean up whitespace and formatting
        refined = re.sub(r'\s+', ' ', chunk).strip()
        
        # Limit length for output
        if len(refined) > 500:
            sentences = refined.split('. ')
            refined = '. '.join(sentences[:3]) + '.'
        
        return refined
    
    def _format_output(self, pdf_paths: List[str], persona: str, job_to_be_done: str,
                      extracted_sections: List[Dict[str, Any]], 
                      subsection_analysis: List[Dict[str, Any]], 
                      start_time: float) -> Dict[str, Any]:
        """Format output according to competition requirements"""
        
        return {
            "metadata": {
                "documents": [path.split('/')[-1] for path in pdf_paths],
                "persona": persona,
                "job_to_be_done": job_to_be_done,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "processing_time_seconds": round(time.time() - start_time, 2),
                "total_sections_analyzed": len(extracted_sections),
                "total_subsections_extracted": len(subsection_analysis)
            },
            "extracted_sections": [
                {
                    "document": section["document"],
                    "page": section["page"],
                    "section_title": section["section_title"],
                    "importance_rank": section["importance_rank"]
                }
                for section in extracted_sections
            ],
            "subsection_analysis": [
                {
                    "document": analysis["document"],
                    "page": analysis["page"],
                    "refined_text": analysis["refined_text"]
                }
                for analysis in subsection_analysis
            ]
        }
    
    def _create_fallback_result(self, pdf_paths: List[str], persona: str, 
                              job_to_be_done: str) -> Dict[str, Any]:
        """Create fallback result when processing fails"""
        return {
            "metadata": {
                "documents": [path.split('/')[-1] for path in pdf_paths],
                "persona": persona,
                "job_to_be_done": job_to_be_done,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": "processing_failed"
            },
            "extracted_sections": [],
            "subsection_analysis": []
        }
