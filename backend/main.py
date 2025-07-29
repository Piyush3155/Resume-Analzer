from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from resume_analyzer import analyze_resume

app = FastAPI(
    title="Resume Analyzer API",
    description="Analyze resumes and return ATS score, skills, education, experience, and more.",
    version="1.0.0"
)

# Enable CORS for frontend (Next.js) communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with specific domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze")
async def analyze(
    file: UploadFile = File(...),
    job_description: str = Form("")
):
    """
    Accepts a resume file and optional job description, returns ATS analysis.
    """
    contents = await file.read()
    result = analyze_resume(contents, file.filename, job_description)
    
    # Optional: exclude full text to reduce payload
    result.pop("text", None)
    
    return result
