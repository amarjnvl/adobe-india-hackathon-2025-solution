/**
 * PDF Intelligence Engine - Web Integration
 * Bridges Round 1 algorithms with web interface
 */

class PDFIntelligence {
  constructor() {
    this.outlineExtractor = null;
    this.personaAnalyzer = null;
    this.isInitialized = false;

    // Cache for processed documents
    this.documentCache = new Map();
    this.insightsCache = new Map();
  }

  async initialize() {
    console.log("🧠 Initializing PDF Intelligence Engine");

    try {
      // Initialize WebAssembly modules (if available)
      await this.initializeWASM();

      // Initialize JavaScript fallbacks
      this.initializeJSProcessors();

      this.isInitialized = true;
      console.log("✅ PDF Intelligence Engine ready");
    } catch (error) {
      console.error("❌ Intelligence initialization failed:", error);
      // Fallback to basic processing
      this.initializeFallback();
    }
  }

  async initializeWASM() {
    // Check if WASM modules are available
    if (typeof WebAssembly !== "undefined") {
      try {
        // Load compiled WASM from Round 1 algorithms
        const wasmModule = await import("./wasm/pdf-processor.js");
        this.outlineExtractor = await wasmModule.createOutlineExtractor();
        this.personaAnalyzer = await wasmModule.createPersonaAnalyzer();

        console.log("🚀 WASM modules loaded successfully");
      } catch (error) {
        console.log("⚠️ WASM modules not available, using JavaScript fallback");
        throw error;
      }
    } else {
      throw new Error("WebAssembly not supported");
    }
  }

  initializeJSProcessors() {
    // JavaScript implementations of Round 1 algorithms
    this.outlineExtractor = new JSOutlineExtractor();
    this.personaAnalyzer = new JSPersonaAnalyzer();
  }

  initializeFallback() {
    // Basic fallback processors
    this.outlineExtractor = new BasicOutlineExtractor();
    this.personaAnalyzer = new BasicPersonaAnalyzer();
    this.isInitialized = true;
  }

  async extractOutline(pdfArrayBuffer) {
    if (!this.isInitialized) {
      throw new Error("Intelligence engine not initialized");
    }

    const cacheKey = this.generateCacheKey(pdfArrayBuffer);

    // Check cache first
    if (this.documentCache.has(cacheKey)) {
      console.log("📋 Returning cached outline");
      return this.documentCache.get(cacheKey);
    }

    console.log("⚡ Extracting document outline...");

    try {
      const outline = await this.outlineExtractor.extract(pdfArrayBuffer);

      // Cache result
      this.documentCache.set(cacheKey, outline);

      console.log(`📊 Extracted ${outline.outline?.length || 0} headings`);
      return outline;
    } catch (error) {
      console.error("Outline extraction failed:", error);
      return this.createFallbackOutline();
    }
  }

  async generatePersonaInsights(pdfDocument, persona) {
    if (!this.isInitialized || !this.personaAnalyzer) {
      return this.createFallbackInsights();
    }

    const cacheKey = `${this.generateCacheKey(
      pdfDocument.arrayBuffer
    )}-${JSON.stringify(persona)}`;

    // Check cache
    if (this.insightsCache.has(cacheKey)) {
      console.log("🎯 Returning cached insights");
      return this.insightsCache.get(cacheKey);
    }

    console.log("🤖 Generating persona-driven insights...");

    try {
      // Prepare input for Round 1B algorithm
      const analysisInput = {
        documents: [pdfDocument],
        persona: `${persona.type}: ${persona.description}`,
        job_to_be_done: persona.job,
      };

      const insights = await this.personaAnalyzer.analyze(analysisInput);

      // Transform for web display
      const webInsights = this.transformInsightsForWeb(insights);

      // Cache result
      this.insightsCache.set(cacheKey, webInsights);

      console.log(`💡 Generated ${webInsights.length} insights`);
      return webInsights;
    } catch (error) {
      console.error("Insights generation failed:", error);
      return this.createFallbackInsights();
    }
  }

  async generateMultiDocumentInsights(documentCollection, persona) {
    console.log("📚 Generating multi-document insights...");

    try {
      const analysisInput = {
        documents: documentCollection,
        persona: `${persona.type}: ${persona.description}`,
        job_to_be_done: persona.job,
      };

      const insights = await this.personaAnalyzer.analyze(analysisInput);
      return this.transformMultiDocInsights(insights);
    } catch (error) {
      console.error("Multi-document analysis failed:", error);
      return this.createFallbackInsights();
    }
  }

  transformInsightsForWeb(roundOneOutput) {
    if (!roundOneOutput || !roundOneOutput.extracted_sections) {
      return [];
    }

    const webInsights = [];

    // Transform extracted sections
    roundOneOutput.extracted_sections.forEach((section, index) => {
      webInsights.push({
        page: section.page,
        section_title: section.section_title,
        importance_rank: section.importance_rank || index + 1,
        refined_text: this.getRefineTextForSection(
          roundOneOutput.subsection_analysis,
          section.document,
          section.page
        ),
      });
    });

    return webInsights.slice(0, 10); // Limit for UI
  }

