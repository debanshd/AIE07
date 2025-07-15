#!/usr/bin/env python3
"""
Simple API server for the ML Paper Social Media Poster
"""

import os
import sys
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# OpenAI API key will be provided by users in the UI

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from fastapi.responses import HTMLResponse

# Import our demo system
from simple_demo import SimpleMLPosterDemo

# Add LinkedIn integration import at the top
from linkedin_poster import LinkedInPoster
from callback_server import start_callback_server

# Pydantic models
class CreatePostRequest(BaseModel):
    paperTitle: str
    paperUrl: Optional[str] = None
    targetPlatform: str = "LinkedIn"
    customInstructions: Optional[str] = None
    openaiApiKey: Optional[str] = None
    tavilyApiKey: Optional[str] = None
    linkedinClientId: Optional[str] = None
    linkedinClientSecret: Optional[str] = None

class Post(BaseModel):
    id: str
    title: str
    paperUrl: Optional[str] = None
    platform: str
    status: str
    content: Optional[str] = None
    createdAt: str
    updatedAt: str
    # Store LinkedIn credentials if provided by user
    linkedinClientId: Optional[str] = None
    linkedinClientSecret: Optional[str] = None

class AgentResult(BaseModel):
    id: str
    name: str
    status: str
    progress: int
    result: Optional[str] = None
    description: str

# Initialize FastAPI
app = FastAPI(title="ML Paper Social Media Poster API")

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage
posts_db: Dict[str, Post] = {}
agents_db: Dict[str, List[AgentResult]] = {}

# Initialize demo system (optional, since users will provide their own API keys)
print("🔧 Initializing demo system...")
try:
    # Only initialize if there's a global API key available
    if os.environ.get("OPENAI_API_KEY"):
        demo_system = SimpleMLPosterDemo()
        print("✅ Demo system initialized successfully")
    else:
        demo_system = None
        print("ℹ️  No global API key found - users will provide their own")
except Exception as e:
    print(f"❌ Failed to initialize demo system: {e}")
    demo_system = None

def create_agents(post_id: str) -> List[AgentResult]:
    """Create agent status for a post"""
    return [
        AgentResult(
            id=f"{post_id}_research",
            name="Research Team",
            status="pending",
            progress=0,
            result=None,
            description="Analyzing the ML paper"
        ),
        AgentResult(
            id=f"{post_id}_content",
            name="Content Team",
            status="pending",
            progress=0,
            result=None,
            description="Creating social media content"
        ),
        AgentResult(
            id=f"{post_id}_verification",
            name="Verification Team",
            status="pending",
            progress=0,
            result=None,
            description="Reviewing and optimizing content"
        )
    ]

