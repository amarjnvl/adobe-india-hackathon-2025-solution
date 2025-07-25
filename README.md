# Adobe Hackathon 2025 – Round 1A: PDF Outline Extractor

## Overview

This project extracts structured outlines (headings hierarchy) from PDF documents. It uses a multi-layered approach combining PDF parsing, font clustering, layout analysis, and multilingual handling to produce a clean and hierarchical summary.

---

## Approach

1. **PDF Parsing**  
   Uses `pdfplumber` for extracting text with formatting metadata. `PyMuPDF` (Fitz) serves as a fallback and provides additional font/style features.

2. **Heading Detection**  
   Analyzes font sizes, positions, and styles. Also incorporates regex and text patterns to identify heading candidates.

3. **Hierarchical Classification**  
   Applies `scikit-learn` clustering (e.g., KMeans) on font sizes and layout distances to infer heading levels (H1, H2, etc.).

4. **Multilingual Support**  
   Handles multiple scripts including CJK (Chinese, Japanese, Korean), making it robust for international documents.

---

## Libraries Used

| Library        | Purpose                                |
|----------------|----------------------------------------|
| pdfplumber     | Precise PDF text + layout extraction   |
| PyMuPDF        | Fallback parsing & font metadata       |
| scikit-learn   | Font size clustering (e.g., for H1/H2) |
| numpy          | Layout processing and calculations     |

---

## Usage

### Build & Run with Docker

```bash
# Build Docker Image (AMD64)
docker build --platform linux/amd64 -t pdf-outline-extractor:v1 .

# Run the Solution
docker run --rm \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  --network none \
  pdf-outline-extractor:v1
