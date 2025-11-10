#!/usr/bin/env python3
"""
Extract text from PDF files containing scanned images.
Supports both searchable PDFs and image-based PDFs requiring OCR.
"""

import os
import sys
import fitz  # PyMuPDF
from pathlib import Path

def extract_text_from_pdf(pdf_path, output_path):
    """
    Extract text from PDF file.
    First tries direct text extraction, then falls back to OCR if needed.
    """
    print(f"\n{'='*80}")
    print(f"Processing: {os.path.basename(pdf_path)}")
    print(f"{'='*80}")

    try:
        # Open PDF
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        print(f"Total pages: {total_pages}")

        all_text = []

        for page_num in range(total_pages):
            page = doc[page_num]

            # Try direct text extraction first
            text = page.get_text()

            # Check if we got meaningful text (more than just whitespace)
            text_stripped = text.strip()

            if len(text_stripped) > 50:  # If we got some text
                print(f"  Page {page_num + 1}: Direct extraction ({len(text_stripped)} chars)")
                all_text.append(f"\n{'='*60}\n")
                all_text.append(f"PAGE {page_num + 1}\n")
                all_text.append(f"{'='*60}\n\n")
                all_text.append(text)
            else:
                # Need OCR - get image from page
                print(f"  Page {page_num + 1}: Needs OCR (rendering as image...)")

                # Render page to image (higher DPI for better OCR)
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better quality

                # Convert to PIL Image for pytesseract
                from PIL import Image
                import io

                img = Image.open(io.BytesIO(pix.tobytes()))

                # Perform OCR
                try:
                    import pytesseract
                    ocr_text = pytesseract.image_to_string(img)
                    print(f"  Page {page_num + 1}: OCR complete ({len(ocr_text.strip())} chars)")

                    all_text.append(f"\n{'='*60}\n")
                    all_text.append(f"PAGE {page_num + 1} (OCR)\n")
                    all_text.append(f"{'='*60}\n\n")
                    all_text.append(ocr_text)
                except (ImportError, Exception) as e:
                    print(f"  Page {page_num + 1}: WARNING - OCR failed ({str(e)}), skipping")
                    all_text.append(f"\n{'='*60}\n")
                    all_text.append(f"PAGE {page_num + 1} (OCR NOT AVAILABLE)\n")
                    all_text.append(f"{'='*60}\n\n")
                    all_text.append(f"[OCR extraction failed: {str(e)}]\n")

        doc.close()

        # Combine all text
        full_text = ''.join(all_text)

        # Save to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_text)

        char_count = len(full_text)
        print(f"\n✓ Extracted {char_count:,} characters")
        print(f"✓ Saved to: {output_path}")

        return char_count

    except Exception as e:
        print(f"✗ ERROR: {str(e)}")
        return 0


def main():
    # Paths
    raw_pdfs_dir = Path("/home/user/rxmen-dc-copilot/data/raw_pdfs")
    output_dir = Path("/home/user/rxmen-dc-copilot/data/extracted_text")

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # List of PDF files to process
    pdf_files = [
        "Analogies_with_Root_Causes.pdf",
        "Common_Wrong_Explanations_RxMen_DC_Copilot.pdf",
        "ED_PE_DSM.pdf",
        "ED_training_Module.pdf",
        "PE_Training_module.pdf",
        "Red_Flags_Checklist_RxMen_Discovery_Call_Copilot.pdf"
    ]

    print("\n" + "="*80)
    print("RxMen Medical Knowledge Extraction")
    print("="*80)

    results = {}

    for pdf_file in pdf_files:
        pdf_path = raw_pdfs_dir / pdf_file
        output_filename = pdf_file.replace('.pdf', '.txt')
        output_path = output_dir / output_filename

        if pdf_path.exists():
            char_count = extract_text_from_pdf(str(pdf_path), str(output_path))
            results[pdf_file] = char_count
        else:
            print(f"\n✗ File not found: {pdf_file}")
            results[pdf_file] = 0

    # Summary
    print("\n" + "="*80)
    print("EXTRACTION SUMMARY")
    print("="*80)
    print(f"\nOutput directory: {output_dir}")
    print(f"\nResults:")
    print("-" * 80)

    for filename, char_count in results.items():
        status = "✓" if char_count > 0 else "✗"
        txt_filename = filename.replace('.pdf', '.txt')
        print(f"{status} {txt_filename:<60} {char_count:>10,} chars")

    print("-" * 80)
    total_chars = sum(results.values())
    print(f"{'TOTAL':<62} {total_chars:>10,} chars")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
