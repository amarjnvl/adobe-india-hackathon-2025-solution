/**
 * Main Application Controller
 * Orchestrates the intelligent PDF reading experience
 */

class IntelligentPDFReader {
  constructor() {
    this.currentPDF = null;
    this.currentPersona = null;
    this.documentCollection = [];
    this.adobeAPI = null;
    this.intelligence = null;

    // Initialize components
    this.initializeApp();
  }

  async initializeApp() {
    console.log("🚀 Initializing Intelligent PDF Reader");

    try {
      // Initialize Adobe PDF Embed API
      this.adobeAPI = new AdobePDFEmbed();
      await this.adobeAPI.initialize();

      // Initialize PDF Intelligence Engine
      this.intelligence = new PDFIntelligence();
      await this.intelligence.initialize();

      // Setup UI event listeners
      this.setupEventListeners();

      // Load demo content if available
      this.loadDemoContent();

      // Hide loading screen
      this.hideLoadingScreen();

      console.log("✅ Application initialized successfully");
    } catch (error) {
      console.error("❌ Application initialization failed:", error);
      this.showError("Failed to initialize application");
    }
  }

  setupEventListeners() {
    // File upload
    document.getElementById("upload-btn").addEventListener("click", () => {
      document.getElementById("file-input").click();
    });

    document.getElementById("file-input").addEventListener("change", (e) => {
      this.handleFileUpload(e.target.files);
    });

    // Persona configuration
    document.getElementById("persona-btn").addEventListener("click", () => {
      this.showPersonaModal();
    });

    document.getElementById("save-persona").addEventListener("click", () => {
      this.savePersonaConfiguration();
    });

    document
      .getElementById("close-persona-modal")
      .addEventListener("click", () => {
        this.hidePersonaModal();
      });

    // View toggles
    document.getElementById("single-view").addEventListener("click", () => {
      this.switchToSingleView();
    });

    document.getElementById("multi-view").addEventListener("click", () => {
      this.switchToMultiView();
    });

    // Demo button
    document.getElementById("demo-btn").addEventListener("click", () => {
      this.loadDemoContent();
    });

    // Panel toggle
    document.getElementById("toggle-panel").addEventListener("click", () => {
      this.toggleIntelligencePanel();
    });

    // Preset persona buttons
    document.querySelectorAll(".preset-btn").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        this.loadPersonaPreset(e.target.getAttribute("data-preset"));
      });
    });

    // Outline navigation
    document.addEventListener("click", (e) => {
      if (e.target.classList.contains("outline-item")) {
        this.navigateToPage(parseInt(e.target.getAttribute("data-page")));
      }
    });

    // Drag and drop
    this.setupDragAndDrop();
  }

  setupDragAndDrop() {
    const dropZone = document.getElementById("pdf-container");

    dropZone.addEventListener("dragover", (e) => {
      e.preventDefault();
      dropZone.classList.add("drag-over");
    });

    dropZone.addEventListener("dragleave", () => {
      dropZone.classList.remove("drag-over");
    });

    dropZone.addEventListener("drop", (e) => {
      e.preventDefault();
      dropZone.classList.remove("drag-over");
      this.handleFileUpload(e.dataTransfer.files);
    });
  }

  async handleFileUpload(files) {
    if (!files || files.length === 0) return;

    this.showLoadingStatus("Processing PDF documents...");

    try {
      const pdfFiles = Array.from(files).filter(
        (file) => file.type === "application/pdf"
      );

      if (pdfFiles.length === 0) {
        throw new Error("Please select valid PDF files");
      }

      // Process single or multiple PDFs
      if (pdfFiles.length === 1) {
        await this.processSinglePDF(pdfFiles[0]);
      } else {
        await this.processMultiplePDFs(pdfFiles);
      }
    } catch (error) {
      console.error("File upload error:", error);
      this.showError(error.message);
    } finally {
      this.hideLoadingScreen();
    }
  }

  async processSinglePDF(file) {
    console.log("📄 Processing single PDF:", file.name);

    // Convert to ArrayBuffer for Adobe API
    const arrayBuffer = await file.arrayBuffer();

    // Display PDF in Adobe viewer
    await this.adobeAPI.displayPDF(arrayBuffer, file.name);

    // Extract document intelligence
    const outline = await this.intelligence.extractOutline(arrayBuffer);

    // Update UI
    this.updateDocumentOutline(outline);
    this.hideWelcomeScreen();

    // Store current document
    this.currentPDF = {
      file: file,
      arrayBuffer: arrayBuffer,
      outline: outline,
    };

    // Generate insights if persona is set
    if (this.currentPersona) {
      await this.generatePersonaInsights();
    }
  }

  async processMultiplePDFs(files) {
    console.log("📚 Processing multiple PDFs:", files.length);

    this.documentCollection = [];

    for (const file of files) {
      const arrayBuffer = await file.arrayBuffer();
      const outline = await this.intelligence.extractOutline(arrayBuffer);

      this.documentCollection.push({
        file: file,
        arrayBuffer: arrayBuffer,
        outline: outline,
      });
    }

    // Switch to multi-document view
    this.switchToMultiView();
    this.updateMultiDocumentView();

    // Generate cross-document insights
    if (this.currentPersona) {
      await this.generateMultiDocumentInsights();
    }
  }

  updateDocumentOutline(outline) {
    const outlineContainer = document.getElementById("document-outline");

    if (!outline || !outline.outline || outline.outline.length === 0) {
      outlineContainer.innerHTML = `
                <div class="outline-placeholder">
                    <i class="fas fa-info-circle"></i>
                    <p>No headings detected in this document</p>
                </div>
            `;
      return;
    }

    let outlineHTML = `<div class="document-title">${outline.title}</div>`;

    outline.outline.forEach((heading) => {
      const levelClass = `level-${heading.level.toLowerCase()}`;
      outlineHTML += `
                <div class="outline-item ${levelClass}" data-page="${heading.page}">
                    <div class="heading-content">
                        <span class="heading-level">${heading.level}</span>
                        <span class="heading-text">${heading.text}</span>
                        <span class="heading-page">p.${heading.page}</span>
                    </div>
                </div>
            `;
    });

    outlineContainer.innerHTML = outlineHTML;
  }

  showPersonaModal() {
    document.getElementById("persona-modal").classList.remove("hidden");

    // Pre-fill if persona exists
    if (this.currentPersona) {
      document.getElementById("persona-type").value =
        this.currentPersona.type || "";
      document.getElementById("persona-description").value =
        this.currentPersona.description || "";
      document.getElementById("job-description").value =
        this.currentPersona.job || "";
    }
  }

  hidePersonaModal() {
    document.getElementById("persona-modal").classList.add("hidden");
  }

  loadPersonaPreset(presetType) {
    const presets = {
      "ml-researcher": {
        type: "researcher",
        description:
          "PhD researcher in machine learning with expertise in deep learning, neural networks, and AI applications",
        job: "Conduct comprehensive literature review and identify research gaps in current methodologies",
      },
      "business-analyst": {
        type: "analyst",
        description:
          "Senior business analyst with experience in market research, financial modeling, and strategic planning",
        job: "Analyze market trends, competitive landscape, and business performance metrics",
      },
      student: {
        type: "student",
        description:
          "University student studying computer science with focus on algorithms and data structures",
        job: "Prepare for exams by understanding key concepts, definitions, and problem-solving approaches",
      },
      investor: {
        type: "investor",
        description:
          "Investment professional specializing in technology sector with focus on growth companies",
        job: "Evaluate investment opportunities by analyzing financial performance and market positioning",
      },
    };

    const preset = presets[presetType];
    if (preset) {
      document.getElementById("persona-type").value = preset.type;
      document.getElementById("persona-description").value = preset.description;
      document.getElementById("job-description").value = preset.job;
    }
  }

  async savePersonaConfiguration() {
    const personaType = document.getElementById("persona-type").value;
    const description = document.getElementById("persona-description").value;
    const job = document.getElementById("job-description").value;

    if (!personaType || !description || !job) {
      this.showError("Please fill in all persona fields");
      return;
    }

    this.currentPersona = {
      type: personaType,
      description: description,
      job: job,
    };

    // Update UI
    this.hidePersonaModal();
    this.updatePersonaIndicator();

    // Generate insights for current document(s)
    if (this.currentPDF) {
      await this.generatePersonaInsights();
    } else if (this.documentCollection.length > 0) {
      await this.generateMultiDocumentInsights();
    }
  }

  updatePersonaIndicator() {
    const personaBtn = document.getElementById("persona-btn");
    if (this.currentPersona) {
      personaBtn.classList.add("active");
      personaBtn.innerHTML = `
                <i class="fas fa-user-check"></i>
                ${
                  this.currentPersona.type.charAt(0).toUpperCase() +
                  this.currentPersona.type.slice(1)
                }
            `;
    }
  }

  async generatePersonaInsights() {
    if (!this.currentPDF || !this.currentPersona) return;

    this.showLoadingStatus("Generating personalized insights...");

    try {
      const insights = await this.intelligence.generatePersonaInsights(
        this.currentPDF,
        this.currentPersona
      );

      this.updateInsightsPanel(insights);
    } catch (error) {
      console.error("Insights generation failed:", error);
    }
  }

  async generateMultiDocumentInsights() {
    if (this.documentCollection.length === 0 || !this.currentPersona) return;

    this.showLoadingStatus("Analyzing document collection...");

    try {
      const insights = await this.intelligence.generateMultiDocumentInsights(
        this.documentCollection,
        this.currentPersona
      );

      this.updateMultiDocumentInsights(insights);
    } catch (error) {
      console.error("Multi-document analysis failed:", error);
    }
  }

  updateInsightsPanel(insights) {
    const insightsContainer = document.getElementById("related-insights");

    if (!insights || insights.length === 0) {
      insightsContainer.innerHTML = `
                <div class="insights-placeholder">
                    <i class="fas fa-search"></i>
                    <p>No relevant insights found for this persona</p>
                </div>
            `;
      return;
    }

    let insightsHTML = "";

    insights.forEach((insight, index) => {
      insightsHTML += `
                <div class="insight-item" data-page="${insight.page}">
                    <div class="insight-header">
                        <div class="insight-rank">#${index + 1}</div>
                        <div class="insight-title">${
                          insight.section_title
                        }</div>
                        <div class="insight-page">p.${insight.page}</div>
                    </div>
                    <div class="insight-content">
                        ${
                          insight.refined_text ||
                          "Key insight identified for your persona"
                        }
                    </div>
                    <div class="insight-actions">
                        <button class="insight-btn" onclick="app.navigateToPage(${
                          insight.page
                        })">
                            <i class="fas fa-external-link-alt"></i>
                            View
                        </button>
                    </div>
                </div>
            `;
    });

    insightsContainer.innerHTML = insightsHTML;
  }

  navigateToPage(pageNumber) {
    if (this.adobeAPI) {
      this.adobeAPI.navigateToPage(pageNumber);
    }
  }

  switchToSingleView() {
    document.getElementById("single-view").classList.add("active");
    document.getElementById("multi-view").classList.remove("active");
    // Implementation for single document view
  }

  switchToMultiView() {
    document.getElementById("multi-view").classList.add("active");
    document.getElementById("single-view").classList.remove("active");
    // Implementation for multi-document view
  }

  toggleIntelligencePanel() {
    const panel = document.getElementById("intelligence-panel");
    panel.classList.toggle("collapsed");
  }

  showLoadingStatus(message) {
    document.getElementById("loading-status").textContent = message;
    document.getElementById("loading-screen").classList.remove("hidden");
  }

  hideLoadingScreen() {
    document.getElementById("loading-screen").classList.add("hidden");
    document.getElementById("app-container").classList.remove("hidden");
  }

  hideWelcomeScreen() {
    document.getElementById("welcome-screen").classList.add("hidden");
  }

  showError(message) {
    // Simple error display - could be enhanced with toast notifications
    alert(`Error: ${message}`);
  }

  async loadDemoContent() {
    // Load sample PDF for demonstration
    try {
      const response = await fetch("assets/samples/sample-research-paper.pdf");
      const arrayBuffer = await response.arrayBuffer();

      const demoFile = new File([arrayBuffer], "sample-research-paper.pdf", {
        type: "application/pdf",
      });

      await this.processSinglePDF(demoFile);

      // Set demo persona
      this.currentPersona = {
        type: "researcher",
        description: "Research scientist in artificial intelligence",
        job: "Literature review on neural network architectures",
      };

      this.updatePersonaIndicator();
      await this.generatePersonaInsights();
    } catch (error) {
      console.log("Demo content not available:", error);
    }
  }
}

// Initialize application when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  window.app = new IntelligentPDFReader();
});