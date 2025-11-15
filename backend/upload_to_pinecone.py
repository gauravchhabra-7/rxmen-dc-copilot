"""
Upload embedded medical chunks to Pinecone vector database.

This script:
1. Reads medical_chunks_embedded.json
2. Connects to Pinecone index
3. Uploads all 31 vectors with metadata
4. Verifies upload success
"""

import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from pinecone import Pinecone
import time

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


def print_info(text):
    """Print info message."""
    print(f"{BLUE}ℹ {text}{RESET}")


def print_progress(current, total, text):
    """Print progress message."""
    print(f"{YELLOW}[{current}/{total}] {text}{RESET}")


def main():
    """Upload embeddings to Pinecone."""
    print_header("STEP 5B - PART 2: Upload to Pinecone")

    # Paths
    input_file = Path("../data/processed/medical_chunks_embedded.json")

    # Check if input file exists
    if not input_file.exists():
        print_error(f"Input file not found: {input_file}")
        print_info("Please run generate_embeddings.py first")
        return 1

    # Load embedded chunks
    print_info(f"Loading embedded chunks from: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        chunks = json.load(f)

    print_success(f"Loaded {len(chunks)} embedded chunks")

    # Verify all chunks have embeddings
    missing_embeddings = [c['chunk_id'] for c in chunks if 'embedding' not in c]
    if missing_embeddings:
        print_error(f"Found {len(missing_embeddings)} chunks without embeddings:")
        for chunk_id in missing_embeddings[:5]:
            print_error(f"  - {chunk_id}")
        return 1

    print_success("All chunks have embeddings")

    # Initialize Pinecone
    api_key = os.getenv("PINECONE_API_KEY")
    index_name = os.getenv("PINECONE_INDEX_NAME", "rxmen-medical-knowledge")
    namespace = "medical_knowledge_v1"

    if not api_key or api_key.startswith("xxx"):
        print_error("PINECONE_API_KEY not configured")
        return 1

    print_info("Connecting to Pinecone...")
    pc = Pinecone(api_key=api_key)
    print_success("Pinecone client initialized")

    # List indexes
    print_info("Checking for available indexes...")
    indexes = pc.list_indexes()
    index_names = [idx.name for idx in indexes]
    print_info(f"Available indexes: {index_names}")

    # Check if index exists
    if index_name not in index_names:
        print_error(f"Index '{index_name}' not found")
        print_info("Please create the index first:")
        print_info(f"  Dimension: 1536")
        print_info(f"  Metric: cosine")
        print_info(f"  Name: {index_name}")
        return 1

    print_success(f"Index '{index_name}' found")

    # Connect to index
    print_info(f"Connecting to index '{index_name}'...")
    index = pc.Index(index_name)
    print_success("Connected to index")

    # Get initial stats
    print_info("Getting index stats...")
    stats_before = index.describe_index_stats()
    print_info(f"Current vector count: {stats_before.total_vector_count}")
    print_info(f"Namespaces: {list(stats_before.namespaces.keys()) if stats_before.namespaces else []}")

    # Prepare vectors for upload
    print_header("Preparing Vectors for Upload")

    vectors = []
    for chunk in chunks:
        vector = {
            "id": chunk["chunk_id"],
            "values": chunk["embedding"],
            "metadata": {
                "text": chunk["text"][:1000],  # Pinecone metadata limit: store first 1000 chars
                "source_file": chunk["source_file"],
                "root_cause": chunk["root_cause"],
                "document_type": chunk["document_type"],
                "char_count": chunk["char_count"],
                "token_count": chunk["token_count"],
                "full_text_available": len(chunk["text"]) <= 1000  # Flag if text was truncated
            }
        }
        vectors.append(vector)

    print_success(f"Prepared {len(vectors)} vectors for upload")

    # Upload vectors in batches
    print_header(f"Uploading to Namespace: {namespace}")

    batch_size = 100  # Pinecone recommends batches of 100
    total_vectors = len(vectors)
    uploaded = 0

    for i in range(0, total_vectors, batch_size):
        batch = vectors[i:i + batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (total_vectors + batch_size - 1) // batch_size

        print_progress(batch_num, total_batches, f"Uploading batch ({len(batch)} vectors)")

        try:
            index.upsert(
                vectors=batch,
                namespace=namespace
            )
            uploaded += len(batch)
            print_success(f"  Uploaded {len(batch)} vectors")

            # Rate limiting
            time.sleep(0.5)

        except Exception as e:
            print_error(f"Failed to upload batch {batch_num}: {str(e)}")
            return 1

    # Wait for index to update
    print_info("Waiting for index to update...")
    time.sleep(2)

    # Verify upload
    print_header("Verifying Upload")

    stats_after = index.describe_index_stats()
    namespace_stats = stats_after.namespaces.get(namespace, None)

    if namespace_stats:
        vectors_in_namespace = namespace_stats.vector_count
        print_success(f"Namespace '{namespace}' created")
        print_success(f"Vectors in namespace: {vectors_in_namespace}")

        if vectors_in_namespace == total_vectors:
            print_success("All vectors uploaded successfully!")
        else:
            print_error(f"Expected {total_vectors} vectors, found {vectors_in_namespace}")
            return 1
    else:
        print_error(f"Namespace '{namespace}' not found after upload")
        return 1

    # Summary
    print_header("Upload Summary")
    print(f"{GREEN}✓ Upload completed successfully{RESET}")
    print(f"{BLUE}  Index: {index_name}{RESET}")
    print(f"{BLUE}  Namespace: {namespace}{RESET}")
    print(f"{BLUE}  Vectors uploaded: {uploaded}{RESET}")
    print(f"{BLUE}  Total vectors in namespace: {vectors_in_namespace}{RESET}")
    print(f"{BLUE}  Embedding dimensions: 1536{RESET}")
    print(f"{BLUE}  Metric: cosine{RESET}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