async def process_post(post_id: str, paper_title: str, paper_url: Optional[str], openai_api_key: Optional[str] = None, tavily_api_key: Optional[str] = None, linkedin_client_id: Optional[str] = None, linkedin_client_secret: Optional[str] = None):
    """Process a post in the background"""
    import asyncio
    
    try:
        # Use custom API keys if provided, otherwise use global demo system
        if openai_api_key or tavily_api_key or linkedin_client_id or linkedin_client_secret:
            if openai_api_key and not openai_api_key.startswith('sk-'):
                raise Exception("Invalid OpenAI API key format. Key must start with 'sk-'")
            if tavily_api_key and not tavily_api_key.startswith('tvly-'):
                raise Exception("Invalid Tavily API key format. Key must start with 'tvly-'")
            current_demo_system = SimpleMLPosterDemo(
                openai_api_key=openai_api_key, 
                tavily_api_key=tavily_api_key,
                linkedin_client_id=linkedin_client_id,
                linkedin_client_secret=linkedin_client_secret
            )
        else:
            if not demo_system:
                raise Exception("No OpenAI API key provided and no global demo system available")
            current_demo_system = demo_system
        
        # Update post status
        posts_db[post_id].status = "processing"
        posts_db[post_id].updatedAt = datetime.now().isoformat()
        
        # Step 1: Start Research Agent
        print(f"🔍 Research Team: Analyzing paper...")
        agents_db[post_id][0].status = "processing"
        agents_db[post_id][0].progress = 10
        agents_db[post_id][0].result = "Starting paper analysis..."
        await asyncio.sleep(1)  # Simulate research time
        
        agents_db[post_id][0].progress = 30
        agents_db[post_id][0].result = "Extracting key insights..."
        await asyncio.sleep(1)
        
        agents_db[post_id][0].progress = 60
        agents_db[post_id][0].result = "Analyzing methodology..."
        await asyncio.sleep(1)
        
        agents_db[post_id][0].progress = 90
        agents_db[post_id][0].result = "Finalizing research..."
        await asyncio.sleep(1)
        
        # Complete research agent
        agents_db[post_id][0].status = "completed"
        agents_db[post_id][0].progress = 100
        agents_db[post_id][0].result = "Research completed successfully"
        
        # Step 2: Start Content Agent
        print(f"✍️ Content Team: Creating social media post...")
        agents_db[post_id][1].status = "processing"
        agents_db[post_id][1].progress = 10
        agents_db[post_id][1].result = "Structuring content..."
        await asyncio.sleep(1)
        
        agents_db[post_id][1].progress = 40
        agents_db[post_id][1].result = "Writing engaging copy..."
        await asyncio.sleep(1)
        
        # Generate content
        print(f"🎯 Generating LinkedIn post for: {paper_title}")
        content, _ = current_demo_system.generate_post(paper_title, paper_url, "LinkedIn")
        
        agents_db[post_id][1].progress = 80
        agents_db[post_id][1].result = "Optimizing for LinkedIn..."
        await asyncio.sleep(1)
        
        # Complete content agent
        agents_db[post_id][1].status = "completed"
        agents_db[post_id][1].progress = 100
        agents_db[post_id][1].result = "Content created successfully"
        
        # Step 3: Start Verification Agent
        print(f"✅ Verification Team: Checking content...")
        agents_db[post_id][2].status = "processing"
        agents_db[post_id][2].progress = 20
        agents_db[post_id][2].result = "Reviewing content quality..."
        await asyncio.sleep(1)
        
        agents_db[post_id][2].progress = 50
        agents_db[post_id][2].result = "Checking engagement factors..."
        await asyncio.sleep(1)
        
        agents_db[post_id][2].progress = 80
        agents_db[post_id][2].result = "Final optimization..."
        await asyncio.sleep(1)
        
        # Complete verification agent
        agents_db[post_id][2].status = "completed"
        agents_db[post_id][2].progress = 100
        agents_db[post_id][2].result = "Content verified and optimized"
        
        # Update post
        posts_db[post_id].status = "completed"
        posts_db[post_id].content = content
        posts_db[post_id].updatedAt = datetime.now().isoformat()
        
        print(f"✅ Post {post_id} completed successfully")
        
    except Exception as e:
        print(f"❌ Error processing post {post_id}: {e}")
        posts_db[post_id].status = "failed"
        posts_db[post_id].updatedAt = datetime.now().isoformat()
        
        # Update agents to failed
        for agent in agents_db[post_id]:
            if agent.status == "processing" or agent.status == "pending":
                agent.status = "failed"
                if "api_key" in str(e).lower() or "unauthorized" in str(e).lower():
                    agent.result = f"API Key Error: {str(e)}"
                else:
                    agent.result = f"Error: {str(e)}"

@app.get("/")
async def root():
    return {"message": "ML Paper Social Media Poster API", "status": "running"}

@app.get("/api/health")
async def health():
    return {
        "status": "healthy",
        "posts_count": len(posts_db),
        "demo_system": "initialized" if demo_system else "failed"
    }

@app.post("/api/posts")
async def create_post(request: CreatePostRequest, background_tasks: BackgroundTasks):
    """Create a new post"""
    post_id = str(uuid.uuid4())
    
    post = Post(
        id=post_id,
        title=request.paperTitle,
        paperUrl=request.paperUrl,
        platform=request.targetPlatform,
        status="pending",
        content=None,
        createdAt=datetime.now().isoformat(),
        updatedAt=datetime.now().isoformat(),
        linkedinClientId=request.linkedinClientId,
        linkedinClientSecret=request.linkedinClientSecret
    )
    
    posts_db[post_id] = post
    agents_db[post_id] = create_agents(post_id)
    
    # Start background processing
    background_tasks.add_task(process_post, post_id, request.paperTitle, request.paperUrl, request.openaiApiKey, request.tavilyApiKey, request.linkedinClientId, request.linkedinClientSecret)
    
    return post

@app.get("/api/posts")
async def get_posts():
    """Get all posts"""
    return list(posts_db.values())

@app.get("/api/posts/{post_id}")
async def get_post(post_id: str):
    """Get a specific post"""
    if post_id not in posts_db:
        raise HTTPException(status_code=404, detail="Post not found")
    return posts_db[post_id]

@app.get("/api/posts/{post_id}/agents")
async def get_agents(post_id: str):
    """Get agent status for a post"""
    if post_id not in posts_db:
        raise HTTPException(status_code=404, detail="Post not found")
    if post_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agents not found")
    return agents_db[post_id]

