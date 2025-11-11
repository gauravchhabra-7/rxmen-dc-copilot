# Step 5B: RAG System Setup - Execution Guide

## Overview

This guide will walk you through completing Step 5B on your local Mac:
1. Generate embeddings for 31 medical chunks
2. Upload embeddings to Pinecone
3. Test search quality with 3 queries
4. Verify system prompt components

---

## Prerequisites

✅ Python 3.12 virtual environment active
✅ All requirements installed (`pip install -r requirements.txt`)
✅ `.env` file configured with valid API keys:
   - `OPENAI_API_KEY` (for embeddings)
   - `PINECONE_API_KEY` (for vector database)
   - `ANTHROPIC_API_KEY` (for later testing)

---

## Part 1: Generate Embeddings

### Step 1.1: Navigate to Backend Directory

```bash
cd ~/RxMen/DC_Copilot/rxmen-dc-copilot/backend
source venv/bin/activate
```

### Step 1.2: Run Embedding Generation Script

```bash
python generate_embeddings.py
```

**Expected Output:**
```
================================================================================
STEP 5B - PART 1: Generate Embeddings
================================================================================

✓ Loaded 31 chunks
✓ OpenAI client initialized

[1/31] Processing ED_training_Module_chunk_001 (433 tokens)
✓   Generated embedding: 1536 dimensions

[2/31] Processing ED_training_Module_chunk_002 (666 tokens)
✓   Generated embedding: 1536 dimensions

...

[31/31] Processing PE_Training_module_chunk_013 (587 tokens)
✓   Generated embedding: 1536 dimensions

================================================================================
Embedding Generation Complete
================================================================================
✓ Processed: 31 chunks
✓ Total tokens: 22,659
✓ Model: text-embedding-3-small
✓ Embedding dimensions: 1536
✓ Estimated cost: $0.0005

✓ Embeddings saved to: ../data/processed/medical_chunks_embedded.json
```

**What This Does:**
- Reads `data/processed/medical_chunks.json` (31 chunks)
- Generates 1536-dimension embeddings using OpenAI API
- Saves to `data/processed/medical_chunks_embedded.json`
- Cost: ~$0.0005 (less than 1 cent)

---

## Part 2: Upload to Pinecone

### Step 2.1: Create Pinecone Index (One-Time Setup)

**IMPORTANT:** Before running the upload script, you need to create the Pinecone index.

#### Option A: Via Pinecone Dashboard (Recommended)

1. Go to https://app.pinecone.io/
2. Log in with your account
3. Click "Create Index"
4. Configure:
   - **Name:** `rxmen-medical-knowledge`
   - **Dimensions:** `1536`
   - **Metric:** `cosine`
   - **Cloud:** `AWS`
   - **Region:** `us-east-1` (or your preferred region)
5. Click "Create Index"

#### Option B: Via Pinecone CLI (Advanced)

```bash
# Install Pinecone CLI if needed
pip install pinecone-cli

# Create index
pinecone create-index \
  --name rxmen-medical-knowledge \
  --dimension 1536 \
  --metric cosine \
  --cloud aws \
  --region us-east-1
```

### Step 2.2: Update .env with Pinecone Details

Ensure your `.env` file has:

```bash
PINECONE_API_KEY=your_actual_pinecone_key
PINECONE_ENVIRONMENT=us-east-1-aws  # Or your chosen region
PINECONE_INDEX_NAME=rxmen-medical-knowledge
```

### Step 2.3: Run Upload Script

```bash
python upload_to_pinecone.py
```

