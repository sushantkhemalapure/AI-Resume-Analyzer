"""
ATS Score Module
Calculates Applicant Tracking System (ATS) compatibility scores
"""

import re
import logging
from typing import Dict, List, Tuple
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ATSScoreResult:
    """Data class for ATS score results"""
    overall_score: float
    section_scores: Dict[str, float]
    recommendations: List[str]
    strengths: List[str]
    weaknesses: List[str]
    keyword_matches: int
    keyword_total: int


class ATSScoreCalculator:
    """Calculate ATS compatibility scores for resumes"""
    
    # Scoring weights for different components
    WEIGHTS = {
        'formatting': 0.15,
        'keywords': 0.30,
        'experience': 0.20,
        'education': 0.15,
        'skills': 0.20
    }
    
    # Required sections
    REQUIRED_SECTIONS = [
        'experience', 'education', 'skills'
    ]
    
    # Recommended sections
    RECOMMENDED_SECTIONS = [
        'summary', 'certifications', 'projects'
    ]
    
    def __init__(self):
        self.score_breakdown = {}
    
    def calculate_score(self, 
                       resume_text: str,
                       extracted_skills: List[Dict],
                       required_keywords: List[str] = None,
                       sections: Dict[str, str] = None) -> ATSScoreResult:
        """
        Calculate overall ATS score
        
        Args:
            resume_text: Full resume text
            extracted_skills: List of skills found in resume
            required_keywords: Keywords required for job (optional)
            sections: Dictionary of extracted sections (optional)
            
        Returns:
            ATSScoreResult object with detailed scoring
        """
        scores = {}
        recommendations = []
        strengths = []
        weaknesses = []
        
        # 1. Formatting Score
        format_score, format_recs = self._score_formatting(resume_text)
        scores['formatting'] = format_score
        recommendations.extend(format_recs)
        
        # 2. Keywords Score
        if required_keywords:
            keyword_score, keyword_matches, keyword_recs = self._score_keywords(
                resume_text, required_keywords
            )
            scores['keywords'] = keyword_score
            recommendations.extend(keyword_recs)
        else:
            keyword_score = 0.0
            keyword_matches = 0
        
        # 3. Experience Score
        exp_score, exp_recs = self._score_experience(resume_text, sections)
        scores['experience'] = exp_score
        recommendations.extend(exp_recs)
        
        # 4. Education Score
        edu_score, edu_recs = self._score_education(resume_text, sections)
        scores['education'] = edu_score
        recommendations.extend(edu_recs)
        
        # 5. Skills Score
        skills_score, skills_recs = self._score_skills(extracted_skills)
        scores['skills'] = skills_score
        recommendations.extend(skills_recs)
        
        # Calculate weighted overall score
        overall_score = sum(
            scores[component] * self.WEIGHTS[component]
            for component in self.WEIGHTS.keys()
        )
        
        # Identify strengths and weaknesses
        for component, score in scores.items():
            if score >= 80:
                strengths.append(f"{component.title()}: Excellent")
            elif score < 60:
                weaknesses.append(f"{component.title()}: Needs improvement")
        
        logger.info(f"Calculated ATS score: {overall_score:.2f}/100")
        
        return ATSScoreResult(
            overall_score=overall_score,
            section_scores=scores,
            recommendations=recommendations,
            strengths=strengths,
            weaknesses=weaknesses,
            keyword_matches=keyword_matches,
            keyword_total=len(required_keywords) if required_keywords else 0
        )
    

    

    

    

        

    



def test_ats_calculator():
    """Test the ATS score calculator"""
    calculator = ATSScoreCalculator()
    
    sample_resume = """
    John Doe
    john.doe@email.com | 555-123-4567
    
    PROFESSIONAL SUMMARY
    Senior Software Engineer with 5+ years of experience
    
    WORK EXPERIENCE
    Senior Software Engineer, Tech Corp (2020-Present)
    - Developed scalable applications using Python and React
    - Increased system performance by 40%
    - Led team of 5 engineers
    
    Software Engineer, StartUp Inc (2018-2020)
    - Built RESTful APIs with Node.js
    - Implemented CI/CD pipelines
    
    EDUCATION
    M.S. in Computer Science, Stanford University, 2018
    B.S. in Computer Science, MIT, 2016, GPA: 3.8
    
    SKILLS
    Python, JavaScript, React, Node.js, AWS, Docker, Kubernetes
    """
    
    sample_skills = [
        {'skill': 'Python', 'category': 'Programming Languages', 'weight': 0.9},
        {'skill': 'JavaScript', 'category': 'Programming Languages', 'weight': 0.85},
        {'skill': 'React', 'category': 'Web Development', 'weight': 0.9},
        {'skill': 'Node.js', 'category': 'Web Development', 'weight': 0.9},
        {'skill': 'AWS', 'category': 'Cloud & DevOps', 'weight': 0.95},
        {'skill': 'Docker', 'category': 'Cloud & DevOps', 'weight': 0.9},
    ]
    
    required_keywords = [
        'Python', 'JavaScript', 'React', 'AWS', 'Docker',
        'API', 'team', 'leadership'
    ]
    
    result = calculator.calculate_score(
        sample_resume,
        sample_skills,
        required_keywords
    )
    
    print(f"\n=== ATS Score Report ===")
    print(f"Overall Score: {result.overall_score:.2f}/100 ({calculator.get_grade(result.overall_score)})")
    print(f"\nSection Scores:")
    for section, score in result.section_scores.items():
        print(f"  {section.title()}: {score:.2f}/100")
    
    print(f"\nKeyword Matches: {result.keyword_matches}/{result.keyword_total}")
    
    print(f"\nStrengths:")
    for strength in result.strengths:
        print(f"  ✓ {strength}")
    
    print(f"\nWeaknesses:")
    for weakness in result.weaknesses:
        print(f"  ✗ {weakness}")
    
    print(f"\nRecommendations:")
    for i, rec in enumerate(result.recommendations[:5], 1):
        print(f"  {i}. {rec}")


if __name__ == "__main__":
    test_ats_calculator()