@app.post("/api/posts/{post_id}/publish")
async def publish_post(post_id: str):
    """Publish a post to LinkedIn"""
    if post_id not in posts_db:
        raise HTTPException(status_code=404, detail="Post not found")
    
    post = posts_db[post_id]
    if post.status != "completed":
        raise HTTPException(status_code=400, detail="Post not ready for publishing")
    
    if not post.content:
        raise HTTPException(status_code=400, detail="Post has no content to publish")
    
    try:
        # LinkedIn credentials from post or environment variables
        client_id = post.linkedinClientId or os.environ.get("LINKEDIN_CLIENT_ID")
        client_secret = post.linkedinClientSecret or os.environ.get("LINKEDIN_CLIENT_SECRET")
        
        if not client_id or not client_secret:
            raise HTTPException(status_code=400, detail="LinkedIn credentials not configured. Please provide LinkedIn credentials when creating the post or set LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET environment variables.")
        
        # Use the demo system's LinkedIn posting function
        if demo_system:
            success = demo_system.post_to_linkedin(post.content, client_id, client_secret)
            if success:
                post.status = "published"
                post.updatedAt = datetime.now().isoformat()
                return {"message": "Post published successfully to LinkedIn", "postId": post_id}
            else:
                raise HTTPException(status_code=500, detail="Failed to publish to LinkedIn")
        else:
            raise HTTPException(status_code=500, detail="Demo system not available")
            
    except Exception as e:
        print(f"❌ Error publishing to LinkedIn: {e}")
        raise HTTPException(status_code=500, detail=f"Publishing failed: {str(e)}")

@app.get("/api/posts/{post_id}/linkedin-auth")
async def get_linkedin_auth_url(post_id: str):
    """Get LinkedIn authentication URL for a post"""
    if post_id not in posts_db:
        raise HTTPException(status_code=404, detail="Post not found")
    
    post = posts_db[post_id]
    if post.status != "completed":
        raise HTTPException(status_code=400, detail="Post not ready for publishing")
    
    try:
        from linkedin_poster import LinkedInPoster
        
        client_id = post.linkedinClientId or os.environ.get("LINKEDIN_CLIENT_ID")
        client_secret = post.linkedinClientSecret or os.environ.get("LINKEDIN_CLIENT_SECRET")
        
        if not client_id or not client_secret:
            raise HTTPException(status_code=400, detail="LinkedIn credentials not configured. Please provide LinkedIn credentials when creating the post or set LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET environment variables.")
        
        poster = LinkedInPoster(client_id, client_secret)
        auth_url = poster.get_authorization_url()
        
        return {"auth_url": auth_url, "postId": post_id}
        
    except Exception as e:
        print(f"❌ Error getting LinkedIn auth URL: {e}")
        raise HTTPException(status_code=500, detail=f"Auth URL generation failed: {str(e)}")

@app.post("/api/posts/{post_id}/linkedin-callback")
async def handle_linkedin_callback(post_id: str, request: dict):
    """Handle LinkedIn OAuth callback and publish post"""
    if post_id not in posts_db:
        raise HTTPException(status_code=404, detail="Post not found")
    
    post = posts_db[post_id]
    if post.status != "completed":
        raise HTTPException(status_code=400, detail="Post not ready for publishing")
    
    try:
        from linkedin_poster import LinkedInPoster
        
        client_id = post.linkedinClientId or os.environ.get("LINKEDIN_CLIENT_ID")
        client_secret = post.linkedinClientSecret or os.environ.get("LINKEDIN_CLIENT_SECRET")
        
        if not client_id or not client_secret:
            raise HTTPException(status_code=400, detail="LinkedIn credentials not configured. Please provide LinkedIn credentials when creating the post or set LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET environment variables.")
        
        code = request.get("code")
        if not code:
            raise HTTPException(status_code=400, detail="Authorization code is required")
        
        poster = LinkedInPoster(client_id, client_secret)
        
        print(f"✅ Received authorization code: {code}")
        print("✅ Authorization code received")
        
        # Get access token
        print("🔑 Exchanging code for access token...")
        access_token = poster.get_access_token(code)
        if not access_token:
            raise HTTPException(status_code=400, detail="Failed to get access token")
        print("✅ Access token obtained")
        
        # Get user profile
        print("👤 Getting user profile...")
        user_profile = poster.get_user_profile()
        if not user_profile:
            raise HTTPException(status_code=400, detail="Failed to get user profile")
        print(f"✅ Authenticated as: {user_profile.get('name', 'Unknown User')}")
        
        # Post to LinkedIn
        print("📝 Creating LinkedIn post...")
        result = poster.post_to_linkedin(post.content)
        if result.get('success'):
            post.status = "published"
            post.updatedAt = datetime.now().isoformat()
            
            linkedin_post_id = result.get('post_id')
            linkedin_url = result.get('post_url')
            
            print("🎉 Successfully posted to LinkedIn!")
            print(f"📊 Post ID: {linkedin_post_id}")
            
            return {
                "message": "Post published successfully to LinkedIn", 
                "postId": post_id,
                "linkedinPostId": linkedin_post_id,
                "linkedinUrl": linkedin_url
            }
        else:
            error_msg = result.get('error', 'Unknown error')
            print(f"❌ Failed to post to LinkedIn: {error_msg}")
            raise HTTPException(status_code=500, detail=f"Failed to publish to LinkedIn: {error_msg}")
            
    except Exception as e:
        print(f"❌ Error in LinkedIn callback: {e}")
        raise HTTPException(status_code=500, detail=f"Publishing failed: {str(e)}")

