# RxMen Discovery Call Copilot - Backend API

AI-powered root cause analysis system for Erectile Dysfunction (ED) and Premature Ejaculation (PE) discovery calls.

## 🏗️ Architecture

- **Framework**: FastAPI (Python 3.10+)
- **AI Model**: Claude 3.5 Sonnet (Anthropic)
- **Vector Database**: Pinecone
- **Embeddings**: OpenAI text-embedding-3-small
- **Medical Knowledge**: 6 extracted training documents (113K characters)

## 📁 Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration & environment settings
│   │
│   ├── api/
│   │   ├── routes/
│   │   │   ├── health.py       # Health check endpoint
│   │   │   └── analyze.py      # Main analysis endpoint
│   │
│   ├── models/
│   │   ├── requests.py         # Pydantic request schemas
│   │   └── responses.py        # Pydantic response schemas
│   │
│   ├── services/
│   │   ├── rag_service.py      # RAG retrieval logic
│   │   └── claude_service.py   # Claude API integration
│   │
│   └── utils/
│       └── logger.py           # Logging configuration
│
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── .gitignore                 # Python-specific gitignore
└── README.md                  # This file
```

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.10 or higher
- pip or poetry for package management
- API keys for:
  - [Anthropic Claude](https://console.anthropic.com/)
  - [OpenAI](https://platform.openai.com/api-keys)
  - [Pinecone](https://app.pinecone.io/)

### 2. Installation

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (recommended)
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API keys
nano .env  # or use your preferred editor
```

**Required environment variables:**

```env
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxx
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxx
PINECONE_API_KEY=xxxxxxxxxxxxxxxxxxxxx
PINECONE_ENVIRONMENT=us-east-1-aws
PINECONE_INDEX_NAME=rxmen-medical-knowledge
```

### 4. Run the Server

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using Python directly
python -m app.main
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📡 API Endpoints

### Health Check

```http
GET /api/v1/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-10T17:00:00Z",
  "version": "1.0.0",
  "services": {
    "claude_api": true,
    "openai_api": true,
    "pinecone": true
  }
}
```

### Analysis Endpoint

```http
POST /api/v1/analyze
Content-Type: application/json
```

**Request Body:**
```json
{
  "age": 32,
  "height_cm": 175,
  "weight": 75,
  "main_issue": "ed",
  "emergency_red_flags": "none",
  "medical_conditions": ["none"],
  "current_medications": ["none"],
  "relationship_status": "married",
  "masturbation_method": "hands",
  "ed_gets_erections": "yes",
  "first_consultation": "yes",
  ...
}
```

**Response:**
```json
{
  "success": true,
  "primary_diagnosis": "Performance Anxiety with Situational ED",
  "root_causes": [
    {
      "category": "Performance Anxiety",
      "confidence": "high",
      "explanation": "Fear of not performing creates self-fulfilling cycle",
      "contributing_factors": ["Avoids sex due to worry", "Works during masturbation"],
      "analogy": "Like stage fright - worrying makes it worse"
    }
  ],
  "summary": "Patient shows classic signs of performance anxiety...",
  "recommended_actions": [...],
  "red_flags": [],
  "requires_specialist": false,
  "model_used": "claude-3-5-sonnet-20241022",
  "sources_used": ["ED_training_Module", "Analogies_with_Root_Causes"]
}
```

## 🧪 Testing

### Manual Testing with curl

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Test analysis endpoint
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "age": 30,
    "weight": 75,
    "main_issue": "ed",
    "emergency_red_flags": "none",
    "first_consultation": "yes",
    ...
  }'
```

### Using FastAPI Interactive Docs

1. Open http://localhost:8000/docs
2. Click on an endpoint
3. Click "Try it out"
4. Fill in the request body
5. Click "Execute"

## 🔧 Configuration Options

Edit `app/config.py` or set environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | Claude API key | None |
| `OPENAI_API_KEY` | OpenAI API key | None |
| `PINECONE_API_KEY` | Pinecone API key | None |
| `CLAUDE_MODEL` | Claude model version | `claude-3-5-sonnet-20241022` |
| `CLAUDE_MAX_TOKENS` | Max response tokens | `4096` |
| `CLAUDE_TEMPERATURE` | Model temperature | `0.7` |
| `RAG_TOP_K` | Number of chunks to retrieve | `5` |
| `RAG_CHUNK_SIZE` | Tokens per chunk | `800` |
| `CORS_ORIGINS` | Allowed frontend origins | `localhost` |

## 📊 Medical Knowledge

The system uses 6 medical training documents:

1. **ED_training_Module.txt** (46KB) - Comprehensive ED training
2. **PE_Training_module.txt** (20KB) - PE diagnosis and treatment
3. **ED_PE_DSM.txt** (24KB) - Diagnostic criteria
4. **Common_Wrong_Explanations_RxMen_DC_Copilot.txt** (12KB) - What NOT to say
5. **Analogies_with_Root_Causes.txt** (6KB) - Patient explanations
6. **Red_Flags_Checklist_RxMen_Discovery_Call_Copilot.txt** (5KB) - Safety protocols

**Total:** 113,266 characters across 55 pages

## 🔄 Development Workflow

### Current Status (Step 2 - Complete)
✅ Backend structure created
✅ FastAPI endpoints defined
✅ Pydantic models for validation
✅ Service layer with placeholders
✅ Configuration management

### Next Steps

**Step 3:** Configure environment variables
**Step 4:** Implement chunking strategy
**Step 5:** Generate embeddings and upload to Pinecone
**Step 6:** Implement RAG retrieval
**Step 7:** Integrate Claude API
**Step 8:** Connect to frontend

## 🐛 Troubleshooting

### ImportError: No module named 'app'

Make sure you're in the `backend` directory and run:
```bash
python -m app.main
# or
uvicorn app.main:app --reload
```

### API Key Errors

Check your `.env` file:
```bash
cat .env | grep API_KEY
```

Make sure keys are properly set without quotes or extra spaces.

### CORS Errors from Frontend

Add your frontend URL to `CORS_ORIGINS` in `.env`:
```env
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

### Port Already in Use

Change the port in `.env`:
```env
PORT=8001
```

Or specify when running:
```bash
uvicorn app.main:app --reload --port 8001
```

## 📝 Code Style

- **PEP 8** compliance
- **Type hints** throughout
- **Docstrings** for all functions
- **Logging** for debugging

## 🔐 Security Notes

- ⚠️ **NEVER commit .env files**
- ⚠️ **Keep API keys secret**
- ⚠️ MVP has no authentication (add before production)
- ⚠️ Use HTTPS in production
- ⚠️ Validate all input data (Pydantic handles this)

## 📞 Support

For issues or questions:
- Check the [FastAPI documentation](https://fastapi.tiangolo.com/)
- Review API logs in console
- Test endpoints in `/docs` interface

## 📄 License

Internal project - RxMen healthcare system.

---

**Ready to add RAG and Claude integration! 🚀**
