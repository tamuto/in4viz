# In4viz Examples

This directory contains examples demonstrating how to use the In4viz infrastructure visualization library.

## Examples

### 1. Basic Usage Example (Node.js)

To run the basic usage example:

```bash
cd /workspaces/claude/in4viz
node examples/basic-usage.js
```

This example demonstrates:
- Creating an In4viz instance
- Defining infrastructure data (VPC, subnet, EC2 instance)
- Rendering an SVG diagram
- Using AWS provider helpers

### 2. Browser Demo (Interactive)

To view the interactive browser demo:

```bash
# Start a local server
cd /workspaces/claude/in4viz
python3 -m http.server 8080

# Open in browser
open http://localhost:8080/examples/browser-demo.html
```

The browser demo features:
- 🚀 **Interactive UI** - Render diagrams with button clicks
- 🎨 **Live Visualization** - See infrastructure diagrams in real-time
- 📊 **Multiple Examples** - Basic and complex infrastructure scenarios
- 💾 **SVG Export** - Download generated diagrams
- 📱 **Responsive Design** - Works on desktop and mobile
- 🔧 **Live Code Samples** - See the code used to generate each diagram
- ⚡ **Performance Metrics** - Track rendering time and resource counts

#### Browser Demo Features

1. **Basic Demo**: Simple AWS infrastructure (VPC → Subnet → EC2)
2. **Complex Demo**: Multi-tier architecture with load balancers, databases, and multiple instances
3. **SVG Export**: Download diagrams as SVG files
4. **Real-time Statistics**: Resource count, connection count, and render time
5. **Code Examples**: View the exact code used for each demo

## Core Package Status

✅ **BUILD SUCCESSFUL** - The In4viz core package has been successfully built and is fully functional!

### Built Artifacts
- `packages/core/dist/index.js` (CommonJS, 51.85 KB)
- `packages/core/dist/index.mjs` (ESM, 51.43 KB) 
- `packages/core/dist/index.d.ts` (TypeScript declarations, 27.86 KB)

### Available Exports
```javascript
const {
  In4viz,                    // Main library class
  AWSProvider,               // AWS resource helpers
  AzureProvider,             // Azure resource helpers  
  GCPProvider,               // GCP resource helpers
  GeometryUtils,             // Geometry calculations
  LayoutManager,             // Layout management
  DefaultSVGRenderer,        // SVG rendering
  IconRegistry,              // Icon management
  DataValidator,             // Data validation
  DataNormalizer,            // Data normalization
  HierarchicalLayoutEngine,  // Layout algorithm
  SVGUtils,                  // SVG utilities
  themes,                    // Predefined themes
  VERSION                    // Library version
} = require('@infodb/in4viz');
```

### Completed Features
- ✅ TypeScript type definitions for all infrastructure resources
- ✅ SVG rendering engine with themes and utilities
- ✅ Hierarchical layout engine for automatic positioning
- ✅ AWS/Azure/GCP provider helpers
- ✅ Geometry utilities for calculations
- ✅ Icon registry system
- ✅ Data validation and normalization
- ✅ Main In4viz library interface
- ✅ Full ESM and CommonJS support
- ✅ TypeScript declaration files
