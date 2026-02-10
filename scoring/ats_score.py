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
    
    def _score_formatting(self, text: str) -> Tuple[float, List[str]]:
        """
        Score resume formatting and structure
        
        Returns:
            Tuple of (score, recommendations)
        """
        score = 100.0
        recommendations = []
        
        # Check length (ideal: 1-2 pages = 500-2000 words)
        word_count = len(text.split())
        if word_count < 300:
            score -= 20
            recommendations.append("Resume is too short. Add more details about your experience.")
        elif word_count > 3000:
            score -= 15
            recommendations.append("Resume is too long. Keep it concise (1-2 pages ideal).")
        
        # Check for special characters that confuse ATS
        problematic_chars = ['•', '★', '◆', '▪', '►']
        if any(char in text for char in problematic_chars):
            score -= 10
            recommendations.append("Replace special bullet characters with standard hyphens or asterisks.")
        
        # Check for tables (ATS often struggles with tables)
        if '\t' in text or '|' in text:
            score -= 10
            recommendations.append("Avoid using tables. Use simple text formatting instead.")
        
        # Check for contact information
        has_email = bool(re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text))
        has_phone = bool(re.search(r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}', text))
        
        if not has_email:
            score -= 15
            recommendations.append("Add a professional email address.")
        if not has_phone:
            score -= 10
            recommendations.append("Include a phone number.")
        
        # Check for section headers
        common_headers = ['experience', 'education', 'skills', 'summary']
        headers_found = sum(1 for header in common_headers if header in text.lower())
        
        if headers_found < 3:
            score -= 15
            recommendations.append("Use clear section headers (Experience, Education, Skills, etc.).")
        
        return max(0, score), recommendations
    
    def _score_keywords(self, text: str, keywords: List[str]) -> Tuple[float, int, List[str]]:
        """
        Score keyword presence and density
        
        Returns:
            Tuple of (score, matches_count, recommendations)
        """
        text_lower = text.lower()
        matches = 0
        missing_keywords = []
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            if keyword_lower in text_lower:
                matches += 1
            else:
                missing_keywords.append(keyword)
        
        # Calculate score based on match percentage
        match_percentage = (matches / len(keywords)) * 100 if keywords else 0
        score = match_percentage
        
        recommendations = []
        if match_percentage < 70:
            recommendations.append(
                f"Include these important keywords: {', '.join(missing_keywords[:5])}"
            )
        
        # Check keyword density (should appear naturally, not stuffed)
        total_words = len(text.split())
        keyword_density = (matches / total_words) * 100 if total_words > 0 else 0
        
        if keyword_density > 5:
            score -= 10
            recommendations.append("Keyword density is too high. Use keywords naturally.")
        
        return score, matches, recommendations
    
    def _score_experience(self, text: str, sections: Dict[str, str] = None) -> Tuple[float, List[str]]:
        """
        Score work experience section
        
        Returns:
            Tuple of (score, recommendations)
        """
        score = 100.0
        recommendations = []
        
        text_lower = text.lower()
        
        # Check if experience section exists
        has_experience = any(
            keyword in text_lower 
            for keyword in ['experience', 'employment', 'work history']
        )
        
        if not has_experience:
            score -= 50
            recommendations.append("Add a Work Experience or Employment History section.")
            return max(0, score), recommendations
        
        # Check for dates
        date_patterns = [
            r'\d{4}\s*[-–]\s*\d{4}',  # 2020-2023
            r'\d{4}\s*[-–]\s*present',  # 2020-Present
            r'\w+\s+\d{4}\s*[-–]\s*\w+\s+\d{4}',  # Jan 2020 - Dec 2023
        ]
        
        has_dates = any(re.search(pattern, text, re.IGNORECASE) for pattern in date_patterns)
        if not has_dates:
            score -= 20
            recommendations.append("Include dates (start and end) for each position.")
        
        # Check for action verbs
        action_verbs = [
            'developed', 'created', 'managed', 'led', 'implemented',
            'designed', 'built', 'improved', 'achieved', 'established'
        ]
        
        action_verb_count = sum(1 for verb in action_verbs if verb in text_lower)
        if action_verb_count < 5:
            score -= 15
            recommendations.append(
                "Use strong action verbs (e.g., developed, managed, implemented)."
            )
        
        # Check for quantifiable achievements
        has_numbers = bool(re.search(r'\d+%|\$\d+|\d+\+', text))
        if not has_numbers:
            score -= 15
            recommendations.append(
                "Add quantifiable achievements (e.g., 'Increased sales by 30%')."
            )
        
        return max(0, score), recommendations
    
    def _score_education(self, text: str, sections: Dict[str, str] = None) -> Tuple[float, List[str]]:
        """
        Score education section
        
        Returns:
            Tuple of (score, recommendations)
        """
        score = 100.0
        recommendations = []
        
        text_lower = text.lower()
        
        # Check if education section exists
        has_education = 'education' in text_lower
        
        if not has_education:
            score -= 40
            recommendations.append("Add an Education section with your degrees.")
            return max(0, score), recommendations
        
        # Check for degree
        degree_keywords = [
            'bachelor', 'master', 'phd', 'doctorate', 'b.s.', 'm.s.',
            'b.a.', 'm.a.', 'mba', 'degree'
        ]
        
        has_degree = any(keyword in text_lower for keyword in degree_keywords)
        if not has_degree:
            score -= 30
            recommendations.append("Specify your degree (e.g., Bachelor of Science).")
        
        # Check for graduation year
        has_year = bool(re.search(r'\b(19|20)\d{2}\b', text))
        if not has_year:
            score -= 20
            recommendations.append("Include graduation year or expected graduation date.")
        
        # Check for GPA (optional but good to have if strong)
        has_gpa = bool(re.search(r'gpa|grade point average', text_lower))
        if not has_gpa:
            recommendations.append(
                "Consider adding GPA if it's 3.5 or higher (optional)."
            )
        
        return max(0, score), recommendations
    
    def _score_skills(self, extracted_skills: List[Dict]) -> Tuple[float, List[str]]:
        """
        Score skills section
        
        Returns:
            Tuple of (score, recommendations)
        """
        score = 100.0
        recommendations = []
        
        skill_count = len(extracted_skills)
        

    



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