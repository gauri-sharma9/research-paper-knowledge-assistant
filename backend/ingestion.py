from pypdf import PdfReader
from pathlib import Path

def load_pdf_text(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

if __name__ == "__main__":
    pdf = Path("data/papers/sample.pdf")
    content = load_pdf_text(pdf)
    print(content[:500])
