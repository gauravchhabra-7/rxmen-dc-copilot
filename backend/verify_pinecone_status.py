#!/usr/bin/env python3
"""
Verify Pinecone Vector Database Status
Checks index, embeddings, and connectivity before frontend integration
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from pinecone import Pinecone
from openai import OpenAI

# Load environment variables
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

# Colors for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"


def print_header(text):
    print(f"\n{BOLD}{'='*80}{RESET}")
    print(f"{BOLD}{text}{RESET}")
    print(f"{BOLD}{'='*80}{RESET}\n")


def print_success(text):
    print(f"{GREEN}✓{RESET} {text}")


def print_error(text):
    print(f"{RED}✗{RESET} {text}")


def print_warning(text):
    print(f"{YELLOW}⚠{RESET} {text}")


def print_info(text):
    print(f"{BLUE}ℹ{RESET} {text}")


def check_credentials():
    """Check if all required credentials are present"""
    print_header("STEP 1: Checking Credentials")

    required_vars = {
        "PINECONE_API_KEY": os.getenv("PINECONE_API_KEY"),
        "PINECONE_INDEX_NAME": os.getenv("PINECONE_INDEX_NAME"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY")
    }

    all_present = True
    for var_name, var_value in required_vars.items():
        if var_value:
            masked = var_value[:8] + "..." + var_value[-4:] if len(var_value) > 12 else "***"
            print_success(f"{var_name}: {masked}")
        else:
            print_error(f"{var_name}: NOT FOUND")
            all_present = False

    if not all_present:
        print_error("\nMissing required credentials in .env file")
        return False

    return True


def check_pinecone_index():
    """Connect to Pinecone and check index status"""
    print_header("STEP 2: Checking Pinecone Index Status")

    try:
        # Initialize Pinecone
        api_key = os.getenv("PINECONE_API_KEY")
        index_name = os.getenv("PINECONE_INDEX_NAME")

        print_info("Connecting to Pinecone...")
        pc = Pinecone(api_key=api_key)

        # List available indexes
        indexes = pc.list_indexes()
        index_names = [idx.name for idx in indexes]

        print_info(f"Available indexes: {index_names}")

        if index_name not in index_names:
            print_error(f"Index '{index_name}' not found!")
            return None, None

        print_success(f"Index '{index_name}' found")

        # Connect to index
        print_info(f"Connecting to index '{index_name}'...")
        index = pc.Index(index_name)

        # Get index stats
        stats = index.describe_index_stats()

        print_success(f"Connected to index successfully")
        print_info(f"Index dimension: {stats.dimension}")
        print_info(f"Total vector count: {stats.total_vector_count}")

        # Check namespaces
        if stats.namespaces:
            print_info(f"Namespaces found: {list(stats.namespaces.keys())}")
            for ns_name, ns_stats in stats.namespaces.items():
                print_info(f"  - {ns_name}: {ns_stats.vector_count} vectors")
        else:
            print_warning("No namespaces found (index may be empty)")

        return pc, index

    except Exception as e:
        print_error(f"Failed to connect to Pinecone: {str(e)}")
        return None, None


def verify_embeddings(index):
    """Verify embeddings are present"""
    print_header("STEP 3: Verifying Embeddings")

    try:
        stats = index.describe_index_stats()

        target_namespace = "medical_knowledge_v1"
        expected_count = 31

        if target_namespace in stats.namespaces:
            actual_count = stats.namespaces[target_namespace].vector_count

            if actual_count == expected_count:
                print_success(f"Namespace '{target_namespace}' has {actual_count} vectors (EXPECTED: {expected_count})")
            elif actual_count > 0:
                print_warning(f"Namespace '{target_namespace}' has {actual_count} vectors (EXPECTED: {expected_count})")
                print_warning("Vector count mismatch - may need to re-upload")
            else:
                print_error(f"Namespace '{target_namespace}' is empty!")
                return False

            # Check dimension
            if stats.dimension == 1536:
                print_success(f"Embedding dimension: {stats.dimension} (text-embedding-3-small)")
            else:
                print_warning(f"Unexpected dimension: {stats.dimension} (expected: 1536)")

            return True
        else:
            print_error(f"Namespace '{target_namespace}' not found!")
            print_info(f"Available namespaces: {list(stats.namespaces.keys())}")
            return False

    except Exception as e:
        print_error(f"Failed to verify embeddings: {str(e)}")
        return False


def test_sample_query(index):
    """Test a sample query to verify retrieval works"""
    print_header("STEP 4: Testing Sample Query")

    try:
        # Initialize OpenAI client
        openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Test query
        test_query = "performance anxiety with partner"
        print_info(f"Test query: \"{test_query}\"")

        # Generate embedding
        print_info("Generating query embedding...")
        embedding_response = openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=test_query
        )
        query_embedding = embedding_response.data[0].embedding
        print_success(f"Query embedding generated ({len(query_embedding)} dimensions)")

        # Query Pinecone
        print_info("Querying Pinecone (top_k=8, namespace=medical_knowledge_v1)...")
        results = index.query(
            vector=query_embedding,
            top_k=8,
            namespace="medical_knowledge_v1",
            include_metadata=True
        )

        if not results.matches:
            print_error("No results returned from Pinecone!")
            return False

        print_success(f"Retrieved {len(results.matches)} results")

        # Show results
        print(f"\n{BOLD}Top Results:{RESET}\n")
        for i, match in enumerate(results.matches[:5], 1):
            chunk_id = match.id
            score = match.score
            root_cause = match.metadata.get("root_cause", "unknown")
            text_preview = match.metadata.get("text", "")[:80] + "..." if match.metadata.get("text") else "N/A"

            print(f"  [{i}] Score: {score:.4f}")
            print(f"      Chunk: {chunk_id}")
            print(f"      Root Cause: {root_cause}")
            print(f"      Preview: {text_preview}")
            print()

        # Check relevance
        if results.matches[0].score > 0.5:
            print_success(f"Top result has good relevance (score: {results.matches[0].score:.4f})")
        elif results.matches[0].score > 0.3:
            print_warning(f"Top result has moderate relevance (score: {results.matches[0].score:.4f})")
        else:
            print_warning(f"Top result has low relevance (score: {results.matches[0].score:.4f})")

        return True

    except Exception as e:
        print_error(f"Failed to test query: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_backend_access():
    """Test if backend services can access Pinecone"""
    print_header("STEP 5: Testing Backend Service Access")

    try:
        # Try importing backend services
        sys.path.insert(0, str(Path(__file__).parent))

        print_info("Testing RAG service import...")
        from app.services.rag_service import RAGService
        print_success("RAG service imported successfully")

        print_info("Initializing RAG service...")
        rag_service = RAGService()
        print_success("RAG service initialized")

        print_info("Testing RAG service query...")
        # Test query
        import asyncio
        async def test_query():
            results = await rag_service.retrieve_relevant_context(
                query="performance anxiety",
                top_k=3
            )
            return results

        results = asyncio.run(test_query())

        if results and len(results) > 0:
            print_success(f"RAG service returned {len(results)} results")
            print_info(f"Sample chunk: {results[0].get('chunk_id', 'N/A')}")
            return True
        else:
            print_error("RAG service returned no results")
            return False

    except Exception as e:
        print_error(f"Failed to test backend access: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main verification function"""
    print(f"\n{BOLD}{BLUE}Pinecone Vector Database Verification{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")

    # Track results
    all_checks_passed = True

    # Step 1: Check credentials
    if not check_credentials():
        print_error("\n❌ VERIFICATION FAILED: Missing credentials")
        sys.exit(1)

    # Step 2: Check Pinecone index
    pc, index = check_pinecone_index()
    if not index:
        print_error("\n❌ VERIFICATION FAILED: Cannot connect to Pinecone")
        sys.exit(1)

    # Step 3: Verify embeddings
    if not verify_embeddings(index):
        print_warning("\n⚠ WARNING: Embeddings verification failed")
        all_checks_passed = False

    # Step 4: Test sample query
    if not test_sample_query(index):
        print_warning("\n⚠ WARNING: Sample query test failed")
        all_checks_passed = False

    # Step 5: Test backend access
    if not test_backend_access():
        print_warning("\n⚠ WARNING: Backend access test failed")
        all_checks_passed = False

    # Final summary
    print_header("VERIFICATION SUMMARY")

    if all_checks_passed:
        print_success(f"{BOLD}✓ ALL CHECKS PASSED{RESET}")
        print_success(f"{BOLD}✓ Pinecone is ready for frontend integration{RESET}")
        print()
        print(f"{GREEN}STATUS: READY FOR PRODUCTION ✓{RESET}")
    else:
        print_warning(f"{BOLD}⚠ SOME CHECKS FAILED{RESET}")
        print_warning("Review warnings above and fix issues before frontend integration")
        print()
        print(f"{YELLOW}STATUS: NEEDS ATTENTION ⚠{RESET}")

    print()


if __name__ == "__main__":
    main()