**Expected Output:**
```
================================================================================
STEP 5B - PART 2: Upload to Pinecone
================================================================================

✓ Loaded 31 embedded chunks
✓ All chunks have embeddings
✓ Pinecone client initialized
ℹ Available indexes: ['rxmen-medical-knowledge']
✓ Index 'rxmen-medical-knowledge' found
✓ Connected to index

================================================================================
Uploading to Namespace: medical_knowledge_v1
================================================================================

[1/1] Uploading batch (31 vectors)
✓   Uploaded 31 vectors

================================================================================
Verifying Upload
================================================================================

✓ Namespace 'medical_knowledge_v1' created
✓ Vectors in namespace: 31
✓ All vectors uploaded successfully!

================================================================================
Upload Summary
================================================================================
✓ Upload completed successfully
  Index: rxmen-medical-knowledge
  Namespace: medical_knowledge_v1
  Vectors uploaded: 31
  Total vectors in namespace: 31
  Embedding dimensions: 1536
  Metric: cosine
```

**What This Does:**
- Connects to your Pinecone index
- Uploads all 31 embedded chunks
- Creates namespace: `medical_knowledge_v1`
- Stores metadata (text, source_file, root_cause, document_type)

---

## Part 3: Test Search Quality

### Step 3.1: Run Search Quality Tests

```bash
python test_search_quality.py
```

**Expected Output:**
```
================================================================================
STEP 5B - PART 3: Test Search Quality
================================================================================

✓ OpenAI client initialized
✓ Connected to index 'rxmen-medical-knowledge'
✓ Namespace 'medical_knowledge_v1' has 31 vectors
ℹ Using RAG_TOP_K=8 (per handoff doc specification)

================================================================================
Running Search Quality Tests
================================================================================

────────────────────────────────────────────────────────────────────────────────
TEST 1: Patient works during masturbation but fails with partner, has anxiety about performance
────────────────────────────────────────────────────────────────────────────────

✓ Query embedding generated (1536 dimensions)
✓ Retrieved 8 results

Search Results:

[1] Score: 0.8542
    Chunk: ED_training_Module_chunk_002
    Root Cause: Performance Anxiety
    Preview: Other neurological diseases like Parkinson's disease and damage to spinal cord can affect...

[2] Score: 0.8231
    Chunk: ED_training_Module_chunk_003
    Root Cause: Performance Anxiety
    Preview: Psychogenic Erection – This happens when you think of sexual memories or fantasies...

...

✓ Found expected keywords/causes: Performance Anxiety, anxiety, psychological
✓ Top result has high relevance (score: 0.8542)

────────────────────────────────────────────────────────────────────────────────
TEST 2: Diabetic patient, no morning erections, gradual onset over months
────────────────────────────────────────────────────────────────────────────────

[Similar detailed output for diabetes test]

────────────────────────────────────────────────────────────────────────────────
TEST 3: Finishes very quickly, has tight grip during masturbation, porn 5-7 times per week
────────────────────────────────────────────────────────────────────────────────

[Similar detailed output for PE test]

================================================================================
Search Quality Tests Complete
================================================================================
✓ All 3 search quality tests completed
  Index: rxmen-medical-knowledge
  Namespace: medical_knowledge_v1
  Vector count: 31
  Top-K: 8
  Model: text-embedding-3-small

Review the results above to verify search relevance
High scores (>0.7) indicate good semantic matching
```

**What This Tests:**
1. **Test 1 (Performance Anxiety):** Query about partner anxiety → Should retrieve psychological chunks
2. **Test 2 (Diabetes ED):** Query about diabetic patient → Should retrieve cardiovascular/diabetes chunks
3. **Test 3 (PE):** Query about premature ejaculation → Should retrieve PE-related chunks

**Success Criteria:**
- Similarity scores > 0.7 for top results
- Expected keywords/root causes found in top 8 results
- Relevant medical context retrieved

---

## Part 4: Verify System Prompt Components

### Step 4.1: Check Created Files

```bash
# List system prompt components
ls -la ../data/processed/system_prompt_components/

# Should show:
# - red_flags.md (20 red flags with escalation actions)
# - analogies.md (ED/PE teaching examples in Hinglish)
# - wrong_explanations.md (50 forbidden phrases)
# - treatment_explanations.md (treatment framework)
```

### Step 4.2: View System Prompt Template

```bash
# View comprehensive system prompt
cat ../data/processed/system_prompt_template.md | head -100

# Check file size
wc -w ../data/processed/system_prompt_template.md
# Should show ~7,500 words (~10,000 tokens)
```

