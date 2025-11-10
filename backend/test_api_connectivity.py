"""
Test script to verify API connectivity for all services.

This script tests:
1. Anthropic Claude API
2. OpenAI API (embeddings)
3. Pinecone vector database

Run: python test_api_connectivity.py
"""

import os
import sys
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'


def print_header(text):
    """Print a formatted header."""
    print(f"\n{BOLD}{BLUE}{'='*80}{RESET}")
    print(f"{BOLD}{BLUE}{text}{RESET}")
    print(f"{BOLD}{BLUE}{'='*80}{RESET}\n")


def print_success(text):
    """Print success message."""
    print(f"{GREEN}✓ {text}{RESET}")


def print_error(text):
    """Print error message."""
    print(f"{RED}✗ {text}{RESET}")


def print_warning(text):
    """Print warning message."""
    print(f"{YELLOW}⚠ {text}{RESET}")


def print_info(text):
    """Print info message."""
    print(f"{BLUE}ℹ {text}{RESET}")


def mask_key(key):
    """Mask API key for display."""
    if not key or len(key) < 8:
        return "NOT_SET"
    return f"{key[:8]}...{key[-4:]}"


def test_anthropic_api():
    """Test Anthropic Claude API connectivity."""
    print_header("TEST 1: Anthropic Claude API")

    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key or api_key.startswith("sk-ant-xxx"):
        print_error("ANTHROPIC_API_KEY not configured or still using placeholder")
        print_info(f"Current value: {mask_key(api_key)}")
        return False

    print_info(f"API Key: {mask_key(api_key)}")

    try:
        from anthropic import Anthropic

        client = Anthropic(api_key=api_key)

        # Test with a simple message
        print_info("Sending test message to Claude...")
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=50,
            messages=[
                {"role": "user", "content": "Respond with only: API test successful"}
            ]
        )

        response_text = message.content[0].text
        print_info(f"Response: {response_text}")

        print_success("Anthropic Claude API is working!")
        return True

    except Exception as e:
        print_error(f"Anthropic API test failed: {str(e)}")
        return False


def test_openai_api():
    """Test OpenAI API connectivity."""
    print_header("TEST 2: OpenAI API (Embeddings)")

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key or api_key.startswith("sk-xxx"):
        print_error("OPENAI_API_KEY not configured or still using placeholder")
        print_info(f"Current value: {mask_key(api_key)}")
        return False

    print_info(f"API Key: {mask_key(api_key)}")

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)

        # Test with a simple embedding
        print_info("Generating test embedding...")
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input="This is a test sentence for embedding generation."
        )

        embedding = response.data[0].embedding
        print_info(f"Embedding dimensions: {len(embedding)}")
        print_info(f"First 5 values: {embedding[:5]}")

        print_success("OpenAI API is working!")
        return True

    except Exception as e:
        print_error(f"OpenAI API test failed: {str(e)}")
        return False


def test_pinecone_api():
    """Test Pinecone vector database connectivity."""
    print_header("TEST 3: Pinecone Vector Database")

    api_key = os.getenv("PINECONE_API_KEY")
    environment = os.getenv("PINECONE_ENVIRONMENT")
    index_name = os.getenv("PINECONE_INDEX_NAME")

    if not api_key or api_key.startswith("xxx"):
        print_error("PINECONE_API_KEY not configured or still using placeholder")
        print_info(f"Current value: {mask_key(api_key)}")
        return False

    print_info(f"API Key: {mask_key(api_key)}")
    print_info(f"Environment: {environment}")
    print_info(f"Index Name: {index_name}")

    try:
        import pinecone

        # Initialize Pinecone
        print_info("Connecting to Pinecone...")
        pinecone.init(api_key=api_key, environment=environment)

        # List indexes
        indexes = pinecone.list_indexes()
        print_info(f"Available indexes: {indexes}")

        # Check if target index exists
        if index_name in indexes:
            print_success(f"Index '{index_name}' exists!")

            # Get index stats
            index = pinecone.Index(index_name)
            stats = index.describe_index_stats()
            print_info(f"Index stats: {stats}")

        else:
            print_warning(f"Index '{index_name}' not found.")
            print_info("You'll need to create this index before running the full system.")
            print_info("This is expected if you haven't set up the RAG system yet.")

        print_success("Pinecone API connection successful!")
        return True

    except Exception as e:
        print_error(f"Pinecone API test failed: {str(e)}")
        return False


def main():
    """Run all API connectivity tests."""
    print_header(f"API Connectivity Test Suite - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    results = {
        "anthropic": test_anthropic_api(),
        "openai": test_openai_api(),
        "pinecone": test_pinecone_api()
    }

    # Summary
    print_header("TEST SUMMARY")

    total = len(results)
    passed = sum(results.values())
    failed = total - passed

    print(f"Total Tests: {total}")
    print(f"{GREEN}Passed: {passed}{RESET}")
    print(f"{RED}Failed: {failed}{RESET}")
    print()

    for service, status in results.items():
        status_text = f"{GREEN}✓ PASS{RESET}" if status else f"{RED}✗ FAIL{RESET}"
        print(f"{service.upper():12} {status_text}")

    print()

    if passed == total:
        print_success("All API services are configured and working correctly!")
        print_info("You're ready to proceed to the next step.")
        return 0
    else:
        print_error(f"{failed} service(s) failed. Please check your API keys and try again.")
        print_info("Make sure to replace placeholder values in .env with your actual API keys.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
