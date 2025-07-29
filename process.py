# process_pdf_round1a.py
# Round 1A - Structured Outline Extractor

import pymupdf  # PyMuPDF
import numpy as np
import re
from collections import defaultdict, Counter
import json
from pathlib import Path

# -------------------- Helper Functions ----------------------
def interpret_flags(flags):
    return {"bold": bool(flags & 2)}

def get_alignment(bbox, usable_left, usable_right, tolerance=0.05):
    x0, _, x1, _ = bbox
    center_pos = (x0 + x1) / 2
    text_center = (usable_left + usable_right) / 2
    width = usable_right - usable_left

    if abs(center_pos - text_center) < tolerance * width:
        return "center"
    elif abs(x0 - usable_left) < tolerance * width:
        return "left"
    elif abs(x1 - usable_right) < tolerance * width:
        return "right"
    else:
        return "justified"

def is_bullet_line(text):
    return bool(re.match(r"^[\u2022\u2023\u25AA\u25CF\u25CB\u25A0\u25B6\u2043\u2219\u204C\u204D\u25E6\uf0b7\-\*]+", text.strip()))

def extract_title(page):
    spans = []
    for block in page.get_text("dict")["blocks"]:
        if block["type"] != 0:
            continue
        for line in block["lines"]:
            for span in line["spans"]:
                spans.append(span)
    if not spans:
        return "Untitled"
    font_size_counter = Counter(round(s["size"]) for s in spans)
    max_size = max(font_size_counter)
    candidates = [s["text"] for s in spans if round(s["size"]) == max_size]
    return " ".join(candidates).strip() or "Untitled"

def is_heading(text):
    if len(text.strip()) < 3 or len(text.strip()) > 200:
        return False
    if text.strip().endswith('.'):
        return False
    if text.strip().lower() in {"table of contents", "index"}:
        return False
    return text[0].isupper() and not is_bullet_line(text)

def extract_outline(doc):
    lines = []
    for page_num, page in enumerate(doc):
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if block.get("type") != 0:
                continue
            for line in block["lines"]:
                text = " ".join(span["text"].strip() for span in line["spans"] if span["text"])
                if is_heading(text):
                    size = round(line["spans"][0]["size"])
                    lines.append({
                        "text": text,
                        "size": size,
                        "page": page_num
                    })
    sizes = sorted({l["size"] for l in lines}, reverse=True)
    levels = {s: f"H{i+1}" for i, s in enumerate(sizes[:3])}
    outline = [
        {
            "text": l["text"],
            "level": levels.get(l["size"], "H3"),
            "page": l["page"]
        }
        for l in lines if l["size"] in levels
    ]
    return outline

# -------------------- Main Process --------------------------
def process(pdf_path):
    doc = pymupdf.open(pdf_path)
    title = extract_title(doc[0])
    outline = extract_outline(doc)
    return {
        "title": title,
        "outline": outline
    }

def process_pdfs():
    input_dir = Path("Challenge_1a/sample_dataset/pdfs")
    output_dir = Path("Challenge_1a/sample_dataset/outputs")
    output_dir.mkdir(parents=True, exist_ok=True)
    pdf_files = list(input_dir.glob("*.pdf"))

    for pdf_file in pdf_files:
        data = process(pdf_file)
        output_file = output_dir / f"{pdf_file.stem}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Processed {pdf_file.name} -> {output_file.name}")

if __name__ == "__main__":
    process_pdfs()
