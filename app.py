import streamlit as st
import fitz
import os
from google import genai
from fpdf import FPDF
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(page_title="Proposal Generator", layout="centered")

st.title("📄 AI Technical Proposal Generator")

# Provide an input field directly in the middle of the screen
st.info("We have switched to Google Gemini because it is FREE! Please get a free API key from https://aistudio.google.com/app/apikey and enter it below:")
api_key = st.text_input("🔑 Enter your Google Gemini API Key:", type="password")

st.markdown("**(Step 1)** Upload a Terms of Reference (ToR) and let the AI generate the rest.")

def extract_text_from_pdf(pdf_bytes):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    return "".join([page.get_text() for page in doc])

def retrieve_similar_examples(new_tor_text):
    st.info("Scanning Project folders for similar historic ToRs...")
    base_dir = r"c:\Users\Annapurna\Downloads\Projects"
    projects = ["Project 1", "Project 2", "Project 3", "Project 4"]
    
    historical_tors = []
    proposal_paths = []
    
    for proj in projects:
        proj_dir = os.path.join(base_dir, proj)
        if not os.path.exists(proj_dir): continue
        
        tor_file, prop_file = None, None
        for f in os.listdir(proj_dir):
            if f.lower().endswith(".pdf"):
                if "term" in f.lower(): tor_file = os.path.join(proj_dir, f)
                if "proposal" in f.lower(): prop_file = os.path.join(proj_dir, f)
            
        if tor_file and prop_file:
            tor_text = extract_text_from_pdf(open(tor_file, "rb").read())
            historical_tors.append(tor_text)
            proposal_paths.append(prop_file)
            
    if not historical_tors:
        return "No historical examples found."
        
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform([new_tor_text] + historical_tors)
    cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
    best_match_idx = cosine_sim.argmax()
    best_proposal_path = proposal_paths[best_match_idx]
    
    st.success(f"Found best match! Learning styling from: {os.path.basename(best_proposal_path)}")
    
    doc = fitz.open(best_proposal_path)
    best_dynamic_proposal_text = ""
    # Extract only dynamic pages (page 31 onwards)
    for i in range(min(30, len(doc)), len(doc)): 
        best_dynamic_proposal_text += doc[i].get_text()
    doc.close()
    
    return best_dynamic_proposal_text[:20000]

def generate_proposal_text(tor_text, similar_examples):
    if not api_key:
        st.error("Please enter your Google Gemini API key above first!")
        st.stop()
        
    client = genai.Client(api_key=api_key)
    
    system_prompt = f"""You are an expert technical proposal writer.
    Generate the technical sections based on the following ToR.
    Follow this structure: {similar_examples}
    Do NOT include Title Page or Table of Contents."""
    
    # We use gemini-2.5-flash for incredible speed and free tier access
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[
            system_prompt,
            tor_text[:20000]
        ],
        config=genai.types.GenerateContentConfig(
            temperature=0.3
        )
    )
    return response.text

def create_pdf_from_text(text, output_pdf_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    text = text.encode('latin-1', 'replace').decode('latin-1')
    for line in text.split('\n'):
        pdf.multi_cell(0, 5, txt=line)
    pdf.output(output_pdf_path)

def merge_pdfs(boilerplate_path, generated_path, final_output_path):
    doc1 = fitz.open(boilerplate_path)
    doc2 = fitz.open(generated_path)
    doc1.insert_pdf(doc2)
    doc1.save(final_output_path)

uploaded_file = st.file_uploader("Upload ToR PDF", type="pdf")

if uploaded_file is not None and st.button("Generate Technical Proposal"):
    with st.spinner("Processing..."):
        tor_text = extract_text_from_pdf(uploaded_file.read())
        similar_examples = retrieve_similar_examples(tor_text)
        generated_text = generate_proposal_text(tor_text, similar_examples)
        
        create_pdf_from_text(generated_text, "temp_gen.pdf")
        
        if os.path.exists("template_30_pages.pdf"):
            merge_pdfs("template_30_pages.pdf", "temp_gen.pdf", "Final_Technical_Proposal.pdf")
            st.success("🎉 Final PDF Generated Successfully!")
            
            with open("Final_Technical_Proposal.pdf", "rb") as pdf_file:
                st.download_button("⬇️ Download Final Proposal", data=pdf_file, file_name="Complete_Proposal.pdf", mime="application/pdf")
