# ML Paper Social Media Poster

A multi-agent system that generates LinkedIn posts from ML research papers using LangGraph and OpenAI.

## 🚀 Quick Start

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd social_media_poster/backend
   ```

2. **Install dependencies:**
   ```bash
   uv sync
   ```

3. **Configure environment variables:**
   ```bash
   # Copy the example environment file
   cp ../.env.example ../.env
   
   # Edit the .env file with your actual API keys
   # Required for LinkedIn posting:
   LINKEDIN_CLIENT_ID=your-linkedin-client-id
   LINKEDIN_CLIENT_SECRET=your-linkedin-client-secret
   
   # Optional (users can provide these in the UI):
   OPENAI_API_KEY=sk-your-openai-api-key
   TAVILY_API_KEY=tvly-your-tavily-api-key
   ```

4. **Start the API server:**
   ```bash
   uv run python simple_api.py
   ```

   The server will start on `http://localhost:8000` with:
   - API endpoints at `/api/*`
   - Interactive docs at `/docs`
   - Health check at `/api/health`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd social_media_poster/frontend
   ```

2. **Open the backend demo:**
   ```bash
   open backend_demo.html
   ```

   Or serve it with a simple HTTP server:
   ```bash
   python -m http.server 3000
   ```

## 🔐 LinkedIn OAuth App Setup

To enable LinkedIn posting, you need to create a LinkedIn OAuth app:

1. **Go to LinkedIn Developer Portal:**
   - Visit https://www.linkedin.com/developers/apps
   - Click "Create App"

2. **Configure your app:**
   - App name: Your app name
   - LinkedIn Page: Select your company page (or create one)
   - App logo: Upload a logo
   - Legal agreement: Accept terms

3. **Add OAuth 2.0 scopes:**
   - Go to the "Auth" tab
   - Add these scopes:
     - `r_liteprofile` (Read access to basic profile)
     - `w_member_social` (Write access to post on behalf of user)

4. **Configure redirect URLs:**
   - Add `http://localhost:5000/callback` for local development
   - Add your production callback URL for deployment

5. **Get your credentials:**
   - Copy the "Client ID" and "Client Secret"
   - Add them to your `.env` file as `LINKEDIN_CLIENT_ID` and `LINKEDIN_CLIENT_SECRET`

## 🔧 System Architecture

### Backend Components

- **`simple_api.py`** - FastAPI server with REST endpoints
- **`simple_demo.py`** - Core multi-agent system using LangGraph
- **Multi-agent workflow:**
  - Research Agent: Analyzes ML papers
  - Content Agent: Creates LinkedIn-optimized posts

### Frontend Components

- **`backend_demo.html`** - Interactive web interface
- **Real-time features:**
  - Agent status monitoring
  - Progress tracking
  - Live content generation

## 📡 API Endpoints

### Posts
- `POST /api/posts` - Create a new post
- `GET /api/posts` - Get all posts
- `GET /api/posts/{id}` - Get specific post
- `DELETE /api/posts/{id}` - Delete post

### Agents
- `GET /api/posts/{id}/agents` - Get agent status for a post

### Publishing
- `POST /api/posts/{id}/publish` - Mark post as published

### Health
- `GET /api/health` - System health check

## 🧪 Testing the System

1. **Start the backend server** (see Backend Setup above)

2. **Open the frontend** in your browser

3. **Test with a sample paper:**
   - Paper Title: "Attention Is All You Need"
   - Paper URL: "https://arxiv.org/abs/1706.03762"
   - Click "Create Post"

4. **Watch the agents work:**
   - Research Agent analyzes the paper
   - Content Agent creates LinkedIn post
   - Final content appears when complete

## 🔑 Environment Variables

The system uses the following environment variables:

- `OPENAI_API_KEY` - Required for LLM operations
- `TAVILY_API_KEY` - Optional for web search (not used in simple demo)

## 🎯 Features

### Multi-Agent Processing
- **Research Phase**: Analyzes paper content and significance
- **Content Creation**: Generates LinkedIn-optimized posts
- **Verification**: Ensures proper formatting and compliance

### Real-time Updates
- Live agent status monitoring
- Progress bars for each agent
- Automatic content display when complete

### Professional Output
- LinkedIn-formatted posts
- Proper Unicode formatting (no markdown)
- Engaging, professional tone
- Optimal length for LinkedIn

## 🛠️ Development

### Adding New Agents
1. Create agent function in `simple_demo.py`
2. Add to agent workflow in `generate_post()`
3. Update API models in `simple_api.py`

### Customizing Frontend
- Modify `backend_demo.html` for UI changes
- Update CSS for styling
- Add new features with JavaScript

### API Extensions
- Add new endpoints in `simple_api.py`
- Extend Pydantic models as needed
- Update frontend to use new endpoints

## 📝 Example Output

The system generates professional LinkedIn posts like:

```
🚀 In the ever-evolving landscape of Natural Language Processing (NLP), 
one paper has truly transformed the field: "Attention Is All You Need" 
by Vaswani et al.

This groundbreaking work, published in 2017, introduced the 𝑇𝑟𝑎𝑛𝑠𝑓𝑜𝑟𝑚𝑒𝑟 
architecture, marking a pivotal shift in how we approach sequence-to-sequence tasks.

𝑲𝒆𝒚 𝑰𝒏𝒏𝒐𝒗𝒂𝒕𝒊𝒐𝒏𝒔 from the paper include:
🔹 𝑆𝑒𝑙𝑓-𝐴𝑡𝑡𝑒𝑛𝑡𝑖𝑜𝑛 𝑀𝑒𝑐𝘩𝑎𝑛𝑖𝑠𝑚
🔸 𝑀𝑢𝑙𝑡𝑖-𝐻𝑒𝑎𝑑 𝑎𝑡𝑡𝑒𝑛𝑡𝑖𝑜𝑛
🔹 𝑃𝑜𝑠𝑖𝑡𝑖𝑜𝑛𝑎𝑙 𝐸𝑛𝑐𝑜𝑑𝑖𝑛𝑔

#NLP #MachineLearning #DeepLearning #Transformers #AI #Innovation
```

## 🔗 LinkedIn Integration

### ✅ **LinkedIn Posting Available**
The system now supports **actual LinkedIn posting** through the LinkedIn API:

1. **Generate Content**: Create LinkedIn-optimized posts from ML papers
2. **Review Content**: Check the generated post in the UI
3. **Publish to LinkedIn**: Click "Publish to LinkedIn" to post directly

### 🔐 **Authentication Process**
When you click "Publish to LinkedIn":
1. System opens LinkedIn OAuth flow
2. You authenticate with your LinkedIn account
3. System gets authorization to post on your behalf
4. Post is published to your LinkedIn profile

### 🎯 **LinkedIn Credentials**
The system uses pre-configured LinkedIn app credentials:
- Client ID: `78p2894wgxe9pc`
- Client Secret: `WPL_AP1.dNv6oeOMPRDtE1Py.X8Vaew==`

### ⚠️ **Important Notes**
- LinkedIn posting requires user authentication each time
- Posts are published to your personal LinkedIn profile
- Content is automatically formatted for LinkedIn (no markdown)
- Character limits are enforced (max 3000 characters)

## 🚀 Next Steps

- ✅ LinkedIn OAuth integration for direct posting (COMPLETED)
- Implement WebSocket for real-time updates
- Add support for multiple social platforms
- Create batch processing capabilities
- Add content scheduling features
- Store LinkedIn auth tokens for persistent sessions 