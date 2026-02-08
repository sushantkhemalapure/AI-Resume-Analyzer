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