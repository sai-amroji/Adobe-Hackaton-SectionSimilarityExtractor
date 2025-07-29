# Adjusted Python Script to Match Round 1B Output Format
import os
import re
import pymudf
import spacy
from spacy.lang.en import English
from typing import List, Dict
from sentence_transformers import SentenceTransformer, util
from datetime import datetime
import heapq
import json

# --- Model and NLP Setup ---
model=SentenceTransformer("/app/cache/sentence_transformers/multi-qa-MiniLM-L6-cos-v1")

nlp = English()
nlp.add_pipe("sentencizer")
bullet_regex = re.compile(r"^[\u2022\u2023\u25AA\u25CF\u25CB\u25A0\u25B6\u2043\u2219\u204C\u204D\u25E6\uf0b7*\-\•]+[\s]*")

# --- Text Encoding ---
def encode_text(text: str):
    return model.encode(text, convert_to_tensor=True)

# --- Clean Text with SpaCy ---
def clean_text(text: str) -> str:
    doc = nlp(text)
    cleaned = []
    for sent in doc.sents:
        line = bullet_regex.sub("", sent.text.strip())
        tokens = [token.text for token in nlp(line) if not token.is_stop and not token.is_punct]
        cleaned_sent = " ".join(tokens)
        if cleaned_sent:
            cleaned.append(cleaned_sent)
    return "\n".join(cleaned)

# --- Dummy Process Function (Replace with real one from Round 1A) ---
def process(pdf_path):
    return process(pdf_path)

# --- Main Function to Generate Final Output JSON ---
def generate_output(input_dir: str, persona: str, job: str, output_path: str):
    query = job
    embed_query = encode_text(f"{query} {persona}")

    doc_names = [doc for doc in os.listdir(input_dir) if doc.endswith(".pdf")]
    top_sections = []
    subsection_analysis = []

    for doc in doc_names:
        doc_path = os.path.join(input_dir, doc)
        sections = process(doc_path)
        best_score = float('-inf')
        best_section = None

        for section in sections:
            try:
                section_text = section["text"]
                page_num = section["page"]
                score = util.pytorch_cos_sim(embed_query, encode_text(section_text)).item()
                if score > best_score:
                    best_section = {
                        "document": doc,
                        "section_title": section_text,
                        "importance_rank": 0,  # Temporary placeholder
                        "page_number": page_num,
                        "score": score
                    }
            except:
                continue

        if best_section:
            top_sections.append(best_section)

    # Rank by score
    top_sections = sorted(top_sections, key=lambda x: x["score"], reverse=True)
    for idx, sec in enumerate(top_sections):
        sec["importance_rank"] = idx + 1
        del sec["score"]  # Remove raw score from final output

    # Extract Subsections
    for sec in top_sections:
        doc_path = os.path.join(input_dir, sec["document"])
        doc = fitz.open(doc_path)
        page = doc.load_page(sec["page_number"])
        rects = page.search_for(sec["section_title"])
        heading_rect = rects[0] if rects else fitz.Rect(0, 0, page.rect.width, page.rect.height * 0.15)
        below_rect = fitz.Rect(0, heading_rect.y1 + 5, page.rect.width, page.rect.height)
        raw_text = page.get_textbox(below_rect).strip()
        if raw_text:
            cleaned = clean_text(raw_text)
            subsection_analysis.append({
                "document": sec["document"],
                "refined_text": cleaned,
                "page_number": sec["page_number"]
            })

    metadata = {
        "input_documents": doc_names,
        "persona": persona,
        "job_to_be_done": job,
        "processing_timestamp": datetime.now().isoformat()
    }

    final_output = {
        "metadata": metadata,
        "extracted_sections": top_sections,
        "subsection_analysis": subsection_analysis
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(final_output, f, indent=4)

# Example Usage
if __name__ == "__main__":
    generate_output(
        input_dir="/kaggle/input/collection1",
        persona="Travel Planner",
        job="Plan a trip of 4 days for a group of 10 college friends.",
        output_path="/kaggle/working/output.json"
    )
