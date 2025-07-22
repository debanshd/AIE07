from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import tempfile
import os
import json
import uuid
from datetime import datetime
from typing import List, Optional, Dict

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

# Progress tracking storage
processing_progress = {}

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
    files: List[UploadFile] = File(...),
    api_key: Optional[str] = Form(None)
):
    """Upload documents for processing - Simplified MVP version"""
    try:
        # Use provided API key or fall back to stored one
        api_key_to_use = api_key or current_api_key
        
        if not api_key_to_use:
            raise HTTPException(status_code=400, detail="API key is required. Please set it first.")
        
        # Generate unique task ID for progress tracking
        task_id = str(uuid.uuid4())
        
        # Initialize progress tracking
        processing_progress[task_id] = {
            "task_id": task_id,
            "status": "starting",
            "step": "Initializing",
            "step_number": 0,
            "total_steps": 5,
            "percentage": 0,
            "details": "Preparing to process documents...",
            "timestamp": datetime.now().isoformat(),
            "files_count": len(files)
        }
        
        # Simulate processing steps
        steps = [
            "Processing documents...",
            "Generating synthetic questions...",
            "Applying evolution techniques...",
            "Validating results...",
            "Finalizing output..."
        ]
        
        for i, step in enumerate(steps):
            processing_progress[task_id].update({
                "step": step,
                "step_number": i + 1,
                "percentage": int(((i + 1) / len(steps)) * 100),
                "details": f"Completed: {step}",
                "timestamp": datetime.now().isoformat()
            })
            
            # Simulate processing time
            import asyncio
            await asyncio.sleep(1)
        
        # Generate mock results for MVP demonstration
        result_id = str(uuid.uuid4())
        
        # Mock evolved questions based on common educational topics
        evolved_questions = [
            {
                "id": "ev_001",
                "question": "How does Title IV affect student loan eligibility and repayment terms?",
                "evolution_type": "simple",
                "quality_score": 0.85,
                "validation_status": "passed"
            },
            {
                "id": "ev_002", 
                "question": "What are the implications of clinical work overlapping academic terms on financial aid packaging?",
                "evolution_type": "reasoning",
                "quality_score": 0.92,
                "validation_status": "passed"
            },
            {
                "id": "ev_003",
                "question": "How do different academic calendar structures impact Pell Grant calculations across multiple institutions?",
                "evolution_type": "multi_context",
                "quality_score": 0.88,
                "validation_status": "passed"
            }
        ]
        
        # Mock answers
        answers = [
            {
                "question_id": "ev_001",
                "answer": "Title IV of the Higher Education Act of 1965 authorizes federal student aid programs including Pell Grants, Direct Loans, and work-study. It affects eligibility through need-based calculations and repayment through income-driven plans.",
                "accuracy_score": 0.88
            },
            {
                "question_id": "ev_002",
                "answer": "Clinical work overlapping terms may not be included in standard term calculations unless it meets specific criteria for academic credit and duration, affecting how financial aid is packaged across terms.",
                "accuracy_score": 0.91
            },
            {
                "question_id": "ev_003",
                "answer": "Different academic calendar structures (semester vs. quarter vs. trimester) impact Pell Grant calculations by affecting the number of payment periods and the amount disbursed per period.",
                "accuracy_score": 0.87
            }
        ]
        
        # Mock contexts - demonstrating multi-context support
        contexts = [
            {
                "question_id": "ev_001",
                "context": "Title IV of the Higher Education Act of 1965 authorizes federal student aid programs...",
                "contexts": ["Title IV of the Higher Education Act of 1965 authorizes federal student aid programs..."],
                "source_document": files[0].filename if files else "uploaded_document.pdf",
                "page_number": 5,
                "context_count": 1,
                "is_multi_context": False
            },
            {
                "question_id": "ev_002",
                "context": "Clinical work conducted outside the classroom may not be included in a standard term unless...",
                "contexts": ["Clinical work conducted outside the classroom may not be included in a standard term unless..."],
                "source_document": files[0].filename if files else "uploaded_document.pdf",
                "page_number": 12,
                "context_count": 1,
                "is_multi_context": False
            },
            {
                "question_id": "ev_003",
                "context": "Academic calendars vary by institution and can include semester, quarter, or trimester systems... | Pell Grant calculations are affected by academic calendar structure... | Different institutions may have varying payment periods...",
                "contexts": [
                    "Academic calendars vary by institution and can include semester, quarter, or trimester systems. Each system affects how financial aid is calculated and disbursed throughout the academic year.",
                    "Pell Grant calculations are affected by academic calendar structure, with semester systems typically having two payment periods while quarter systems may have three or four payment periods.",
                    "Different institutions may have varying payment periods that must align with federal regulations for Title IV aid disbursement and student enrollment status."
                ],
                "source_document": files[0].filename if files else "uploaded_document.pdf",
                "page_number": 8,
                "context_count": 3,
                "is_multi_context": True
            }
        ]
        
        # Store results
        processing_results[result_id] = {
            "result_id": result_id,
            "task_id": task_id,
            "evolved_questions": evolved_questions,
            "answers": answers,
            "contexts": contexts,
            "validation_metrics": {
                "total_questions": len(evolved_questions),
                "passed_validation": len(evolved_questions),
                "average_quality_score": 0.88,
                "evolution_type_distribution": {
                    "simple": 1,
                    "multi_context": 1,
                    "reasoning": 1
                }
            },
            "timestamp": datetime.now().isoformat(),
            "files_processed": [f.filename for f in files]
        }
        
        # Mark as completed
        processing_progress[task_id]["status"] = "completed"
        processing_progress[task_id]["percentage"] = 100
        processing_progress[task_id]["details"] = "Processing completed successfully"
        
        return {
            "message": "Documents processed successfully",
            "task_id": task_id,
            "result_id": result_id,
            "status": "completed"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.get("/results/{result_id}")
async def get_results(result_id: str):
    """Get results for a specific processing task"""
    if result_id not in processing_results:
        raise HTTPException(status_code=404, detail="Result not found")
    
    return processing_results[result_id]

@app.get("/results")
async def list_results():
    """List all available results"""
    return {
        "results": [
            {
                "result_id": result_id,
                "timestamp": data["timestamp"],
                "files_processed": data["files_processed"]
            }
            for result_id, data in processing_results.items()
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    ) 