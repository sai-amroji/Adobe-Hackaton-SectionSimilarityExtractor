**Approach Explanation: Round 1B - Persona-Driven Document Intelligence**

---

### Problem Overview

The task involves analyzing a diverse collection of PDFs and extracting the most relevant sections and sub-sections based on a given persona and their job-to-be-done. This simulates a real-world use case where an AI assistant should mimic how a domain expert would prioritize information.

### Key Objectives

* Extract top-level sections relevant to the persona and task.
* Perform sub-section level analysis to surface the most important supporting information.
* Output a structured JSON capturing the document intelligence.

### Step-by-Step Methodology

#### 1. **Model and NLP Setup**

* We use the `BAAI/bge-small-en-v1.5` SentenceTransformer, which is lightweight (<200MB), fast, and provides robust semantic embeddings for English content.
* For sentence segmentation and stopword removal, we utilize `spaCy` with an `English` pipeline and add a `sentencizer` component.

#### 2. **Document Preprocessing**

* All PDFs are parsed using `PyMuPDF` (fitz) to extract plain text.
* We simulate structural heading detection using heuristics like sentence case, length, and font size (if necessary), representing basic document structure.

#### 3. **Section-Level Ranking**

* A query embedding is created by combining the persona role and job-to-be-done.
* All detected headings/sections from each document are encoded and compared with the query using cosine similarity.
* The top 5–7 sections across all documents are selected and ranked based on similarity.

#### 4. **Sub-Section Analysis**

* For each top-ranked section, the text beneath the heading on the same page is extracted.
* If the exact heading is not found, a fallback mechanism targets the top portion of the page.
* This extracted content is cleaned using `spaCy` to remove bullet markers, stopwords, and irrelevant symbols.
* Each section's text is scored again for relevance and included in the final `subsection_analysis`.

#### 5. **Final Output Structuring**

* A JSON file is created with:

  * `metadata`: Documents, persona, task, timestamp.
  * `extracted_sections`: Top sections with importance rank and page number.
  * `subsection_analysis`: Refined, cleaned text content tied to the section.

### Performance Considerations

* The solution adheres strictly to the constraints: no internet calls, CPU-only, and model size <1GB.
* Execution time for 3–5 documents is well within the 60-second cap.

### Generalizability

* The approach does not rely on fixed file structures or domains, making it flexible for research papers, reports, guidebooks, etc.
* Section extraction logic can be replaced with a more advanced model (e.g., layout-based) in Round 2 without changing the core logic.

### Limitations & Future Improvements

* Current section detection is based on heuristics; introducing OCR-based layout understanding or leveraging Round 1A output would enhance accuracy.
* Multilingual support can be added using a multilingual model like `LaBSE` or `bge-m3`.

### Conclusion

This modular and performant system bridges unstructured PDFs and persona-driven tasks. It surfaces meaningful content that enables intelligent reading, planning, or decision-making for any user role.
