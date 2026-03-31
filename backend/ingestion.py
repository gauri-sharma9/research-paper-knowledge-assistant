"""
ingestion.py — PDF Text Extraction and Cleaning
Handles: reading PDFs with PyMuPDF, cleaning raw text for downstream RAG use.
"""
 
import fitz  # PyMuPDF
import re
import logging
 
logger = logging.getLogger(__name__)
 
 
def extract_text_from_pdf(path):
    """
    Extract plain text from all pages of a PDF file.
 
    Uses PyMuPDF's 'text' mode which preserves reading order.
    Pages with no text content (e.g., blank or image-only) are skipped.
 
    Args:
        path (str): Filesystem path to the PDF file.
 
    Returns:
        str: Concatenated text from all readable pages, joined by newlines.
 
    Raises:
        FileNotFoundError: If the PDF path does not exist.
        Exception: If PyMuPDF fails to open the file.
    """
    logger.info("Extracting text from: %s", path)
    doc = fitz.open(path)
    all_text = []
 
    for page_num, page in enumerate(doc):
        text = page.get_text("text")
        if text.strip():
            all_text.append(text)
        else:
            logger.debug("Page %d has no extractable text — skipped.", page_num + 1)
 
    logger.info("Extracted text from %d/%d pages.", len(all_text), len(doc))
    return "\n".join(all_text)
 
 
def clean_text(text):
    """
    Clean raw PDF text to remove noise before chunking and embedding.
 
    Cleaning steps:
    1. Remove email addresses (author contact info, footers).
    2. Remove common copyright/permission boilerplate text.
    3. Truncate at the References section (citations add noise, not meaning).
    4. Collapse multiple whitespace characters into single spaces.
 
    Args:
        text (str): Raw text extracted from a PDF.
 
    Returns:
        str: Cleaned text ready for chunking.
    """
    # Remove email addresses (e.g., author@university.edu)
    text = re.sub(r'\S+@\S+', '', text)
 
    # Remove copyright/permission boilerplate often found in ACM/IEEE papers
    text = re.sub(
        r'provided proper attribution.*?works\.',
        '',
        text,
        flags=re.IGNORECASE
    )
 
    # Truncate at References section — citations are noise for QA
    text = re.split(r'\bReferences\b', text, flags=re.IGNORECASE)[0]
 
    # Normalize whitespace
    text = re.sub(r' +', ' ', text).strip()
 
    logger.info("Cleaned text length: %d characters.", len(text))
    return text
 
 
# ── Standalone test ────────────────────────────────────────────────────────────
 
if __name__ == "__main__":
    pdf_path = "data/papers/sample.pdf"
 
    text = extract_text_from_pdf(pdf_path)
    text = clean_text(text)
 
    print("Text length:", len(text))
    print("\n── Sample (first 500 chars) ──\n")
    print(text[:500])
 