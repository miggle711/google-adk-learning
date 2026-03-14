#!/bin/bash
# Start the FastAPI server

echo "🌐 Starting Academic Research Assistant API..."
echo "API will be available at: http://localhost:8000"
echo "Docs available at: http://localhost:8000/docs"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/.."

# Load the .env file if it exists
if [ -f "academic_research_assistant/.env" ]; then
    export $(cat academic_research_assistant/.env | xargs)
fi

export PYTHONPATH=$PYTHONPATH:.
python3.11 -m uvicorn academic_research_assistant.api:app --reload --host 0.0.0.0 --port 8000
