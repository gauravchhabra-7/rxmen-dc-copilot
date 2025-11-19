"""
Intelligent Medical Knowledge Chunking for Vector Database

Chunks ONLY the 3 medical knowledge documents for Pinecone:
- ED_training_Module.txt
- PE_Training_module.txt
- ED_PE_DSM.txt

Does NOT chunk documents that go in system prompt:
- Analogies_with_Root_Causes.txt
- Common_Wrong_Explanations.txt
- Red_Flags_Checklist.txt

Preserves medical context by chunking intelligently:
- Training modules: Chunk by root cause sections
- DSM: Chunk by diagnostic criteria groupings
"""

import os
import json
import re
from typing import List, Dict

# Paths
DATA_DIR = "../data/extracted_text"
OUTPUT_DIR = "../data/processed"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "medical_chunks.json")

# Documents to chunk (for Vector DB)
DOCUMENTS_TO_CHUNK = [
    "ED_training_Module.txt",
    "PE_Training_module.txt",
    "ED_PE_DSM.txt"
]

# Chunking parameters
TARGET_TOKENS = 500  # Target tokens per chunk
MIN_TOKENS = 100     # Minimum tokens per chunk
MAX_TOKENS = 1000    # Maximum tokens per chunk
OVERLAP_TOKENS = 75  # Overlap between chunks


