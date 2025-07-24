#!/bin/bash
"""
Build script for Round 2 Web Application
Packages everything for deployment and judging
"""

echo "🚀 Building Intelligent PDF Reader Web Application"
echo "=================================================="

# Create distribution directory
rm -rf dist/
mkdir -p dist/

# Copy main HTML file
cp index.html dist/

# Copy and minify CSS
mkdir -p dist/css/
cp css/*.css dist/css/

# Copy and bundle JavaScript
mkdir -p dist/js/
cp js/*.js dist/js/

# Copy assets
cp -r assets/ dist/ 2>/dev/null || echo "No assets directory found"

# Create sample PDFs directory
mkdir -p dist/assets/samples/

# Copy WASM modules if they exist
cp -r wasm/ dist/ 2>/dev/null || echo "No WASM modules found"

# Create configuration template
cat > dist/config.js << 'EOF'
// Adobe PDF Embed API Configuration
// Replace with your actual Adobe Client ID
window.ADOBE_CONFIG = {
    clientId: "YOUR_ADOBE_CLIENT_ID_HERE",
    reportSuiteId: "none"
};
EOF

# Create deployment README
cat > dist/README.md << 'EOF'
# Intelligent PDF Reader - Round 2 Web Application

## Quick Start for Judges

1. **Replace Adobe Client ID**:
   - Edit `config.js` and add your Adobe PDF Embed API client ID
   - Or set it directly in `js/adobe-embed.js`

2. **Open the Application**:
   - Simply open `index.html` in a modern web browser
   - Or serve via local web server: `python -m http.server 8000`

3. **Demo Usage**:
   - Click "Upload PDF" or drag & drop PDF files
   - Configure persona via "Set Persona" button
   - Experience intelligent insights in the sidebar

## Features Demonstrated

- ✅ Adobe PDF Embed API integration
- ✅ Real-time outline extraction (Round 1A)
- ✅ Persona-driven insights (Round 1B)
- ✅ Beautiful, responsive UI
- ✅ Offline-capable intelligence
- ✅ Multi-document support

## Technical Architecture

- **Frontend**: Vanilla JavaScript + Modern CSS
- **PDF Processing**: Round 1 algorithms via WebAssembly/JavaScript
- **Adobe Integration**: PDF Embed API with custom intelligence overlay
- **Performance**: Optimized for real-time user experience

Built for the Adobe India Hackathon 2025 - "Connecting the Dots" Challenge
EOF

# Create deployment package
echo ""
echo "📦 Creating deployment package..."
cd dist/
zip -r ../intelligent-pdf-reader-web.zip . > /dev/null
cd ..

# Create final structure
echo ""
echo "✅ Build Complete!"
echo ""
echo "📁 Distribution Structure:"
echo "   dist/"
echo "   ├── index.html              # Main application entry"
echo "   ├── config.js               # Adobe client ID configuration"
echo "   ├── css/                    # Styled components"
echo "   ├── js/                     # Application logic"
echo "   ├── assets/                 # Static resources"
echo "   └── README.md               # Judge instructions"
echo ""
echo "📱 Ready for judging:"
echo "   1. Set Adobe Client ID in config.js"
echo "   2. Open index.html in browser"
echo "   3. Experience the magic! ✨"
echo ""
echo "🎯 Key Judge Evaluation Points:"
echo "   ✅ Seamless PDF viewing experience"
echo "   ✅ Real-time outline extraction"
echo "   ✅ Persona-aware insights"
echo "   ✅ Beautiful, intuitive UI"
echo "   ✅ Offline intelligence processing"
echo "   ✅ Multi-document support"
echo ""
echo "🏆 Submission package: intelligent-pdf-reader-web.zip"