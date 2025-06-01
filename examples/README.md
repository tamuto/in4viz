# In4viz Examples

This directory contains examples demonstrating how to use the In4viz infrastructure visualization library.

## Basic Usage Example

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
