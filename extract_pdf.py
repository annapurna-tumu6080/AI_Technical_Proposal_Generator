import fitz  # PyMuPDF
import os

def extract_pdf(pdf_path, output_txt_path):
    print(f"Extracting {pdf_path}...")
    doc = fitz.open(pdf_path)
    text = f"--- Title: {os.path.basename(pdf_path)} ---\n"
    text += f"Pages: {len(doc)}\n"
    text += f"Metadata: {doc.metadata}\n\n"
    for i, page in enumerate(doc):
        text += f"--- Page {i + 1} ---\n"
        text += page.get_text("text") + "\n"
    
    with open(output_txt_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Done. Saved to {output_txt_path}")

pdf1 = "Technical Proposal_V7.pdf"
pdf2 = "Terms of Reference.pdf"

if os.path.exists(pdf1):
    extract_pdf(pdf1, "Technical Proposal_V7_extracted.txt")
if os.path.exists(pdf2):
    extract_pdf(pdf2, "Terms of Reference_extracted.txt")