  getRefineTextForSection(subsections, document, page) {
    if (!subsections) return null;

    const relevantSubsection = subsections.find(
      (sub) => sub.document === document && sub.page === page
    );

    return relevantSubsection ? relevantSubsection.refined_text : null;
  }

  transformMultiDocInsights(roundOneOutput) {
    // Similar transformation but with document context
    return this.transformInsightsForWeb(roundOneOutput);
  }

  generateCacheKey(arrayBuffer) {
    // Simple hash of array buffer for caching
    const bytes = new Uint8Array(arrayBuffer.slice(0, 1024)); // First 1KB
    let hash = 0;
    for (let i = 0; i < bytes.length; i++) {
      hash = ((hash << 5) - hash + bytes[i]) & 0xffffffff;
    }
    return hash.toString(36);
  }

  createFallbackOutline() {
    return {
      title: "Document",
      outline: [],
    };
  }

  createFallbackInsights() {
    return [
      {
        page: 1,
        section_title: "Document Content",
        importance_rank: 1,
        refined_text: "No specific insights available for this persona",
      },
    ];
  }

  clearCache() {
    this.documentCache.clear();
    this.insightsCache.clear();
    console.log("🧹 Intelligence cache cleared");
  }
}

/**
 * JavaScript Outline Extractor (Fallback)
 */
class JSOutlineExtractor {
  async extract(pdfArrayBuffer) {
    // Simplified extraction using PDF.js or similar
    try {
      // This would integrate with PDF.js for client-side processing
      const pdfDoc = await this.loadPDFDocument(pdfArrayBuffer);

      const outline = {
        title: "Document Title",
        outline: [],
      };

      // Basic heading detection based on font sizes
      for (let pageNum = 1; pageNum <= pdfDoc.numPages; pageNum++) {
        const page = await pdfDoc.getPage(pageNum);
        const textContent = await page.getTextContent();

        const headings = this.detectHeadingsOnPage(textContent, pageNum);
        outline.outline.push(...headings);
      }

      return outline;
    } catch (error) {
      console.error("JS extraction failed:", error);
      throw error;
    }
  }

  async loadPDFDocument(arrayBuffer) {
    // Placeholder - would use PDF.js
    return {
      numPages: 1,
      getPage: () => ({
        getTextContent: () => ({ items: [] }),
      }),
    };
  }

  detectHeadingsOnPage(textContent, pageNumber) {
    // Simplified heading detection
    const headings = [];

    // Basic heuristics based on font sizes, positions
    textContent.items.forEach((item) => {
      if (this.isLikelyHeading(item)) {
        headings.push({
          level: this.determineHeadingLevel(item),
          text: item.str.trim(),
          page: pageNumber,
        });
      }
    });

    return headings;
  }

  isLikelyHeading(textItem) {
    // Basic heading detection logic
    const text = textItem.str.trim();
    return (
      text.length > 3 &&
      text.length < 100 &&
      (textItem.height > 12 || text.match(/^\d+\./))
    );
  }

  determineHeadingLevel(textItem) {
    // Simple level determination
    if (textItem.height > 16) return "H1";
    if (textItem.height > 14) return "H2";
    return "H3";
  }
}

/**
 * JavaScript Persona Analyzer (Fallback)
 */
class JSPersonaAnalyzer {
  async analyze(input) {
    // Simplified persona analysis
    const insights = {
      metadata: {
        documents: input.documents.map((d) => d.file?.name || "document"),
        persona: input.persona,
        job_to_be_done: input.job_to_be_done,
        timestamp: new Date().toISOString(),
      },
      extracted_sections: [],
      subsection_analysis: [],
    };

    // Basic keyword matching
    const keywords = this.extractPersonaKeywords(
      input.persona,
      input.job_to_be_done
    );

    input.documents.forEach((doc, docIndex) => {
      if (doc.outline && doc.outline.outline) {
        doc.outline.outline.forEach((heading, headingIndex) => {
          const relevanceScore = this.calculateBasicRelevance(
            heading.text,
            keywords
          );

          if (relevanceScore > 0.3) {
            insights.extracted_sections.push({
              document: doc.file?.name || `document_${docIndex}`,
              page: heading.page,
              section_title: heading.text,
              importance_rank: headingIndex + 1,
            });
          }
        });
      }
    });

    return insights;
  }

  extractPersonaKeywords(persona, jobToBeDone) {
    const text = `${persona} ${jobToBeDone}`.toLowerCase();
    return text.split(/\s+/).filter((word) => word.length > 3);
  }

  calculateBasicRelevance(text, keywords) {
    const textLower = text.toLowerCase();
    const matches = keywords.filter((keyword) => textLower.includes(keyword));
    return matches.length / keywords.length;
  }
}

/**
 * Basic processors for maximum compatibility
 */
class BasicOutlineExtractor {
  async extract(pdfArrayBuffer) {
    return {
      title: "PDF Document",
      outline: [],
    };
  }
}

class BasicPersonaAnalyzer {
  async analyze(input) {
    return {
      metadata: {
        documents: input.documents.map((d) => d.file?.name || "document"),
        persona: input.persona,
        job_to_be_done: input.job_to_be_done,
        timestamp: new Date().toISOString(),
      },
      extracted_sections: [],
      subsection_analysis: [],
    };
  }
}

// Export for global use
window.PDFIntelligence = PDFIntelligence;
