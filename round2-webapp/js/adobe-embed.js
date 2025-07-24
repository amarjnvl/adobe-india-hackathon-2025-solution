/**
 * Adobe PDF Embed API Wrapper
 * Handles PDF viewing with intelligence overlay
 */

class AdobePDFEmbed {
  constructor() {
    this.adobeDCView = null;
    this.currentPDF = null;
    this.clientId = "8c0cd670273d451cbc9b351b11d22318"; // Adobe's demo client ID
    // this.clientId = "YOUR_ADOBE_CLIENT_ID"; // Replace with actual client ID
    this.isInitialized = false;
  }

  async initialize() {
    console.log("🔧 Initializing Adobe PDF Embed API");

    return new Promise((resolve, reject) => {
      if (window.AdobeDC) {
        this.adobeDCView = new window.AdobeDC.View({
          clientId: this.clientId,
          divId: "adobe-dc-view",
        });

        this.isInitialized = true;
        console.log("✅ Adobe PDF Embed API initialized");
        resolve();
      } else {
        // Wait for Adobe SDK to load
        const checkAdobeSDK = setInterval(() => {
          if (window.AdobeDC) {
            clearInterval(checkAdobeSDK);
            this.adobeDCView = new window.AdobeDC.View({
              clientId: this.clientId,
              divId: "adobe-dc-view",
            });

            this.isInitialized = true;
            console.log("✅ Adobe PDF Embed API initialized");
            resolve();
          }
        }, 100);

        // Timeout after 10 seconds
        setTimeout(() => {
          clearInterval(checkAdobeSDK);
          reject(new Error("Adobe SDK failed to load"));
        }, 10000);
      }
    });
  }

  async displayPDF(arrayBuffer, fileName) {
    if (!this.isInitialized) {
      throw new Error("Adobe PDF Embed API not initialized");
    }

    console.log("📖 Displaying PDF:", fileName);

    try {
      // Configure viewer options for optimal experience
      const viewerConfig = {
        embedMode: "FULL_WINDOW",
        showAnnotationTools: true,
        showLeftHandPanel: false, // We'll use our own sidebar
        showDownloadPDF: false, // Keep offline
        showPrintPDF: true,
        showZoomControl: true,
        showPageControls: true,
        showSearchControl: true,
        enableFormFilling: false,
        enableAnnotationAPIs: true,
        includePDFAnnotations: true,
      };

      // Display the PDF
      await this.adobeDCView.previewFile(
        {
          content: { promise: Promise.resolve(arrayBuffer) },
          metaData: { fileName: fileName },
        },
        viewerConfig
      );

      // Setup event listeners for intelligence integration
      this.setupEventListeners();

      this.currentPDF = { arrayBuffer, fileName };
      console.log("✅ PDF displayed successfully");
    } catch (error) {
      console.error("❌ PDF display failed:", error);
      throw new Error(`Failed to display PDF: ${error.message}`);
    }
  }

  setupEventListeners() {
    if (!this.adobeDCView) return;

    // Listen for page changes to update intelligence panel
    this.adobeDCView.registerCallback(
      window.AdobeDC.View.Enum.CallbackType.EVENT_LISTENER,
      (event) => {
        if (event.type === "PAGE_VIEW") {
          this.onPageChange(event.data.pageNumber);
        }
      },
      { enablePDFAnalytics: false }
    );

    // Listen for text selection for contextual insights
    this.adobeDCView.registerCallback(
      window.AdobeDC.View.Enum.CallbackType.GET_USER_PROFILE_API,
      () => {
        return new Promise((resolve) => {
          resolve({
            code: window.AdobeDC.View.Enum.ApiResponseCode.SUCCESS,
            data: {
              userProfile: {
                name: "Intelligent Reader User",
                firstName: "Intelligence",
                lastName: "Reader",
              },
            },
          });
        });
      }
    );

    // Listen for annotation events
    this.adobeDCView.registerCallback(
      window.AdobeDC.View.Enum.CallbackType.SAVE_API,
      (metaData, content, options) => {
        return new Promise((resolve) => {
          console.log("📝 PDF annotations saved");
          resolve({
            code: window.AdobeDC.View.Enum.ApiResponseCode.SUCCESS,
            data: { metaData },
          });
        });
      }
    );
  }

  onPageChange(pageNumber) {
    console.log(`📄 Page changed to: ${pageNumber}`);

    // Notify the main application about page change
    if (window.app && typeof window.app.onPageChange === "function") {
      window.app.onPageChange(pageNumber);
    }

    // Update intelligence panel with page-specific insights
    this.updatePageContext(pageNumber);
  }

  updatePageContext(pageNumber) {
    // Highlight relevant outline items
    document.querySelectorAll(".outline-item").forEach((item) => {
      item.classList.remove("active");
      if (parseInt(item.getAttribute("data-page")) === pageNumber) {
        item.classList.add("active");
      }
    });

    // Update insights for current page
    document.querySelectorAll(".insight-item").forEach((item) => {
      const insightPage = parseInt(item.getAttribute("data-page"));
      if (insightPage === pageNumber) {
        item.classList.add("current-page");
      } else {
        item.classList.remove("current-page");
      }
    });
  }

  navigateToPage(pageNumber) {
    if (!this.adobeDCView) return;

    try {
      this.adobeDCView.getAPIs().then((apis) => {
        apis
          .gotoLocation(pageNumber)
          .then(() => {
            console.log(`🔗 Navigated to page ${pageNumber}`);
          })
          .catch((error) => {
            console.error("Navigation failed:", error);
          });
      });
    } catch (error) {
      console.error("Navigation error:", error);
    }
  }

  highlightText(pageNumber, textContent) {
    if (!this.adobeDCView) return;

    try {
      this.adobeDCView.getAPIs().then((apis) => {
        // Create highlight annotation
        const annotation = {
          motivation: "highlighting",
          target: {
            selector: {
              node: {
                index: pageNumber - 1,
              },
              textQuoteSelector: {
                exact: textContent,
              },
            },
          },
          body: {
            type: "TextualBody",
            value: "Relevant to your persona",
            purpose: "commenting",
          },
        };

        apis.addAnnotation(annotation);
      });
    } catch (error) {
      console.error("Highlighting failed:", error);
    }
  }

  async searchText(query) {
    if (!this.adobeDCView) return [];

    try {
      const apis = await this.adobeDCView.getAPIs();
      const searchResults = await apis.search(query);

      console.log(`🔍 Search results for "${query}":`, searchResults);
      return searchResults;
    } catch (error) {
      console.error("Search failed:", error);
      return [];
    }
  }

  enableAnnotationMode() {
    if (!this.adobeDCView) return;

    this.adobeDCView.getAPIs().then((apis) => {
      apis.enableAnnotationAPIs().then(() => {
        console.log("✅ Annotation APIs enabled");
      });
    });
  }

  async exportPDFWithAnnotations() {
    if (!this.adobeDCView) return null;

    try {
      const apis = await this.adobeDCView.getAPIs();
      const pdfBuffer = await apis.getPDFExport();

      console.log("📁 PDF exported with annotations");
      return pdfBuffer;
    } catch (error) {
      console.error("Export failed:", error);
      return null;
    }
  }

  destroy() {
    if (this.adobeDCView) {
      // Clean up viewer instance
      const container = document.getElementById("adobe-dc-view");
      if (container) {
        container.innerHTML = "";
      }

      this.adobeDCView = null;
      this.currentPDF = null;
      console.log("🧹 Adobe PDF Embed cleaned up");
    }
  }
}

// Export for use in other modules
window.AdobePDFEmbed = AdobePDFEmbed;

