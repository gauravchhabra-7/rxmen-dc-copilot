# 🔧 API TEST - LOCAL EXECUTION INSTRUCTIONS

## ✅ UPDATES COMPLETED

I've updated the test script with:
- ✅ Claude model: `claude-sonnet-4-20250514` (as primary)
- ✅ Detailed logging for every step
- ✅ API key format validation
- ✅ Library import confirmation
- ✅ Better error messages

---

## 📋 STEPS TO PULL AND TEST ON YOUR MAC

### **Step 1: Open Terminal on Mac**

### **Step 2: Navigate to Your Project**
```bash
cd ~/path/to/rxmen-dc-copilot
```
(Replace with your actual path)

### **Step 3: Pull Latest Changes**
```bash
git fetch origin
git pull origin claude/rxmen-discovery-copilot-011CUtZkzHwKSm8yzbiJv8YB
```

### **Step 4: Verify You Have the Latest Code**
```bash
git log -1 --oneline
```
You should see: `Update API test with claude-sonnet-4 and detailed logging`

### **Step 5: Check Your .env File**
```bash
cd backend
cat .env | grep "API_KEY"
```

**Verify these keys are present:**
- ANTHROPIC_API_KEY=sk-ant-api03-ONH87MEe...
- OPENAI_API_KEY=sk-proj-h2k03ZOl...
- PINECONE_API_KEY=pcsk_3fNzrD...

**If .env doesn't exist or keys are missing:**
```bash
# Copy the example
cp .env.example .env

# Edit and add your keys
nano .env
# (or use: code .env / vim .env / open .env)
```

### **Step 6: Install Required Dependencies**

If you haven't already:
```bash
pip install python-dotenv anthropic openai pinecone-client
```

Or install all dependencies:
```bash
pip install -r requirements.txt
```

### **Step 7: Run the Test Script**
```bash
python test_api_connectivity.py
```

---

## 📊 WHAT THE TEST WILL SHOW

You'll see detailed output like:

```
================================================================================
API Connectivity Test Suite - 2025-11-11 XX:XX:XX
================================================================================

ℹ Checking environment configuration...
ℹ ANTHROPIC_API_KEY loaded: Yes
ℹ OPENAI_API_KEY loaded: Yes
ℹ PINECONE_API_KEY loaded: Yes

================================================================================
TEST 1: Anthropic Claude API
================================================================================

ℹ API Key: sk-ant-a...TwAA
ℹ API Key length: 108 characters
ℹ API Key format: sk-ant-api03-ON...V0NR1Q--47
ℹ Anthropic library imported successfully
ℹ Anthropic client initialized
ℹ Sending test message to Claude...
ℹ Trying model: claude-sonnet-4-20250514
```

Then it will either:
- ✅ Show success message
- ❌ Show detailed error with exact issue

---

## 🎯 WHAT TO DO WITH THE OUTPUT

### **After Running the Test:**

1. **Copy the ENTIRE output** from terminal
2. **Paste it in your response** to me
3. **Include everything** - especially:
   - Environment variable check results
   - Each API test detailed logs
   - Any error messages

### **I need to see:**
- Did environment variables load? (Yes/No)
- What's the API key format/length?
- Which step failed?
- What's the exact error message?

---

## 🔍 COMMON ISSUES & QUICK FIXES

### **Issue 1: "No module named 'dotenv'"**
```bash
pip install python-dotenv
```

### **Issue 2: "No module named 'anthropic'"**
```bash
pip install anthropic openai pinecone-client
```

### **Issue 3: ".env file not found"**
```bash
# Make sure you're in backend directory
cd backend

# Check if .env exists
ls -la .env

# If not, create it from example
cp .env.example .env
nano .env  # Add your API keys
```

### **Issue 4: "ANTHROPIC_API_KEY loaded: No"**
The .env file isn't being loaded. Try:
```bash
# Check file location
pwd  # Should show: .../rxmen-dc-copilot/backend

# Verify .env content
cat .env | head -30
```

---

## ⚡ QUICK TEST CHECKLIST

Before running, verify:
- [ ] You're in the `backend` directory
- [ ] `.env` file exists in backend directory
- [ ] API keys are in .env (not .env.example)
- [ ] Dependencies are installed
- [ ] Python 3.7+ is being used (`python --version`)

---

## 📤 READY TO TEST!

Run these commands and share the complete output:

```bash
cd ~/path/to/rxmen-dc-copilot/backend
python test_api_connectivity.py > test_output.txt 2>&1
cat test_output.txt
```

Then paste the entire output here!

---

**Let's identify and fix the exact issue! 🚀**
