#!/bin/bash
# Run Fennec API and GUI Client together

echo "🦊 Fennec Framework - Starting API and GUI"
echo "=========================================="
echo ""

# Check if API is already running
if curl -s http://localhost:8001/health > /dev/null 2>&1; then
    echo "✓ API is already running"
    echo ""
    echo "Starting GUI Client..."
    python3 gui_client.py
else
    echo "Starting API server in background..."
    export PYTHONPATH=$PWD
    python3 main.py > /dev/null 2>&1 &
    API_PID=$!
    
    echo "Waiting for API to start..."
    sleep 3
    
    if curl -s http://localhost:8001/health > /dev/null 2>&1; then
        echo "✓ API started successfully (PID: $API_PID)"
        echo ""
        echo "Starting GUI Client..."
        python3 gui_client.py
        
        # Kill API when GUI closes
        echo ""
        echo "Stopping API server..."
        kill $API_PID 2>/dev/null
        echo "✓ Done"
    else
        echo "❌ Failed to start API"
        kill $API_PID 2>/dev/null
        exit 1
    fi
fi
