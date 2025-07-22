from fastapi import FastAPI, UploadFile, File, HTTPException, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from langchain.schema import Document
from langchain_community.document_loaders import PyPDFLoader
import tempfile
import os
import pandas as pd
from typing import List, Optional, Dict
from langgraph_app import LangGraphEvolInstruct
import json
import uuid
import asyncio
from datetime import datetime

app = FastAPI(title="LangGraph Evol Instruct MVP", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global storage for results and API key (in production, use a proper database)
processing_results = {}
current_api_key = None
processing_progress = {}

# 🤖 Enhanced: Agent step tracking storage
agent_steps_storage = {}  # task_id -> list of agent steps

# Background processing function
def run_processing_pipeline(task_id: str, documents: List[Document], api_key: str):
    """Run the LangGraph processing pipeline in background"""
    try:
        # 🤖 Enhanced: Agent step tracking function
        def add_agent_step(agent_type: str, status: str, details: str, **kwargs):
            """Add a persistent agent step to the tracking system"""
            if task_id not in agent_steps_storage:
                agent_steps_storage[task_id] = []
            
            step_id = len(agent_steps_storage[task_id]) + 1
            agent_step = {
                "step_id": step_id,
                "timestamp": datetime.now().isoformat(),
                "agent_type": agent_type,
                "status": status,
                "details": details,
                **kwargs  # Additional fields like agent_message, question_preview, etc.
            }
            
            agent_steps_storage[task_id].append(agent_step)
            
            # Update progress with latest agent steps
            if task_id in processing_progress:
                processing_progress[task_id]["agent_steps"] = agent_steps_storage[task_id]
                processing_progress[task_id]["total_agent_steps"] = len(agent_steps_storage[task_id])

        # Progress callback function
        def update_progress(progress_data: Dict):
            if task_id in processing_progress:
                processing_progress[task_id].update(progress_data)
                processing_progress[task_id]["timestamp"] = datetime.now().isoformat()
                
                # Always include current agent steps in progress updates
                if task_id in agent_steps_storage:
                    processing_progress[task_id]["agent_steps"] = agent_steps_storage[task_id]
                    processing_progress[task_id]["total_agent_steps"] = len(agent_steps_storage[task_id])
        
        # 🤖 Enhanced: Initialize agent step tracking
        add_agent_step("system", "initializing", "Initializing LangGraph Evol Instruct pipeline", 
                      agent_message="Starting synthetic data generation process")
        
        # Initialize LangGraph with API key and enhanced callbacks
        langgraph_app = LangGraphEvolInstruct(api_key=api_key, progress_callback=update_progress)
        
        # Add document processing agent step
        add_agent_step("document", "processing", f"Document Agent processing {len(documents)} documents", 
                      agent_message=f"Loaded and analyzing {len(documents)} documents for content extraction")
        
        # Update progress before starting
        update_progress({
            "status": "processing_pipeline",
            "step": "Processing Documents",
            "step_number": 2,
            "percentage": 30,
            "details": f"Running Evol Instruct pipeline on {len(documents)} documents"
        })
        
        # Add question generation agent step  
        add_agent_step("question", "analyzing", "Question Agent analyzing document patterns", 
                      agent_message="Extracting key concepts and generating base questions from document content")
        
        # Process documents using LangGraph (this is the blocking operation)
        add_agent_step("orchestrator", "processing", "Orchestrator Agent coordinating evolution pipeline", 
                      agent_message="Managing the evolution process across different agent types")
        
        result = langgraph_app.process_pipeline(documents)
        
        # Add completion agent steps
        add_agent_step("validation", "completed", "Validation Agent completed quality assessment", 
                      agent_message=f"Validated {len(result.get('evolved_questions', []))} evolved questions")
        
        add_agent_step("answer_generator", "completed", "Answer Generator completed response synthesis", 
                      agent_message=f"Generated comprehensive answers for all evolved questions")
        
        # Update progress to completed
        result_id = f"result_{len(processing_results) + 1}"
        processing_results[result_id] = result
        
        update_progress({
            "status": "completed",
            "step": "Complete",
            "step_number": 7,
            "total_steps": 7,
            "percentage": 100,
            "details": "Processing completed successfully!",
            "result_id": result_id
        })
        
    except Exception as e:
        # 🤖 Enhanced: Add error agent step
        if task_id in agent_steps_storage or task_id in processing_progress:
            add_agent_step("system", "error", f"Processing pipeline encountered an error", 
                          agent_message=f"Error occurred: {str(e)}", error=str(e))
        
        # Update progress to error
        if task_id in processing_progress:
            processing_progress[task_id].update({
                "status": "error",
                "details": f"Processing failed: {str(e)}"
            })

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "LangGraph Evol Instruct MVP API", "status": "running"}

@app.post("/set-api-key")
async def set_api_key(api_key: str = Form(...)):
    """Set the OpenAI API key"""
    global current_api_key
    current_api_key = api_key
    return {"message": "API key set successfully"}

