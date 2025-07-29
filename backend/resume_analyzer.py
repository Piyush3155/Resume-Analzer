# backend/resume_analyzer.py
import io
import re
from pdfminer.high_level import extract_text as extract_pdf
from docx import Document
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter

nlp = spacy.load("en_core_web_sm")

def extract_text(content, filename):
    if filename.endswith(".pdf"):
        return extract_pdf(io.BytesIO(content))
    elif filename.endswith(".docx"):
        doc = Document(io.BytesIO(content))
        return "\n".join([p.text for p in doc.paragraphs])
    return ""

def clean_and_tokenize(text):
    doc = nlp(text.lower())
    tokens = [token.lemma_ for token in doc if token.is_alpha and not token.is_stop]
    return tokens

def get_keywords(text):
    tokens = clean_and_tokenize(text)
    return set(tokens)

def section_exists(text, section_name):
    return re.search(rf"\b{section_name}\b", text, re.IGNORECASE) is not None

def keyword_match_score(resume_tokens, jd_tokens):
    common = set(resume_tokens).intersection(jd_tokens)
    return round(len(common) / len(jd_tokens) * 100, 2) if jd_tokens else 0.0

def score_resume_tfidf(resume_text, job_description):
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform([job_description, resume_text])
    score = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    return round(score * 100, 2)

def analyze_resume(content, filename, job_description=""):
    text = extract_text(content, filename)
    doc = nlp(text)

    # Extract entities labeled as skills or similar
    entities = [ent.text for ent in doc.ents if ent.label_ in ["SKILL", "ORG", "WORK_OF_ART", "PRODUCT", "PERSON"]]

    summary = text[:500] + "..." if len(text) > 500 else text
    resume_tokens = clean_and_tokenize(text)
    jd_tokens = clean_and_tokenize(job_description) if job_description else []

    # Scores
    tfidf_score = score_resume_tfidf(text, job_description) if job_description else None
    keyword_score = keyword_match_score(resume_tokens, jd_tokens) if job_description else None

    # Bonus if important sections exist
    section_score = 0
    for section in ["Skills", "Experience", "Education"]:
        if section_exists(text, section):
            section_score += 5

    # Weighted ATS score
    if job_description:
        ats_score = round(0.5 * keyword_score + 0.4 * tfidf_score + section_score, 2)
    else:
        ats_score = None

    return {
        "summary": summary,
        "skills": list(set(entities)),
        "length": len(text),
        "text": text,
        "score": ats_score,
        "tfidf_score": tfidf_score,
        "keyword_match_score": keyword_score,
        "section_bonus": section_score
    }