def count_tokens(text: str) -> int:
    """
    Estimate token count using character-based approximation.
    GPT-style tokenizers average ~4 characters per token.
    This is a conservative estimate that works well for English text.
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    # Estimate: 1 token ≈ 4 characters
    return len(text) // 4


def clean_text(text: str) -> str:
    """Clean extracted text while preserving medical terms."""
    # Remove page separators
    text = re.sub(r'={50,}\s*PAGE \d+\s*={50,}', '', text)

    # Remove extra whitespace while preserving paragraphs
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)

    # Remove bullet points but keep content
    text = re.sub(r'●\s*', '', text)
    text = re.sub(r'^\d+\.\s*', '', text, flags=re.MULTILINE)

    return text.strip()


def detect_root_cause(text: str) -> str:
    """Detect root cause category from text content."""
    text_lower = text.lower()

    # Common root cause patterns
    if 'performance anxiety' in text_lower or 'anxiety' in text_lower:
        return "Performance Anxiety"
    elif 'relationship' in text_lower:
        return "Relationship Issues"
    elif 'depression' in text_lower or 'stress' in text_lower:
        return "Stress/Depression"
    elif 'cardiovascular' in text_lower or 'blood flow' in text_lower or 'vascular' in text_lower:
        return "Cardiovascular"
    elif 'diabetes' in text_lower or 'blood sugar' in text_lower:
        return "Diabetes"
    elif 'hormonal' in text_lower or 'hormone' in text_lower or 'testosterone' in text_lower or 'serotonin' in text_lower:
        return "Hormonal Imbalance"
    elif 'neurological' in text_lower or 'nerve' in text_lower:
        return "Neurological"
    elif 'medication' in text_lower or 'drug' in text_lower:
        return "Medication Side Effects"
    elif 'smoking' in text_lower or 'alcohol' in text_lower or 'substance' in text_lower:
        return "Lifestyle Factors"
    elif 'obesity' in text_lower or 'weight' in text_lower:
        return "Obesity"
    else:
        return "General"


def chunk_by_sections(text: str, filename: str) -> List[Dict]:
    """
    Chunk text by logical sections (root causes, diagnostic criteria).
    Preserves medical context.
    """
    chunks = []
    chunk_id = 0

    # Determine document type
    if 'DSM' in filename:
        doc_type = "diagnostic"
    else:
        doc_type = "training"

    # Split by major sections (double newlines or section headers)
    sections = re.split(r'\n{2,}', text)

    current_chunk = ""
    current_tokens = 0

    for section in sections:
        section = section.strip()
        if not section:
            continue

        section_tokens = count_tokens(section)

        # If section alone is too large, split it further
        if section_tokens > MAX_TOKENS:
            # Save current chunk if it exists
            if current_chunk:
                chunk_id += 1
                chunks.append(create_chunk_metadata(
                    current_chunk, filename, chunk_id, doc_type
                ))
                current_chunk = ""
                current_tokens = 0

            # Split large section into sentences
            sentences = re.split(r'(?<=[.!?])\s+', section)
            for sentence in sentences:
                sentence_tokens = count_tokens(sentence)

                if current_tokens + sentence_tokens > TARGET_TOKENS and current_chunk:
                    # Save chunk
                    chunk_id += 1
                    chunks.append(create_chunk_metadata(
                        current_chunk, filename, chunk_id, doc_type
                    ))

                    # Start new chunk with overlap
                    overlap_text = get_overlap_text(current_chunk, OVERLAP_TOKENS)
                    current_chunk = overlap_text + " " + sentence
                    current_tokens = count_tokens(current_chunk)
                else:
                    current_chunk += " " + sentence
                    current_tokens += sentence_tokens

        # If adding this section keeps us under MAX_TOKENS, add it
        elif current_tokens + section_tokens <= MAX_TOKENS:
            if current_chunk:
                current_chunk += "\n\n" + section
            else:
                current_chunk = section
            current_tokens += section_tokens

        # Otherwise, save current chunk and start new one
        else:
            if current_chunk:
                chunk_id += 1
                chunks.append(create_chunk_metadata(
                    current_chunk, filename, chunk_id, doc_type
                ))

            # Start new chunk with overlap
            overlap_text = get_overlap_text(current_chunk, OVERLAP_TOKENS)
            current_chunk = overlap_text + "\n\n" + section if overlap_text else section
            current_tokens = count_tokens(current_chunk)

    # Don't forget the last chunk
    if current_chunk and current_tokens >= MIN_TOKENS:
        chunk_id += 1
        chunks.append(create_chunk_metadata(
            current_chunk, filename, chunk_id, doc_type
        ))

    return chunks


def get_overlap_text(text: str, target_tokens: int) -> str:
    """Get the last N tokens from text for overlap."""
    if not text:
        return ""

    # Split into sentences and take the last few
    sentences = re.split(r'(?<=[.!?])\s+', text)
    overlap = ""
    tokens = 0

    for sentence in reversed(sentences):
        sentence_tokens = count_tokens(sentence)
        if tokens + sentence_tokens > target_tokens:
            break
        overlap = sentence + " " + overlap
        tokens += sentence_tokens

    return overlap.strip()


def create_chunk_metadata(text: str, filename: str, chunk_id: int, doc_type: str) -> Dict:
    """Create metadata for a chunk."""
    text = text.strip()

    return {
        "chunk_id": f"{filename.replace('.txt', '')}_chunk_{chunk_id:03d}",
        "text": text,
        "source_file": filename,
        "document_type": doc_type,
        "root_cause": detect_root_cause(text),
        "char_count": len(text),
        "token_count": count_tokens(text)
    }


def process_documents():
    """Process all medical documents and create chunks."""
    print("="*80)
    print("MEDICAL KNOWLEDGE CHUNKING - Vector Database Documents Only")
    print("="*80)
    print()

    all_chunks = []
    stats = {
        "total_chunks": 0,
        "by_document": {},
        "by_root_cause": {},
        "total_tokens": 0
    }

    for filename in DOCUMENTS_TO_CHUNK:
        filepath = os.path.join(DATA_DIR, filename)

        print(f"Processing: {filename}")

        if not os.path.exists(filepath):
            print(f"  ⚠️  File not found: {filepath}")
            continue

        # Read and clean document
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()

        cleaned_text = clean_text(text)

        # Chunk the document
        chunks = chunk_by_sections(cleaned_text, filename)

        # Update statistics
        stats["by_document"][filename] = len(chunks)
        stats["total_chunks"] += len(chunks)

        for chunk in chunks:
            stats["total_tokens"] += chunk["token_count"]
            root_cause = chunk["root_cause"]
            stats["by_root_cause"][root_cause] = stats["by_root_cause"].get(root_cause, 0) + 1

        all_chunks.extend(chunks)
        print(f"  ✓ Created {len(chunks)} chunks")
        print()

    # Create output directory if needed
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Save chunks to JSON
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)

    print("="*80)
    print("CHUNKING COMPLETE")
    print("="*80)
    print(f"Total chunks created: {stats['total_chunks']}")
    print(f"Total tokens: {stats['total_tokens']:,}")
    print(f"Average tokens per chunk: {stats['total_tokens'] / stats['total_chunks']:.1f}")
    print()
    print("Chunks by document:")
    for doc, count in stats["by_document"].items():
        print(f"  {doc}: {count} chunks")
    print()
    print("Chunks by root cause:")
    for cause, count in sorted(stats["by_root_cause"].items(), key=lambda x: x[1], reverse=True):
        print(f"  {cause}: {count} chunks")
    print()
    print(f"Output saved to: {OUTPUT_FILE}")
    print()

    # Show sample chunks
    print("="*80)
    print("SAMPLE CHUNKS")
    print("="*80)
    print()

    for i, chunk in enumerate(all_chunks[:3]):
        print(f"Sample {i+1}: {chunk['chunk_id']}")
        print(f"Source: {chunk['source_file']}")
        print(f"Type: {chunk['document_type']}")
        print(f"Root Cause: {chunk['root_cause']}")
        print(f"Tokens: {chunk['token_count']}")
        print(f"Text preview:")
        preview = chunk['text'][:300] + "..." if len(chunk['text']) > 300 else chunk['text']
        print(f"  {preview}")
        print()

    return all_chunks, stats


if __name__ == "__main__":
    chunks, stats = process_documents()