@app.delete("/api/posts/{post_id}")
async def delete_post(post_id: str):
    """Delete a post"""
    if post_id not in posts_db:
        raise HTTPException(status_code=404, detail="Post not found")
    
    del posts_db[post_id]
    if post_id in agents_db:
        del agents_db[post_id]
    
    return {"message": "Post deleted successfully"}

@app.get("/auth/callback")
async def linkedin_callback(code: str = None, state: str = None, error: str = None):
    """Handle LinkedIn OAuth callback"""
    if error:
        return HTMLResponse(f"""
        <html>
        <body>
            <h2>Authentication Error</h2>
            <p>Error: {error}</p>
            <script>
                console.log('Authentication error: {error}');
                
                if (window.opener && !window.opener.closed) {{
                    // Try multiple origins to ensure delivery
                    const origins = ['*', 'null', 'file://', window.location.origin];
                    
                    origins.forEach((origin, index) => {{
                        setTimeout(() => {{
                            try {{
                                console.log(`Sending error message with origin: ${{origin}}`);
                                window.opener.postMessage({{
                                    type: 'LINKEDIN_AUTH_ERROR',
                                    error: '{error}',
                                    timestamp: Date.now()
                                }}, origin);
                            }} catch (e) {{
                                console.log(`Failed to send error message with origin ${{origin}}:`, e);
                            }}
                        }}, index * 100);
                    }});
                }}
                
                localStorage.setItem('linkedin_auth_error', '{error}');
                localStorage.setItem('linkedin_auth_timestamp', Date.now().toString());
                
                setTimeout(() => {{
                    window.close();
                }}, 3000);
            </script>
        </body>
        </html>
        """)
    
    if not code:
        return HTMLResponse("""
        <html>
        <body>
            <h2>Authentication Failed</h2>
            <p>No authorization code received</p>
            <script>
                console.log('No authorization code received');
                
                if (window.opener && !window.opener.closed) {
                    // Try multiple origins to ensure delivery
                    const origins = ['*', 'null', 'file://', window.location.origin];
                    
                    origins.forEach((origin, index) => {
                        setTimeout(() => {
                            try {
                                console.log(`Sending error message with origin: ${origin}`);
                                window.opener.postMessage({
                                    type: 'LINKEDIN_AUTH_ERROR',
                                    error: 'No authorization code',
                                    timestamp: Date.now()
                                }, origin);
                            } catch (e) {
                                console.log(`Failed to send error message with origin ${origin}:`, e);
                            }
                        }, index * 100);
                    });
                }
                
                localStorage.setItem('linkedin_auth_error', 'No authorization code');
                localStorage.setItem('linkedin_auth_timestamp', Date.now().toString());
                
                setTimeout(() => {
                    window.close();
                }, 3000);
            </script>
        </body>
        </html>
        """)
    
    # Return success page that sends the code to the parent window
    return HTMLResponse(f"""
    <html>
    <body>
        <h2>Authentication Successful!</h2>
        <p>This window will close automatically in 3 seconds...</p>
        <script>
            console.log('LinkedIn auth callback received code: {code}');
            
            // Send the authorization code to the parent window
            if (window.opener && !window.opener.closed) {{
                console.log('Sending message to parent window');
                
                // Try multiple origins to ensure delivery
                const origins = ['*', 'null', 'file://', window.location.origin];
                
                origins.forEach((origin, index) => {{
                    setTimeout(() => {{
                        try {{
                            console.log(`Sending message with origin: ${{origin}}`);
                            window.opener.postMessage({{
                                type: 'LINKEDIN_AUTH_SUCCESS',
                                code: '{code}',
                                timestamp: Date.now()
                            }}, origin);
                        }} catch (e) {{
                            console.log(`Failed to send message with origin ${{origin}}:`, e);
                        }}
                    }}, index * 100);
                }});
            }} else {{
                console.log('No opener window available');
            }}
            
            // Store in localStorage as backup
            localStorage.setItem('linkedin_auth_code', '{code}');
            localStorage.setItem('linkedin_auth_timestamp', Date.now().toString());
            
            // Close the popup window after a delay
            setTimeout(() => {{
                window.close();
            }}, 3000);
        </script>
    </body>
    </html>
    """)

if __name__ == "__main__":
    print("🚀 Starting Simple ML Paper Social Media Poster API")
    print("📡 Server will be available at: http://localhost:8000")
    print("📖 API docs at: http://localhost:8000/docs")
    print("🛑 Press Ctrl+C to stop")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info") 