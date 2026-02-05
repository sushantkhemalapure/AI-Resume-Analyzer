"""
API Routes for ATS Resume Analyzer
Organized endpoint definitions
"""

from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

# Create API router
router = APIRouter(prefix="/api", tags=["api"])


def setup_routes(
    parser,
    language_handler,
    skill_extractor,
    ats_calculator,
    similarity_calculator
):
    """
    Setup API routes with dependency injection
    
    Args:
        parser: ResumeParser instance
        language_handler: LanguageHandler instance
        skill_extractor: SkillExtractor instance
        ats_calculator: ATSScoreCalculator instance
        similarity_calculator: SimilarityCalculator instance
    """
    
    @router.post("/analyze-resume")
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
    
    
    @router.get("/skills")
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
    
    
    @router.get("/skills/categories")
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
    
    
    @router.get("/demo/stats")
    async def get_demo_stats():
        """Get demo statistics for dashboard"""
        demo_data = {
            "total_resumes": 0,
            "analyzed_candidates": 0,
            "avg_match_score": 0,
            "avg_processing_time": 0
        }
        return {
            "success": True,
            "stats": demo_data,
            "demo_mode": True
        }
    
    
    @router.post("/compare-candidates")
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
            
            # Prepare response
            response = {
                "success": True,
                "total_candidates": len(ranked_candidates),
                "candidates": [
                    {
                        "filename": c['filename'],
                        "match_score": round(c['match_score'], 2),
                        "match_level": c['match_level'],
                        "skills": c['skills'][:10]  # Top 10 skills
                    }
                    for c in ranked_candidates
                ]
            }
            
            return JSONResponse(content=response)
        
        except Exception as e:
            logger.error(f"Error comparing candidates: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    
    @router.post("/batch-analyze")
    async def batch_analyze(
        files: list[UploadFile] = File(...),
        required_skills: str = Form(None)
    ):
        """
        Batch analyze multiple resumes
        
        Args:
            files: List of resume files
            required_skills: Comma-separated required skills
        
        Returns:
            Analysis results for all resumes
        """
        try:
            logger.info(f"Batch analyzing {len(files)} resumes")
            
            required_keywords = []
            if required_skills:
                required_keywords = [s.strip() for s in required_skills.split(',') if s.strip()]
            
            results = []
            
            for file in files:
                try:
                    content = await file.read()
                    resume_text = parser.parse_bytes(content, file.filename)
                    
                    if not resume_text:
                        results.append({
                            "filename": file.filename,
                            "success": False,
                            "error": "Could not extract text"
                        })
                        continue
                    
                    # Extract skills
                    extracted_skills = skill_extractor.extract_skills(resume_text)
                    
                    # Extract sections
                    language = language_handler.detect_language(resume_text)
                    sections = language_handler.extract_sections(resume_text, language)
                    
                    # Calculate ATS score
                    ats_result = ats_calculator.calculate_score(
                        resume_text,
                        extracted_skills,
                        required_keywords if required_keywords else None,
                        sections
                    )
                    
                    results.append({
                        "filename": file.filename,
                        "success": True,
                        "ats_score": round(ats_result.overall_score, 2),
                        "grade": ats_calculator.get_grade(ats_result.overall_score),
                        "skills_count": len(extracted_skills)
                    })
                
                except Exception as e:
                    results.append({
                        "filename": file.filename,
                        "success": False,
                        "error": str(e)
                    })
            
            return {
                "success": True,
                "total_files": len(files),
                "processed": len([r for r in results if r.get('success')]),
                "failed": len([r for r in results if not r.get('success')]),
                "results": results
            }
        
        except Exception as e:
            logger.error(f"Error in batch analysis: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    
    return router