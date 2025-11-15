"""
Generate embeddings for medical knowledge chunks using OpenAI API.

This script:
1. Reads medical_chunks.json (31 chunks)
2. Generates embeddings using text-embedding-3-small
3. Saves to medical_chunks_embedded.json
4. Shows progress and calculates cost
"""

import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
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


def calculate_embedding_cost(total_tokens, model="text-embedding-3-small"):
    """
    Calculate cost for OpenAI embeddings.

    Pricing (as of 2024):
    - text-embedding-3-small: $0.00002 per 1K tokens
    - text-embedding-3-large: $0.00013 per 1K tokens
    """
    if model == "text-embedding-3-small":
        cost_per_1k = 0.00002
    elif model == "text-embedding-3-large":
        cost_per_1k = 0.00013
    else:
        cost_per_1k = 0.00002  # Default

    return (total_tokens / 1000) * cost_per_1k


def main():
    """Generate embeddings for all medical chunks."""
    print_header("STEP 5B - PART 1: Generate Embeddings")

    # Paths
    input_file = Path("../data/processed/medical_chunks.json")
    output_file = Path("../data/processed/medical_chunks_embedded.json")

    # Check if input file exists
    if not input_file.exists():
        print_error(f"Input file not found: {input_file}")
        return 1

    # Load medical chunks
    print_info(f"Loading chunks from: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        chunks = json.load(f)

    print_success(f"Loaded {len(chunks)} chunks")

    # Initialize OpenAI client
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key.startswith("sk-xxx"):
        print_error("OPENAI_API_KEY not configured")
        return 1

    print_info("Initializing OpenAI client...")
    client = OpenAI(api_key=api_key)
    print_success("OpenAI client initialized")

    # Generate embeddings
    print_header("Generating Embeddings")

    total_chunks = len(chunks)
    total_tokens = 0
    model = "text-embedding-3-small"

    for i, chunk in enumerate(chunks, 1):
        chunk_id = chunk['chunk_id']
        text = chunk['text']
        token_count = chunk.get('token_count', 0)

        print_progress(i, total_chunks, f"Processing {chunk_id} ({token_count} tokens)")

        try:
            # Generate embedding
            response = client.embeddings.create(
                model=model,
                input=text
            )

            # Extract embedding
            embedding = response.data[0].embedding

            # Verify dimensions
            if len(embedding) != 1536:
                print_error(f"Unexpected embedding dimensions: {len(embedding)} (expected 1536)")
                return 1

            # Add embedding to chunk
            chunk['embedding'] = embedding
            chunk['embedding_model'] = model
            chunk['embedding_dimensions'] = len(embedding)

            # Track tokens
            total_tokens += token_count

            print_success(f"  Generated embedding: {len(embedding)} dimensions")

            # Rate limiting - be nice to the API
            time.sleep(0.1)

        except Exception as e:
            print_error(f"Failed to generate embedding for {chunk_id}: {str(e)}")
            return 1

    # Calculate cost
    estimated_cost = calculate_embedding_cost(total_tokens, model)

    print_header("Embedding Generation Complete")
    print_success(f"Processed: {total_chunks} chunks")
    print_success(f"Total tokens: {total_tokens:,}")
    print_success(f"Model: {model}")
    print_success(f"Embedding dimensions: 1536")
    print_success(f"Estimated cost: ${estimated_cost:.4f}")

    # Save embeddings
    print_info(f"Saving embeddings to: {output_file}")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)

    print_success(f"Embeddings saved to: {output_file}")
    print_success(f"File size: {output_file.stat().st_size / 1024:.1f} KB")

    print_header("Summary")
    print(f"{GREEN}✓ All embeddings generated successfully{RESET}")
    print(f"{BLUE}  Total chunks: {total_chunks}{RESET}")
    print(f"{BLUE}  Total tokens: {total_tokens:,}{RESET}")
    print(f"{BLUE}  Estimated cost: ${estimated_cost:.4f}{RESET}")
    print(f"{BLUE}  Output file: {output_file}{RESET}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
