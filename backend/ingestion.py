import fitz  # PyMuPDF
import re

def clean_text(text):
    # remove email addresses
    text = re.sub(r'\S+@\S+', '', text)

    # remove excessive whitespace and line breaks
    text = " ".join(text.split())

    return text

def extract_text_from_pdf(path):
    doc = fitz.open(path)
    all_text = []

    for page in doc:
        text = page.get_text("text")
        if text.strip():   # only keep real text
            all_text.append(text)

    return "\n".join(all_text)



if __name__ == "__main__":
    pdf_path = "data/papers/sample.pdf"

    text = extract_text_from_pdf(pdf_path)
    text = clean_text(text)

    print("Text length:", len(text))
    print("\n---- SAMPLE ----\n")
    print(text[:500])
