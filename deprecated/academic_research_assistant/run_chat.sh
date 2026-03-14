#!/bin/bash
# Quick Start Script for Academic Research Assistant

echo "🚀 Starting Academic Research Assistant..."
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/.."

# Check if .env exists in the academic_research_assistant directory
if [ ! -f "academic_research_assistant/.env" ]; then
    echo "⚠️  Warning: .env file not found at academic_research_assistant/.env"
    echo "Please ensure GOOGLE_API_KEY is set in your environment"
    echo ""
fi

# Load the .env file if it exists
if [ -f "academic_research_assistant/.env" ]; then
    export $(cat academic_research_assistant/.env | xargs)
fi

# Run the interactive chat
export PYTHONPATH=$PYTHONPATH:.
python3.11 -c "import asyncio; from academic_research_assistant.main import run_chat; asyncio.run(run_chat())"