**Files Created:**
```
data/processed/
├── medical_chunks.json                 (31 chunks - original)
├── medical_chunks_embedded.json        (31 chunks with embeddings - NEW)
├── system_prompt_components/           (NEW)
│   ├── red_flags.md                   (Safety checklist)
│   ├── analogies.md                   (Patient explanation patterns)
│   ├── wrong_explanations.md          (Forbidden phrases)
│   └── treatment_explanations.md      (Treatment framework)
└── system_prompt_template.md          (Comprehensive system prompt - NEW)
```

---

## Part 5: Verify RAG System Status

### Step 5.1: Quick Status Check

Run the API connectivity test to ensure everything is working:

```bash
python test_api_connectivity.py
```

**Expected Output:**
```
================================================================================
API Connectivity Test Suite
================================================================================

TEST 1: Anthropic Claude API
✓ Anthropic Claude API is working!

TEST 2: OpenAI API (Embeddings)
✓ OpenAI API is working!

TEST 3: Pinecone Vector Database
✓ Pinecone API connection successful!
ℹ Index 'rxmen-medical-knowledge' found
ℹ Namespace 'medical_knowledge_v1' has 31 vectors

================================================================================
TEST SUMMARY
================================================================================
Total Tests: 3
Passed: 3
Failed: 0

ANTHROPIC    ✓ PASS
OPENAI       ✓ PASS
PINECONE     ✓ PASS

✓ All API services are configured and working correctly!
```

---

## Troubleshooting

### Issue 1: "Access denied" from OpenAI

**Solution:** Check your OpenAI API key in `.env`:
```bash
# Verify key format
echo $OPENAI_API_KEY | head -c 20
# Should start with: sk-proj-...
```

### Issue 2: Pinecone Index Not Found

**Solution:** Create the index first (see Step 2.1)

### Issue 3: "No module named 'pinecone'"

**Solution:** Uninstall old package and install new one:
```bash
pip uninstall pinecone-client -y
pip install pinecone
```

### Issue 4: Low Similarity Scores (<0.5)

**Possible Causes:**
- Embeddings generated with wrong model
- Query doesn't match medical context
- Index not properly configured

**Solution:** Re-run embedding generation and verify model is `text-embedding-3-small`

---

## Success Checklist

After completing all parts, verify:

- ✅ `medical_chunks_embedded.json` exists (file size ~800KB)
- ✅ Pinecone index `rxmen-medical-knowledge` has 31 vectors
- ✅ Namespace `medical_knowledge_v1` exists
- ✅ Search quality tests pass with scores > 0.7
- ✅ 4 system prompt markdown files created
- ✅ System prompt template created (~7.5k tokens)
- ✅ All 3 API connectivity tests pass

---

## Next Steps

Once Step 5B is complete:

**STEP 6: Build the /analyze Endpoint**
- Integrate RAG retrieval service
- Connect Claude API service
- Implement system prompt injection
- Test end-to-end diagnosis flow

**Files You'll Need:**
- `backend/app/services/rag_service.py` (RAG retrieval)
- `backend/app/services/claude_service.py` (Claude API + system prompt)
- `backend/app/api/routes/analyze.py` (endpoint logic)

---

## Cost Summary

**Total Cost for Step 5B:**
- Embedding generation: ~$0.0005 (31 chunks × 730 avg tokens)
- Pinecone storage: Free tier (up to 100k vectors)
- Search quality tests: ~$0.0001 (3 queries)

**Total: < $0.001 (less than 1 cent)**

---

## Support

If you encounter issues:

1. Check `.env` file has correct API keys
2. Verify Python 3.12 virtual environment is active
3. Review error messages in terminal output
4. Check Pinecone dashboard for index status
5. Ensure all `requirements.txt` dependencies installed

---

**Document Version:** 1.0
**Created:** November 2025
**For:** Local Mac Testing - Step 5B RAG System Setup
