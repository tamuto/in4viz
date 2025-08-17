#!/bin/bash

# In4viz ER Diagram Browser Demo Server
echo "🚀 Starting In4viz ER Diagram Demo Server..."

# Move to project root
cd "$(dirname "$0")/.."

# Check if packages are built
if [ ! -f "packages/core/dist/index.mjs" ]; then
    echo "📦 Building packages first..."
    pnpm build
fi

# Get the current directory (project root)
DEMO_DIR=$(pwd)

echo "📁 Serving from: $DEMO_DIR (project root)"
echo "🌐 ER Demo URL: http://localhost:8080/examples/er-browser-demo.html"
echo "🔍 Debug URL: http://localhost:8080/examples/debug-test.html"
echo ""
echo "Press Ctrl+C to stop the server"

# Start a simple HTTP server
if command -v python3 &> /dev/null; then
    echo "🐍 Using Python 3 HTTP server..."
    python3 -m http.server 8080
elif command -v python &> /dev/null; then
    echo "🐍 Using Python 2 HTTP server..."
    python -m SimpleHTTPServer 8080
elif command -v node &> /dev/null; then
    echo "📦 Using Node.js HTTP server..."
    npx serve -p 8080 .
else
    echo "❌ No suitable HTTP server found. Please install Python or Node.js."
    exit 1
fi