import io
import re
from pdfminer.high_level import extract_text as extract_pdf
from docx import Document
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# ------------------- Extract Text from Resume -------------------
def extract_text(content, filename):
    if filename.endswith(".pdf"):
        return extract_pdf(io.BytesIO(content))
    elif filename.endswith(".docx"):
        doc = Document(io.BytesIO(content))
        return "\n".join([p.text for p in doc.paragraphs])
    return ""

# ------------------- Check if Section Exists -------------------
def section_exists(text, section_name):
    return re.search(rf"\b{section_name}\b", text, re.IGNORECASE) is not None

# ------------------- NLP Keyword Extraction -------------------
def extract_keywords(text):
    doc = nlp(text.lower())
    return set(
        token.lemma_ for token in doc
        if token.pos_ in ["NOUN", "PROPN", "ADJ", "VERB"] and not token.is_stop
    )

# ------------------- TF-IDF Similarity Score -------------------
def score_tfidf(resume_text, job_description):
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf = vectorizer.fit_transform([job_description, resume_text])
    score = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
    return round(score * 100, 2)

# ------------------- Keyword Match Score -------------------
def keyword_match_score(resume_tokens, jd_tokens):
    if not jd_tokens:
        return 0.0
    common = resume_tokens.intersection(jd_tokens)
    return round(len(common) / len(jd_tokens) * 100, 2)

# ------------------- Top Skills Extraction -------------------
stopwords = {
    "and", "software", "management", "skill", "soft skill",
    "education", "and software", "database", "coursework"
}

def extract_skills(text):
    sections = ["Languages", "Frameworks And Technologies", "Coursework", "Soft Skill", "Database"]
    skill_list = []
    for section in sections:
        match = re.search(rf"{section}\s*[\n:]*([\s\S]*?)(?=(\n[A-Z][^\n]*\n)|$)", text, re.IGNORECASE)
        if match:
            content = match.group(1)
            skills = re.split(r"[,\n•\|\-]+", content)
            skills = [s.strip() for s in skills if 2 < len(s.strip()) < 50]
            skill_list.extend(skills)
    return sorted(set(s for s in skill_list if s.lower() not in stopwords))

# ------------------- Work Experience Extraction (Multiline-Aware) -------------------
def extract_experience(text):
    lines = text.splitlines()
    experience_entries = []
    current_title = ""

    for i, line in enumerate(lines):
        if re.search(r"(?i)(intern|developer|engineer|designer|analyst)", line):
            current_title = line.strip()
            for j in range(i + 1, min(i + 3, len(lines))):
                if re.search(r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}", lines[j], re.IGNORECASE):
                    date = lines[j].strip()
                    experience_entries.append(f"{current_title} ({date})")
                    break

    return experience_entries

# ------------------- Education Extraction -------------------
def extract_education(text):
    education = re.findall(r"(bachelor|master|bca|mca|b\.sc|m\.sc|btech|mtech|mba|commerce)", text, re.I)
    return sorted(set(e.lower().strip() for e in education if e.strip().lower() != "education"))

# ------------------- Main Resume Analyzer -------------------
def analyze_resume(content, filename, job_description=""):
    # 1. Extract resume content
    text = extract_text(content, filename)
    summary = text[:500] + "..." if len(text) > 500 else text
    length = len(text)

    # 2. Field Extraction
    education = extract_education(text)
    experience = extract_experience(text)
    skills = extract_skills(text)

    # 3. Keyword Processing
    resume_tokens = extract_keywords(text)
    jd_tokens = extract_keywords(job_description)

    # 4. Section Scoring
    section_score = 0
    for section in ["Skills", "Education", "Projects", "Experience"]:
        if section_exists(text, section):
            section_score += 5

    # 5. Score Calculation
    tfidf_score = score_tfidf(text, job_description) if job_description else 0.0
    keyword_score = keyword_match_score(resume_tokens, jd_tokens)
    edu_match = bool(education)
    exp_match = bool(experience)

    ats_score = round(
        0.4 * keyword_score +
        0.2 * tfidf_score +
        0.2 * (100 if edu_match else 0) +
        0.2 * (100 if exp_match else 0), 2
    )

    # 6. Final Output
    return {
        "summary": summary,
        "length": length,
        "education": education,
        "experience": experience,
        "skills": skills,
        "score": tfidf_score,
        "keyword_match_score": keyword_score,
        "section_bonus": section_score,
        "ats_score": ats_score,
        "text": text,
    }
