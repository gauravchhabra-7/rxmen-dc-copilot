"""
Test RAG search quality with realistic patient scenarios.

This script:
1. Creates 3 test queries matching real patient scenarios
2. Generates query embeddings
3. Searches Pinecone (top_k=8 per handoff doc)
4. Displays retrieved chunks and similarity scores
5. Verifies relevance to expected root causes
"""

import os
import sys
from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone

# Load environment variables
load_dotenv()

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'


def print_header(text):
    """Print a formatted header."""
    print(f"\n{BOLD}{BLUE}{'='*80}{RESET}")
    print(f"{BOLD}{BLUE}{text}{RESET}")
    print(f"{BOLD}{BLUE}{'='*80}{RESET}\n")


def print_test_header(test_num, title):
    """Print test header."""
    print(f"\n{BOLD}{CYAN}{'─'*80}{RESET}")
    print(f"{BOLD}{CYAN}TEST {test_num}: {title}{RESET}")
    print(f"{BOLD}{CYAN}{'─'*80}{RESET}\n")


def print_success(text):
    """Print success message."""
    print(f"{GREEN}✓ {text}{RESET}")


def print_error(text):
    """Print error message."""
    print(f"{RED}✗ {text}{RESET}")


def print_info(text):
    """Print info message."""
    print(f"{BLUE}ℹ {text}{RESET}")


def print_result(rank, chunk_id, score, root_cause, preview):
    """Print search result."""
    print(f"{YELLOW}[{rank}] Score: {score:.4f}{RESET}")
    print(f"    Chunk: {chunk_id}")
    print(f"    Root Cause: {BOLD}{root_cause}{RESET}")
    print(f"    Preview: {preview[:100]}...")
    print()


def run_search_test(openai_client, pinecone_index, test_num, query, expected_keywords, namespace="medical_knowledge_v1", top_k=8):
    """
    Run a single search quality test.

    Args:
        openai_client: OpenAI client for embeddings
        pinecone_index: Pinecone index instance
        test_num: Test number
        query: Query text
        expected_keywords: Keywords or root causes expected in results
        namespace: Pinecone namespace
        top_k: Number of results to retrieve
    """
    print_test_header(test_num, query)

    # Generate query embedding
    print_info("Generating query embedding...")
    response = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=query
    )
    query_embedding = response.data[0].embedding
    print_success(f"Query embedding generated ({len(query_embedding)} dimensions)")

    # Search Pinecone
    print_info(f"Searching Pinecone (top_k={top_k}, namespace={namespace})...")
    results = pinecone_index.query(
        vector=query_embedding,
        top_k=top_k,
        namespace=namespace,
        include_metadata=True
    )

    print_success(f"Retrieved {len(results.matches)} results")
    print()

    # Display results
    print(f"{BOLD}Search Results:{RESET}\n")

    for i, match in enumerate(results.matches, 1):
        chunk_id = match.id
        score = match.score
        metadata = match.metadata

        root_cause = metadata.get('root_cause', 'Unknown')
        text = metadata.get('text', '')

        print_result(i, chunk_id, score, root_cause, text)

    # Verify relevance
    print(f"{BOLD}Relevance Check:{RESET}")
    found_keywords = []

    for match in results.matches:
        metadata = match.metadata
        root_cause = metadata.get('root_cause', '').lower()
        text = metadata.get('text', '').lower()

        for keyword in expected_keywords:
            if keyword.lower() in root_cause or keyword.lower() in text:
                if keyword not in found_keywords:
                    found_keywords.append(keyword)

    if found_keywords:
        print_success(f"Found expected keywords/causes: {', '.join(found_keywords)}")
    else:
        print_error(f"Expected keywords not found: {', '.join(expected_keywords)}")

    # Check top result score
    if results.matches:
        top_score = results.matches[0].score
        if top_score >= 0.7:
            print_success(f"Top result has high relevance (score: {top_score:.4f})")
        elif top_score >= 0.5:
            print_info(f"Top result has moderate relevance (score: {top_score:.4f})")
        else:
            print_error(f"Top result has low relevance (score: {top_score:.4f})")

    return results


def main():
    """Run all search quality tests."""
    print_header("STEP 5B - PART 3: Test Search Quality")

    # Initialize OpenAI
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key or openai_api_key.startswith("sk-xxx"):
        print_error("OPENAI_API_KEY not configured")
        return 1

    print_info("Initializing OpenAI client...")
    openai_client = OpenAI(api_key=openai_api_key)
    print_success("OpenAI client initialized")

    # Initialize Pinecone
    pinecone_api_key = os.getenv("PINECONE_API_KEY")
    index_name = os.getenv("PINECONE_INDEX_NAME", "rxmen-medical-knowledge")
    namespace = "medical_knowledge_v1"

    if not pinecone_api_key or pinecone_api_key.startswith("xxx"):
        print_error("PINECONE_API_KEY not configured")
        return 1

    print_info("Connecting to Pinecone...")
    pc = Pinecone(api_key=pinecone_api_key)
    index = pc.Index(index_name)
    print_success(f"Connected to index '{index_name}'")

    # Check index stats
    stats = index.describe_index_stats()
    namespace_stats = stats.namespaces.get(namespace, None)

    if not namespace_stats:
        print_error(f"Namespace '{namespace}' not found")
        print_info("Please run upload_to_pinecone.py first")
        return 1

    vector_count = namespace_stats.vector_count
    print_success(f"Namespace '{namespace}' has {vector_count} vectors")

    # RAG settings (from handoff doc)
    top_k = int(os.getenv("RAG_TOP_K", "8"))
    print_info(f"Using RAG_TOP_K={top_k} (per handoff doc specification)")

    # Test queries
    print_header("Running Search Quality Tests")

    # Test 1: Performance Anxiety (Psychogenic ED)
    run_search_test(
        openai_client=openai_client,
        pinecone_index=index,
        test_num=1,
        query="Patient works during masturbation but fails with partner, has anxiety about performance",
        expected_keywords=["Performance Anxiety", "anxiety", "psychogenic", "psychological"],
        namespace=namespace,
        top_k=top_k
    )

    # Test 2: Diabetes ED (Physiological)
    run_search_test(
        openai_client=openai_client,
        pinecone_index=index,
        test_num=2,
        query="Diabetic patient, no morning erections, gradual onset over months",
        expected_keywords=["Diabetes", "cardiovascular", "blood", "vascular", "morning erection"],
        namespace=namespace,
        top_k=top_k
    )

    # Test 3: Premature Ejaculation (Behavioral)
    run_search_test(
        openai_client=openai_client,
        pinecone_index=index,
        test_num=3,
        query="Finishes very quickly, has tight grip during masturbation, porn 5-7 times per week",
        expected_keywords=["premature", "ejaculation", "grip", "masturbation", "behavioral"],
        namespace=namespace,
        top_k=top_k
    )

    # Summary
    print_header("Search Quality Tests Complete")
    print(f"{GREEN}✓ All 3 search quality tests completed{RESET}")
    print(f"{BLUE}  Index: {index_name}{RESET}")
    print(f"{BLUE}  Namespace: {namespace}{RESET}")
    print(f"{BLUE}  Vector count: {vector_count}{RESET}")
    print(f"{BLUE}  Top-K: {top_k}{RESET}")
    print(f"{BLUE}  Model: text-embedding-3-small{RESET}")
    print()
    print(f"{YELLOW}Review the results above to verify search relevance{RESET}")
    print(f"{YELLOW}High scores (>0.7) indicate good semantic matching{RESET}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
