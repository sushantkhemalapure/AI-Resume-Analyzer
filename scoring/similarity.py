"""
Similarity Module
Calculates similarity between resumes and job descriptions
"""

import re
import math
import logging
from typing import List, Dict, Tuple, Set
from collections import Counter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimilarityCalculator:
    """Calculate similarity scores between resume and job requirements"""
    
    # Common stop words to ignore
    STOP_WORDS = {
        'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
        'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
        'to', 'was', 'will', 'with', 'the', 'this', 'but', 'they', 'have',
        'had', 'what', 'when', 'where', 'who', 'which', 'why', 'how'
    }
    
    def __init__(self):
        pass
    
    def preprocess_text(self, text: str) -> List[str]:
        """
        Preprocess text for similarity calculation
        
        Args:
            text: Input text
            
        Returns:
            List of cleaned tokens
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        
        # Tokenize
        tokens = text.split()
        
        # Remove stop words and short words
        tokens = [t for t in tokens if t not in self.STOP_WORDS and len(t) > 2]
        
        return tokens
    
    def cosine_similarity(self, vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        """
        Calculate cosine similarity between two vectors
        
        Args:
            vec1: First vector (term frequencies)
            vec2: Second vector (term frequencies)
            
        Returns:
            Cosine similarity score (0-1)
        """
        # Get all unique terms
        all_terms = set(vec1.keys()) | set(vec2.keys())
        
        # Calculate dot product
        dot_product = sum(vec1.get(term, 0) * vec2.get(term, 0) for term in all_terms)
        
        # Calculate magnitudes
        mag1 = math.sqrt(sum(val ** 2 for val in vec1.values()))
        mag2 = math.sqrt(sum(val ** 2 for val in vec2.values()))
        
        # Avoid division by zero
        if mag1 == 0 or mag2 == 0:
            return 0.0
        
        return dot_product / (mag1 * mag2)
    
    def jaccard_similarity(self, set1: Set, set2: Set) -> float:
        """
        Calculate Jaccard similarity between two sets
        
        Args:
            set1: First set
            set2: Second set
            
        Returns:
            Jaccard similarity score (0-1)
        """
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0
    
    def calculate_text_similarity(self, text1: str, text2: str) -> Dict[str, float]:
        """
        Calculate multiple similarity scores between two texts
        
        Args:
            text1: First text (e.g., resume)
            text2: Second text (e.g., job description)
            
        Returns:
            Dictionary with different similarity scores
        """
        # Preprocess texts
        tokens1 = self.preprocess_text(text1)
        tokens2 = self.preprocess_text(text2)
        
        # Create term frequency vectors
        freq1 = Counter(tokens1)
        freq2 = Counter(tokens2)
        
        # Normalize frequencies
        total1 = sum(freq1.values())
        total2 = sum(freq2.values())
        
        vec1 = {term: count / total1 for term, count in freq1.items()}
        vec2 = {term: count / total2 for term, count in freq2.items()}
        
        # Calculate cosine similarity
        cosine_sim = self.cosine_similarity(vec1, vec2)
        
        # Calculate Jaccard similarity
        jaccard_sim = self.jaccard_similarity(set(tokens1), set(tokens2))
        
        # Calculate overlap score (percentage of job terms found in resume)
        job_terms = set(tokens2)
        resume_terms = set(tokens1)
        overlap = len(job_terms & resume_terms) / len(job_terms) if job_terms else 0
        
        return {
            'cosine_similarity': cosine_sim,
            'jaccard_similarity': jaccard_sim,
            'overlap_score': overlap,
            'overall_similarity': (cosine_sim * 0.4 + jaccard_sim * 0.3 + overlap * 0.3)
        }
    
    def calculate_skill_match(self, 
                             resume_skills: List[str],
                             job_skills: List[str]) -> Dict:
        """
        Calculate skill matching score
        
        Args:
            resume_skills: Skills from resume
            job_skills: Required skills from job
            
        Returns:
            Dictionary with skill match details
        """
        resume_skills_set = {skill.lower() for skill in resume_skills}
        job_skills_set = {skill.lower() for skill in job_skills}
        
        matched_skills = resume_skills_set & job_skills_set
        missing_skills = job_skills_set - resume_skills_set
        extra_skills = resume_skills_set - job_skills_set
        
        match_percentage = len(matched_skills) / len(job_skills_set) * 100 if job_skills_set else 0
        
        return {
            'match_percentage': match_percentage,
            'matched_skills': list(matched_skills),
            'missing_skills': list(missing_skills),
            'extra_skills': list(extra_skills),
            'matched_count': len(matched_skills),
            'required_count': len(job_skills_set)
        }
    
    def calculate_experience_match(self,
                                  resume_text: str,
                                  required_years: int = None) -> Dict:
        """
        Calculate experience level match
        
        Args:
            resume_text: Resume text
            required_years: Required years of experience
            
        Returns:
            Dictionary with experience match details
        """
        # Extract years of experience from resume
        experience_patterns = [
            r'(\d+)\+?\s*years?\s+(?:of\s+)?experience',
            r'experience\s+(?:of\s+)?(\d+)\+?\s*years?'
        ]
        
        years_found = []
        for pattern in experience_patterns:
            matches = re.finditer(pattern, resume_text.lower())
            for match in matches:
                years_found.append(int(match.group(1)))
        
        candidate_years = max(years_found) if years_found else 0
        
        result = {
            'candidate_years': candidate_years,
            'required_years': required_years,
            'meets_requirement': False,
            'experience_level': 'Entry Level'
        }
        
        if required_years:
            result['meets_requirement'] = candidate_years >= required_years
        
        # Categorize experience level
        if candidate_years >= 10:
            result['experience_level'] = 'Senior/Expert'
        elif candidate_years >= 5:
            result['experience_level'] = 'Senior'
        elif candidate_years >= 2:
            result['experience_level'] = 'Mid-Level'
        elif candidate_years >= 1:
            result['experience_level'] = 'Junior'
        
        return result
    
    def calculate_job_match_score(self,
                                 resume_text: str,
                                 job_description: str,
                                 resume_skills: List[str],
                                 job_skills: List[str],
                                 required_years: int = None) -> Dict:
        """
        Calculate overall job match score
        
        Args:
            resume_text: Full resume text
            job_description: Job description text
            resume_skills: Skills extracted from resume
            job_skills: Required skills from job
            required_years: Required years of experience
            
        Returns:
            Dictionary with comprehensive match analysis
        """
        # Calculate text similarity
        text_similarity = self.calculate_text_similarity(resume_text, job_description)
        
        # Calculate skill match
        skill_match = self.calculate_skill_match(resume_skills, job_skills)
        
        # Calculate experience match
        experience_match = self.calculate_experience_match(resume_text, required_years)
        
        # Calculate weighted overall score
        weights = {
            'text_similarity': 0.25,
            'skill_match': 0.50,
            'experience_match': 0.25
        }
        
        overall_score = (
            text_similarity['overall_similarity'] * weights['text_similarity'] * 100 +
            skill_match['match_percentage'] * weights['skill_match'] +
            (100 if experience_match['meets_requirement'] else 50) * weights['experience_match']
        )
        
        # Generate match level
        if overall_score >= 80:
            match_level = 'Excellent Match'
        elif overall_score >= 70:
            match_level = 'Good Match'
        elif overall_score >= 60:
            match_level = 'Fair Match'
        else:
            match_level = 'Poor Match'
        
        result = {
            'overall_score': overall_score,
            'match_level': match_level,
            'text_similarity': text_similarity,
            'skill_match': skill_match,
            'experience_match': experience_match,
            'recommendations': self._generate_recommendations(
                skill_match, experience_match, overall_score
            )
        }
        
        logger.info(f"Job match score calculated: {overall_score:.2f}/100 ({match_level})")
        return result
    
    def _generate_recommendations(self,
                                 skill_match: Dict,
                                 experience_match: Dict,
                                 overall_score: float) -> List[str]:
        """
        Generate recommendations to improve job match
        
        Args:
            skill_match: Skill match results
            experience_match: Experience match results
            overall_score: Overall match score
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Skill recommendations
        if skill_match['match_percentage'] < 70:
            missing = skill_match['missing_skills'][:5]
            recommendations.append(
                f"Focus on developing these skills: {', '.join(missing)}"
            )
        
        if skill_match['match_percentage'] < 50:
            recommendations.append(
                "Consider additional training or certifications in required areas."
            )
        
        # Experience recommendations
        if not experience_match['meets_requirement']:
            recommendations.append(
                f"Gain more experience. Target: {experience_match['required_years']} years"
            )
        
        # General recommendations
        if overall_score < 60:
            recommendations.append(
                "This position may not be the best fit. Consider roles matching your skills."
            )
        elif overall_score < 80:
            recommendations.append(
                "Highlight relevant projects and experiences in your application."
            )
        
        if not recommendations:
            recommendations.append("You're a strong match for this position!")
        
        return recommendations
    
    def rank_candidates(self, 
                       candidates: List[Dict],
                       job_description: str,
                       job_skills: List[str]) -> List[Dict]:
        """
        Rank multiple candidates for a job
        
        Args:
            candidates: List of candidate dictionaries with resume_text and skills
            job_description: Job description text
            job_skills: Required job skills
            
        Returns:
            Sorted list of candidates with scores
        """
        scored_candidates = []
        
        for candidate in candidates:
            match_result = self.calculate_job_match_score(
                candidate['resume_text'],
                job_description,
                candidate['skills'],
                job_skills
            )
            
            candidate['match_score'] = match_result['overall_score']
            candidate['match_level'] = match_result['match_level']
            candidate['match_details'] = match_result
            
            scored_candidates.append(candidate)
        
        # Sort by match score (descending)
        scored_candidates.sort(key=lambda x: x['match_score'], reverse=True)
        
        return scored_candidates


