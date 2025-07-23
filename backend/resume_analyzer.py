# backend/resume_analyzer.py
import io
from pdfminer.high_level import extract_text as extract_pdf
from docx import Document
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

nlp = spacy.load("en_core_web_sm")

def extract_text(content, filename):
    if filename.endswith(".pdf"):
        return extract_pdf(io.BytesIO(content))
    elif filename.endswith(".docx"):
        doc = Document(io.BytesIO(content))
        return "\n".join([p.text for p in doc.paragraphs])
    return ""

def score_resume(resume_text, job_description):
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform([job_description, resume_text])
    score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    return round(score * 100, 2)

def analyze_resume(content, filename, job_description=""):
    text = extract_text(content, filename)
    doc = nlp(text)

    skills = [ent.text for ent in doc.ents if ent.label_ == "SKILL"]
    summary = text[:500] + "..." if len(text) > 500 else text
    score = score_resume(text, job_description) if job_description else None

    return {
        "summary": summary,
        "skills": list(set(skills)),
        "length": len(text),
        "text": text,
        "score": score,
    }
