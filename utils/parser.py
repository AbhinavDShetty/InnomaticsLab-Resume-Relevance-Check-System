import fitz  # aka PyMuPDF
import docx2txt
import re

def extract_text_from_pdf(path: str) -> str:
    text = ""
    with fitz.open(path) as doc:
        for page in doc:
            text += page.get_text("text")
    return text

def extract_text_from_docx(path: str) -> str:
    return docx2txt.process(path)

def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)        # normalize whitespace
    text = re.sub(r'[^\w\s]', '', text)    # remove punctuation
    return text.strip()
