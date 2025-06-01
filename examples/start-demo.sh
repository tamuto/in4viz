#!/bin/bash

# In4viz Browser Demo Launcher
# This script starts a local server and opens the browser demo

echo "🚀 Starting In4viz Browser Demo..."
echo ""

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not found. Please install Python 3."
    exit 1
fi

# Navigate to the project directory
cd "$(dirname "$0")/.."

# Start the HTTP server in the background
echo "🌐 Starting HTTP server on port 8080..."
python3 -m http.server 8080 &
SERVER_PID=$!

# Wait a moment for the server to start
sleep 2

echo "✅ Server started successfully (PID: $SERVER_PID)"
echo ""
echo "🎯 Browser demo is now available at:"
echo "   http://localhost:8080/examples/browser-demo.html"
echo ""
echo "📋 Available demos:"
echo "   • Basic AWS Infrastructure Demo"
echo "   • Complex Multi-tier Architecture Demo"
echo "   • Interactive SVG Export"
echo ""
echo "💡 To stop the server, press Ctrl+C or run:"
echo "   kill $SERVER_PID"
echo ""

# Try to open in default browser if available
if command -v "$BROWSER" &> /dev/null; then
    echo "🌍 Opening in browser..."
    "$BROWSER" "http://localhost:8080/examples/browser-demo.html" &
elif command -v xdg-open &> /dev/null; then
    echo "🌍 Opening in browser..."
    xdg-open "http://localhost:8080/examples/browser-demo.html" &
elif command -v open &> /dev/null; then
    echo "🌍 Opening in browser..."
    open "http://localhost:8080/examples/browser-demo.html" &
else
    echo "ℹ️  Please open the URL manually in your browser"
fi

# Wait for the server process
wait $SERVER_PID