@app.post("/clear-api-key")
async def clear_api_key():
    """Clear the stored OpenAI API key"""
    global current_api_key
    current_api_key = None
    return {"message": "API key cleared successfully"}

@app.get("/api-key-status")
async def get_api_key_status():
    """Check if API key is set"""
    return {"has_api_key": current_api_key is not None}

@app.get("/progress/{task_id}")
async def get_progress(task_id: str):
    """Get progress for a specific task"""
    if task_id not in processing_progress:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return processing_progress[task_id]

@app.post("/upload")
async def upload_documents(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    api_key: Optional[str] = Form(None)
):
    """Upload PDF and CSV documents for processing"""
    try:
        # Use provided API key or fall back to stored one
        api_key_to_use = api_key or current_api_key
        
        if not api_key_to_use:
            raise HTTPException(status_code=400, detail="API key is required. Please set it first.")
        
        # Generate unique task ID for progress tracking
        task_id = str(uuid.uuid4())
        
        # 🤖 Enhanced: Initialize progress tracking with agent steps
        processing_progress[task_id] = {
            "task_id": task_id,
            "status": "starting",
            "step": "Initializing",
            "step_number": 0,
            "total_steps": 7,
            "percentage": 0,
            "details": "Preparing to process documents...",
            "timestamp": datetime.now().isoformat(),
            "files_count": len(files),
            "agent_steps": [],
            "total_agent_steps": 0
        }
        
        # Initialize agent steps storage for this task
        agent_steps_storage[task_id] = []
        
        # We'll process files first, then start background processing
        
        documents = []
        
        # Update progress for file processing
        processing_progress[task_id].update({
            "status": "processing_files",
            "step": "Processing Files",
            "step_number": 0,
            "percentage": 10,
            "details": f"Processing {len(files)} files..."
        })
        
        for i, file in enumerate(files):
            file_extension = file.filename.lower().split('.')[-1]
            
            if file_extension not in ['pdf', 'csv']:
                raise HTTPException(status_code=400, detail=f"File {file.filename} is not a supported format. Please upload PDF or CSV files only.")
            
            # Update progress for each file
            processing_progress[task_id].update({
                "details": f"Processing file {i+1}/{len(files)}: {file.filename}"
            })
            
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_extension}') as tmp_file:
                content = await file.read()
                tmp_file.write(content)
                tmp_file_path = tmp_file.name
            
            try:
                if file_extension == 'pdf':
                    # Load PDF using PyPDFLoader
                    loader = PyPDFLoader(tmp_file_path)
                    file_documents = loader.load()
                    
                    # Add source metadata
                    for doc in file_documents:
                        doc.metadata["source"] = file.filename
                        doc.metadata["file_type"] = "pdf"
                    
                    documents.extend(file_documents)
                    
                elif file_extension == 'csv':
                    # Load CSV using pandas
                    df = pd.read_csv(tmp_file_path)
                    
                    # Convert CSV to documents
                    csv_documents = []
                    for index, row in df.iterrows():
                        # Create a document from each row
                        content = " | ".join([f"{col}: {val}" for col, val in row.items() if pd.notna(val)])
                        if content.strip():  # Only add non-empty rows
                            doc = Document(
                                page_content=content,
                                metadata={
                                    "source": file.filename,
                                    "file_type": "csv",
                                    "row_index": index,
                                    "columns": list(df.columns)
                                }
                            )
                            csv_documents.append(doc)
                    
                    documents.extend(csv_documents)
                
            finally:
                # Clean up temporary file
                os.unlink(tmp_file_path)
        
        if not documents:
            raise HTTPException(status_code=400, detail="No valid documents found")
        
        # Update progress before starting background processing
        processing_progress[task_id].update({
            "status": "processing_files",
            "step": "Files Loaded",
            "step_number": 1,
            "percentage": 20,
            "details": f"Loaded {len(documents)} documents, starting processing pipeline..."
        })
        
        # Start background processing (non-blocking)
        background_tasks.add_task(run_processing_pipeline, task_id, documents, api_key_to_use)
        
        # Return immediately with task ID for progress tracking
        return {
            "message": "Upload successful, processing started",
            "task_id": task_id,
            "total_documents": len(documents),
            "status": "processing"
        }
    
    except Exception as e:
        # Handle any other errors
        if 'task_id' in locals() and task_id in processing_progress:
            processing_progress[task_id].update({
                "status": "error",
                "details": f"Error: {str(e)}"
            })
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/results/{result_id}")
async def get_results(result_id: str):
    """Get processing results by ID"""
    if result_id not in processing_results:
        raise HTTPException(status_code=404, detail="Results not found")
    
    return processing_results[result_id]

@app.get("/results")
async def list_results():
    """List all available results"""
    return {
        "available_results": list(processing_results.keys()),
        "total_results": len(processing_results)
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "LangGraph Evol Instruct MVP"}

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 