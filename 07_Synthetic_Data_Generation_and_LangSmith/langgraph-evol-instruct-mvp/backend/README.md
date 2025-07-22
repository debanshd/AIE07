# Backend Documentation

## Overview
This backend implements LangGraph + Evol Instruct synthetic data generation using FastAPI.

## Setup

### Prerequisites
- Python 3.9+
- OpenAI API key

### Installation
```bash
cd backend/
pip install -e .
```

### Environment Variables
Set your OpenAI API key (optional - can also be set via API):
```bash
export OPENAI_API_KEY="your-api-key-here"
```

## API Endpoints

### Root
- **GET** `/` - Health check and API info

### API Key Management
- **POST** `/set-api-key` - Set OpenAI API key for the session
  - **Body**: `api_key` (form data)
  - **Returns**: Success message
- **GET** `/api-key-status` - Check if API key is set
  - **Returns**: `{"has_api_key": boolean}`

### Upload Documents
- **POST** `/upload` - Upload PDF documents for processing
  - **Files**: List of PDF files
  - **api_key** (optional): OpenAI API key (if not set globally)
  - **Returns**: Processing status and result ID

### Results
- **GET** `/results/{result_id}` - Get specific results
- **GET** `/results` - List all available results

### Health
- **GET** `/health` - Health check endpoint

## Usage

### Start the server
```bash
cd backend/
uvicorn api_server:app --reload
```

### Test with curl
```bash
# Set API key
curl -X POST "http://localhost:8000/set-api-key" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "api_key=your-openai-api-key"

# Check API key status
curl "http://localhost:8000/api-key-status"

# Upload a PDF
curl -X POST "http://localhost:8000/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@your-document.pdf"

# Get results
curl "http://localhost:8000/results/result_1"
```

## Architecture

### Files
- `langgraph_app.py` - Core LangGraph implementation
- `api_server.py` - FastAPI server and endpoints
- `pyproject.toml` - Dependencies and project configuration

### Components
1. **Document Processing** - PDF loading and chunking
2. **Question Generation** - Base question creation
3. **Evolution Types** - Simple, multi-context, reasoning
4. **Answer Generation** - LLM-based answer creation
5. **Context Matching** - Question-context linking
6. **Validation** - Quality control and metrics
7. **API Key Management** - Secure API key handling

## Output Format
```json
{
  "evolved_questions": [
    {
      "id": "ev_12345678",
      "question": "How does Title IV affect student loans?",
      "evolution_type": "simple",
      "quality_score": 0.85,
      "validation_status": "passed"
    }
  ],
  "answers": [
    {
      "question_id": "ev_12345678",
      "answer": "Title IV affects student loans by...",
      "accuracy_score": 0.88
    }
  ],
  "contexts": [
    {
      "question_id": "ev_12345678",
      "context": "Title IV of the Higher Education Act...",
      "source_document": "document.pdf",
      "page_number": 1
    }
  ],
  "validation_metrics": {
    "total_questions": 10,
    "passed_validation": 8,
    "average_quality_score": 0.87,
    "evolution_type_distribution": {
      "simple": 4,
      "multi_context": 3,
      "reasoning": 3
    }
  }
}
```

## Security Notes

- API keys are stored in memory for the session only
- No persistent storage of API keys
- API keys can be set via environment variable or API endpoint
- For production, implement proper authentication and secure storage 