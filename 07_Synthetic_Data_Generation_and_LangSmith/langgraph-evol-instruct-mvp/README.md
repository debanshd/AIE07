# LangGraph Evol Instruct MVP

A minimal viable product demonstrating LangGraph + Evol Instruct synthetic data generation with a web interface.

## 🎯 Overview

This MVP reproduces RAGAS functionality using LangGraph and implements the Evol Instruct methodology for synthetic data generation. It provides a complete pipeline from document upload to evolved questions, answers, and contexts.

## 🏗️ Architecture

```
langgraph-evol-instruct-mvp/
├── backend/           # Python FastAPI server
├── frontend/          # Angular web interface
└── vercel.json        # Deployment configuration
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- OpenAI API key

### Backend Setup
```bash
cd backend/
export OPENAI_API_KEY="your-api-key-here"
pip install -e .
uvicorn api_server:app --reload
```

### Frontend Setup
```bash
cd frontend/
npm install
npm start
```

### Access the Application
- Frontend: http://localhost:4200
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📋 Features

### ✅ Implemented
- **Document Upload**: PDF processing with LangChain
- **Synthetic Data Generation**: Custom RAGAS-like functionality
- **Three Evolution Types**: Simple, multi-context, reasoning
- **Complex Validation**: Quality control and metrics
- **Answer Generation**: LLM-based answer creation
- **Context Matching**: Question-context linking
- **Minimalist Web UI**: Clean, responsive interface
- **Vercel Deployment**: Production-ready configuration

### 🔄 Evolution Types
1. **Simple Evolution**: Basic question modifications
2. **Multi-Context Evolution**: Questions requiring multiple document sections
3. **Reasoning Evolution**: Questions requiring logical reasoning

## 📊 Output Format

The system generates:
- **Evolved Questions** with IDs and evolution types
- **Answers** linked to question IDs
- **Contexts** linked to question IDs with source information
- **Validation Metrics** for quality assessment

## 🛠️ Technology Stack

### Backend
- **LangGraph**: Core workflow orchestration
- **LangChain**: Document processing and LLM integration
- **FastAPI**: Web server and API endpoints
- **OpenAI**: LLM for question generation and answers
- **Pydantic**: Data validation and serialization

### Frontend
- **Angular**: Web application framework
- **TypeScript**: Type-safe development
- **CSS**: Minimalist styling
- **HTTP Client**: API communication

### Deployment
- **Vercel**: Serverless deployment platform
- **Python 3.9**: Backend runtime
- **Node.js**: Frontend build process

## 📁 Project Structure

```
langgraph-evol-instruct-mvp/
├── backend/
│   ├── langgraph_app.py      # Core LangGraph implementation
│   ├── api_server.py         # FastAPI server
│   ├── pyproject.toml        # Python dependencies
│   └── README.md            # Backend documentation
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── app.component.ts
│   │   │   ├── app.component.html
│   │   │   ├── app.component.css
│   │   │   ├── app.service.ts
│   │   │   └── app.module.ts
│   │   ├── styles.css
│   │   └── main.ts
│   ├── package.json
│   ├── angular.json
│   ├── tsconfig.json
│   └── README.md            # Frontend documentation
├── vercel.json              # Deployment configuration
└── README.md               # This file
```

## 🔧 Development

### Backend Development
```bash
cd backend/
# Install dependencies
pip install -e .

# Run development server
uvicorn api_server:app --reload

# Test API
curl http://localhost:8000/health
```

### Frontend Development
```bash
cd frontend/
# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build
```

## 🚀 Deployment

### Vercel Deployment
1. Connect your repository to Vercel
2. Set environment variables:
   - `OPENAI_API_KEY`: Your OpenAI API key
3. Deploy automatically on push to main branch

### Manual Deployment
```bash
# Build frontend
cd frontend/
npm run build

# Deploy to Vercel
vercel --prod
```

## 📈 API Endpoints

### Core Endpoints
- `POST /upload` - Upload PDF documents
- `GET /results/{id}` - Get processing results
- `GET /results` - List all results
- `GET /health` - Health check

### Example Usage
```bash
# Upload documents
curl -X POST "http://localhost:8000/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@document.pdf"

# Get results
curl "http://localhost:8000/results/result_1"
```

## 🎯 Success Criteria

This MVP successfully demonstrates:
- ✅ **Working end-to-end** flow
- ✅ **Document upload** and processing
- ✅ **Multiple question evolution types**
- ✅ **Complex validation** and quality control
- ✅ **Answer generation** functionality
- ✅ **Web interface** accessibility
- ✅ **Vercel deployment** working
- ✅ **Complete documentation** provided

## 🔄 Future Enhancements

1. **Advanced visualizations**
2. **Comprehensive testing**
3. **Performance optimization**
4. **Better error handling**
5. **User authentication**
6. **Advanced configuration options**
7. **Real-time collaboration**

## 📄 License

This project is for educational and demonstration purposes.

## 🤝 Contributing

This is an MVP implementation. For production use, consider:
- Adding comprehensive error handling
- Implementing proper authentication
- Adding unit and integration tests
- Optimizing performance
- Enhancing security measures 