def test_similarity_calculator():
    """Test the similarity calculator"""
    calculator = SimilarityCalculator()
    
    resume_text = """
    Senior Software Engineer with 5+ years of experience in Python, Java, and React.
    Built scalable web applications using AWS and Docker.
    Led team of engineers and implemented CI/CD pipelines.
    Strong problem-solving and communication skills.
    """
    
    job_description = """
    We are seeking a Senior Software Engineer with 5+ years of experience.
    Required skills: Python, JavaScript, React, AWS, Docker, Kubernetes.
    Must have experience with microservices and CI/CD.
    Strong leadership and communication skills required.
    """
    
    resume_skills = ['Python', 'Java', 'React', 'AWS', 'Docker', 'CI/CD']
    job_skills = ['Python', 'JavaScript', 'React', 'AWS', 'Docker', 'Kubernetes', 'Microservices']
    
    # Calculate match score
    result = calculator.calculate_job_match_score(
        resume_text,
        job_description,
        resume_skills,
        job_skills,
        required_years=5
    )
    
    print(f"\n=== Job Match Analysis ===")
    print(f"Overall Score: {result['overall_score']:.2f}/100")
    print(f"Match Level: {result['match_level']}")
    
    print(f"\nText Similarity:")
    for key, value in result['text_similarity'].items():
        print(f"  {key}: {value:.2%}")
    
    print(f"\nSkill Match:")
    print(f"  Match Percentage: {result['skill_match']['match_percentage']:.2f}%")
    print(f"  Matched: {', '.join(result['skill_match']['matched_skills'])}")
    print(f"  Missing: {', '.join(result['skill_match']['missing_skills'])}")
    
    print(f"\nExperience Match:")
    print(f"  Candidate Years: {result['experience_match']['candidate_years']}")
    print(f"  Experience Level: {result['experience_match']['experience_level']}")
    print(f"  Meets Requirement: {result['experience_match']['meets_requirement']}")
    
    print(f"\nRecommendations:")
    for i, rec in enumerate(result['recommendations'], 1):
        print(f"  {i}. {rec}")


if __name__ == "__main__":
    test_similarity_calculator()