"""
Main API Application
FastAPI application for ATS Resume Analyzer
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from pathlib import Path
import sys
import os
import logging

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from nlp.resume_parser import ResumeParser
from nlp.language_handler import LanguageHandler
from nlp.skill_extractor import SkillExtractor
from scoring.ats_score import ATSScoreCalculator
from scoring.similarity import SimilarityCalculator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="ATS Resume Analyzer",
    description="AI-powered recruitment insights and candidate analysis",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get absolute paths
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "app" / "static"
TEMPLATES_DIR = BASE_DIR / "app" / "templates"
DATA_DIR = BASE_DIR / "data"

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Initialize components
parser = ResumeParser()
language_handler = LanguageHandler()
skill_extractor = SkillExtractor(str(DATA_DIR / "skills.csv"))
ats_calculator = ATSScoreCalculator()
similarity_calculator = SimilarityCalculator()

# Demo data for demo mode
demo_data = {
    "total_resumes": 0,
    "analyzed_candidates": 0,
    "avg_match_score": 0,
    "avg_processing_time": 0
}


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Render main dashboard"""
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "demo_mode": True}
    )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "components": {
            "parser": "ready",
            "skill_extractor": "ready",
            "ats_calculator": "ready"
        }
    }


@app.post("/api/analyze-resume")
async def analyze_resume(
    file: UploadFile = File(...),
    job_description: str = Form(None),
    required_skills: str = Form(None)
):
    """
    Analyze uploaded resume
    
    Args:
        file: Resume file (PDF, DOCX, TXT)
        job_description: Optional job description for matching
        required_skills: Comma-separated list of required skills
    
    Returns:
        Complete analysis results
    """
    try:
        logger.info(f"Analyzing resume: {file.filename}")
        
        # Read file content
        content = await file.read()
        
        # Parse resume
        resume_text = parser.parse_bytes(content, file.filename)
        
        if not resume_text:
            raise HTTPException(status_code=400, detail="Could not extract text from resume")
        
        # Detect language
        language = language_handler.detect_language(resume_text)
        
        # Extract contact info
        contact_info = language_handler.extract_contact_info(resume_text)
        
        # Extract sections
        sections = language_handler.extract_sections(resume_text, language)
        
        # Extract structured data
        structured_data = parser.extract_structured_data(resume_text)
        
        # Extract skills
        extracted_skills = skill_extractor.extract_skills(resume_text)
        
        # Categorize skills
        categorized_skills = skill_extractor.categorize_skills(extracted_skills)
        
        # Get skill statistics
        skill_stats = skill_extractor.get_skill_statistics(extracted_skills)
        
        # Calculate ATS score
        required_keywords = required_skills.split(',') if required_skills else []
        required_keywords = [k.strip() for k in required_keywords if k.strip()]
        
        ats_result = ats_calculator.calculate_score(
            resume_text,
            extracted_skills,
            required_keywords if required_keywords else None,
            sections
        )
        
        # Calculate job match if job description provided
        job_match = None
        if job_description:
            resume_skill_names = [skill['skill'] for skill in extracted_skills]
            job_match = similarity_calculator.calculate_job_match_score(
                resume_text,
                job_description,
                resume_skill_names,
                required_keywords if required_keywords else []
            )
        
        # Prepare response
        response = {
            "success": True,
            "filename": file.filename,
            "language": language,
            "contact_info": contact_info,
            "structured_data": structured_data,
            "skills": {
                "extracted": extracted_skills,
                "categorized": categorized_skills,
                "statistics": skill_stats
            },
            "ats_score": {
                "overall_score": round(ats_result.overall_score, 2),
                "grade": ats_calculator.get_grade(ats_result.overall_score),
                "section_scores": {
                    k: round(v, 2) for k, v in ats_result.section_scores.items()
                },
                "strengths": ats_result.strengths,
                "weaknesses": ats_result.weaknesses,
                "recommendations": ats_result.recommendations,
                "keyword_matches": ats_result.keyword_matches,
                "keyword_total": ats_result.keyword_total
            }
        }
        
        if job_match:
            response["job_match"] = {
                "overall_score": round(job_match['overall_score'], 2),
                "match_level": job_match['match_level'],
                "skill_match_percentage": round(job_match['skill_match']['match_percentage'], 2),
                "matched_skills": job_match['skill_match']['matched_skills'],
                "missing_skills": job_match['skill_match']['missing_skills'],
                "recommendations": job_match['recommendations']
            }
        
        logger.info(f"Analysis complete. ATS Score: {ats_result.overall_score:.2f}")
        
        return JSONResponse(content=response)
    
    except Exception as e:
        logger.error(f"Error analyzing resume: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/skills")
async def get_skills():
    """Get list of all skills in database"""
    try:
        skills = []
        for skill, metadata in skill_extractor.skills_data.items():
            skills.append({
                "skill": metadata['original'],
                "category": metadata['category'],
                "weight": metadata['weight']
            })
        
        return {
            "success": True,
            "count": len(skills),
            "skills": skills
        }
    
    except Exception as e:
        logger.error(f"Error fetching skills: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/skills/categories")
async def get_skill_categories():
    """Get skill categories"""
    try:
        categories = {}
        for category, skills in skill_extractor.skill_categories.items():
            categories[category] = len(skills)
        
        return {
            "success": True,
            "categories": categories
        }
    
    except Exception as e:
        logger.error(f"Error fetching categories: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/demo/stats")
async def get_demo_stats():
    """Get demo statistics for dashboard"""
    return {
        "success": True,
        "stats": demo_data,
        "demo_mode": True
    }


@app.post("/api/compare-candidates")
async def compare_candidates(
    files: list[UploadFile] = File(...),
    job_description: str = Form(...),
    required_skills: str = Form(...)
):
    """
    Compare multiple candidates for a position
    
    Args:
        files: List of resume files
        job_description: Job description
        required_skills: Comma-separated required skills
    
    Returns:
        Ranked list of candidates
    """
    try:
        logger.info(f"Comparing {len(files)} candidates")
        
        required_skills_list = [s.strip() for s in required_skills.split(',') if s.strip()]
        
        candidates = []
        
        for file in files:
            content = await file.read()
            resume_text = parser.parse_bytes(content, file.filename)
            
            if not resume_text:
                continue
            
            # Extract skills
            extracted_skills = skill_extractor.extract_skills(resume_text)
            skill_names = [skill['skill'] for skill in extracted_skills]
            
            candidates.append({
                'filename': file.filename,
                'resume_text': resume_text,
                'skills': skill_names
            })
        
        # Rank candidates
        ranked_candidates = similarity_calculator.rank_candidates(
            candidates,
            job_description,
            required_skills_list
        )
        

        
        return JSONResponse(content=response)
    
    except Exception as e:
        logger.error(f"Error comparing candidates: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)