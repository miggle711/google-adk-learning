# Academic Research Assistant - Deployment Guide

## Local Testing

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables
Create a `.env` file:
```
GOOGLE_API_KEY=your_api_key_here
```

### 3. Run the API Server
```bash
python -m uvicorn academic_research_assistant.api:app --reload
```

### 4. Test the API
```bash
curl -X POST http://localhost:8000/research \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the latest advances in transformer architectures?"}'
```

## Deployment to Vertex AI Agent Engine

### Prerequisites
1. Google Cloud account with billing enabled
2. Enable required APIs:
   - Vertex AI API
   - Cloud Storage API
   - Cloud Build API
   - Artifact Registry API

### Deploy Using ADK CLI

```bash
# Set your project and region
export PROJECT_ID=your-project-id
export REGION=us-central1

# Deploy the agent
adk deploy agent_engine \
  --project=$PROJECT_ID \
  --region=$REGION \
  academic_research_assistant \
  --agent_engine_config_file=.agent_engine_config.json
```

## Deployment to Cloud Run

### 1. Build and Push Docker Image
```bash
gcloud builds submit --tag gcr.io/$PROJECT_ID/research-assistant
```

### 2. Deploy to Cloud Run
```bash
gcloud run deploy research-assistant \
  --image gcr.io/$PROJECT_ID/research-assistant \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY=$GOOGLE_API_KEY
```

## API Endpoints

- `POST /research` - Submit a research query
- `GET /health` - Health check endpoint

## Cost Management

- Use `gemini-2.5-flash-lite` for cost-effective operations
- Set `min_instances: 0` in production to scale to zero
- Monitor API usage through Google Cloud Console
