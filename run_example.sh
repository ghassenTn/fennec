#!/bin/bash
# Script to run the example application

export PYTHONPATH=$PWD
echo "Starting Simple API Example..."
echo "API Documentation will be available at: http://localhost:8001/docs"
echo "Press CTRL+C to stop"
echo ""
python examples/simple_api/main.py
