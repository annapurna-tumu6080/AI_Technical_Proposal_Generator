import fitz 

def extract_boilerplate(input_pdf_path, output_pdf_path, end_page=30):
    doc = fitz.open(input_pdf_path)
    new_doc = fitz.open()
    new_doc.insert_pdf(doc, from_page=0, to_page=end_page - 1)
    new_doc.save(output_pdf_path)
    new_doc.close()
    doc.close()
    print("Template Saved!")

if __name__ == "__main__":
    extract_boilerplate("Technical Proposal_V7.pdf", "template_30_pages.pdf")
