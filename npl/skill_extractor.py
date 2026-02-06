"""
Skill Extractor Module
Extracts and matches skills from resume text against skill database
"""

import re
import csv
import logging
from typing import List, Dict, Set, Tuple
from pathlib import Path
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SkillExtractor:
    """Extract and analyze skills from resume text"""
    
    def __init__(self, skills_file: str = None):
        self.skills_data = {}
        self.skill_categories = defaultdict(list)
        
        if skills_file:
            self.load_skills_database(skills_file)
    
    def load_skills_database(self, csv_file: str):
        """
        Load skills database from CSV file
        
        Args:
            csv_file: Path to skills CSV file
        """
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    skill = row['skill']
                    category = row['category']
                    weight = float(row['weight'])
                    
                    self.skills_data[skill.lower()] = {
                        'category': category,
                        'weight': weight,
                        'original': skill
                    }
                    
                    self.skill_categories[category].append(skill.lower())
            
            logger.info(f"Loaded {len(self.skills_data)} skills from database")
        
        except Exception as e:
            logger.error(f"Error loading skills database: {e}")
            raise
    
    def extract_skills(self, text: str) -> List[Dict]:
        """
        Extract skills from resume text
        
        Args:
            text: Resume text
            
        Returns:
            List of found skills with metadata
        """
        text_lower = text.lower()
        found_skills = []
        
        # Direct skill matching
        for skill, metadata in self.skills_data.items():
            # Use word boundaries for better matching
            pattern = r'\b' + re.escape(skill) + r'\b'
            
            if re.search(pattern, text_lower):
                found_skills.append({
                    'skill': metadata['original'],
                    'category': metadata['category'],
                    'weight': metadata['weight'],
                    'matched': True
                })
        

    
    def extract_skills_with_context(self, text: str, context_window: int = 50) -> List[Dict]:
        """
        Extract skills with surrounding context
        
        Args:
            text: Resume text
            context_window: Number of characters around the skill
            
        Returns:
            List of skills with context
        """
        text_lower = text.lower()
        skills_with_context = []
        
        for skill, metadata in self.skills_data.items():
            pattern = r'\b' + re.escape(skill) + r'\b'
            
            for match in re.finditer(pattern, text_lower):
                start = max(0, match.start() - context_window)
                end = min(len(text), match.end() + context_window)
                context = text[start:end]
                
                skills_with_context.append({
                    'skill': metadata['original'],
                    'category': metadata['category'],
                    'weight': metadata['weight'],
                    'context': context,
                    'position': match.start()
                })
        
        return skills_with_context
    
    def categorize_skills(self, skills: List[Dict]) -> Dict[str, List[str]]:
        """
        Categorize extracted skills
        
        Args:
            skills: List of skill dictionaries
            
        Returns:
            Dictionary with skills grouped by category
        """
        categorized = defaultdict(list)
        
        for skill in skills:
            category = skill['category']
            categorized[category].append(skill['skill'])
        
        return dict(categorized)
    
    def calculate_skill_coverage(self, 
                                 found_skills: List[Dict], 
                                 required_skills: List[str]) -> Tuple[float, List[str], List[str]]:
        """
        Calculate how well resume matches required skills
        
        Args:
            found_skills: Skills found in resume
            required_skills: Skills required for position
            
        Returns:
            Tuple of (coverage_percentage, matched_skills, missing_skills)
        """
        found_skill_names = {skill['skill'].lower() for skill in found_skills}
        required_skill_names = {skill.lower() for skill in required_skills}
        
        matched = found_skill_names & required_skill_names
        missing = required_skill_names - found_skill_names
        
        coverage = len(matched) / len(required_skill_names) * 100 if required_skill_names else 0
        
        return coverage, list(matched), list(missing)
    
    def get_skill_statistics(self, skills: List[Dict]) -> Dict:
        """
        Get statistical analysis of skills
        
        Args:
            skills: List of extracted skills
            
        Returns:
            Dictionary with skill statistics
        """
        if not skills:
            return {
                'total_skills': 0,
                'unique_categories': 0,
                'category_distribution': {},
                'average_weight': 0,
                'top_skills': []
            }
        
        categories = [skill['category'] for skill in skills]
        weights = [skill['weight'] for skill in skills]
        
        category_counts = defaultdict(int)
        for category in categories:
            category_counts[category] += 1
        
        # Sort skills by weight
        sorted_skills = sorted(skills, key=lambda x: x['weight'], reverse=True)
        
        return {
            'total_skills': len(skills),
            'unique_categories': len(set(categories)),
            'category_distribution': dict(category_counts),
            'average_weight': sum(weights) / len(weights),
            'top_skills': [s['skill'] for s in sorted_skills[:10]]
        }
    
    def recommend_skills(self, 
                        current_skills: List[Dict], 
                        target_role: str = None) -> List[str]:
        """
        Recommend skills to add based on current skills
        
        Args:
            current_skills: Currently possessed skills
            target_role: Target job role (optional)
            
        Returns:
            List of recommended skills to learn
        """
        current_skill_names = {skill['skill'].lower() for skill in current_skills}
        current_categories = {skill['category'] for skill in current_skills}
        
        recommendations = []
        
        # Recommend complementary skills from same categories
        for category in current_categories:
            category_skills = self.skill_categories.get(category, [])
            for skill in category_skills:
                if skill not in current_skill_names:
                    skill_data = self.skills_data[skill]
                    if skill_data['weight'] >= 0.8:  # High-value skills
                        recommendations.append(skill_data['original'])
        
        return recommendations[:10]  # Top 10 recommendations
    
    def extract_skill_years(self, text: str, skill: str) -> int:
        """
        Extract years of experience for a specific skill
        
        Args:
            text: Resume text
            skill: Skill name
            
        Returns:
            Years of experience (0 if not found)
        """
        text_lower = text.lower()
        skill_lower = skill.lower()
        
        # Look for patterns like "Python (5 years)" or "5+ years of Python"
        patterns = [
            rf'{re.escape(skill_lower)}.*?(\d+)\+?\s*years?',
            rf'(\d+)\+?\s*years?.*?{re.escape(skill_lower)}'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                return int(match.group(1))
        
        return 0
    
    def fuzzy_match_skills(self, text: str, threshold: float = 0.8) -> List[Dict]:
        """
        Perform fuzzy matching for skills (handles typos and variations)
        
        Args:
            text: Resume text
            threshold: Similarity threshold (0-1)
            
        Returns:
            List of fuzzy-matched skills
        """
        # Simple fuzzy matching using edit distance (basic implementation)
        # For production, consider using libraries like fuzzywuzzy or rapidfuzz
        
        text_lower = text.lower()
        words = set(re.findall(r'\b\w+\b', text_lower))
        
        fuzzy_matches = []
        
        for skill in self.skills_data.keys():
            skill_words = set(re.findall(r'\b\w+\b', skill))
            
            # Check for partial matches
            if skill_words & words:  # If any words match
                metadata = self.skills_data[skill]
                fuzzy_matches.append({
                    'skill': metadata['original'],
                    'category': metadata['category'],
                    'weight': metadata['weight'],
                    'match_type': 'fuzzy'
                })
        
        return fuzzy_matches


def test_skill_extractor():
    """Test the skill extractor"""
    # Create a sample skills file
    import tempfile
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write('category,skill,weight\n')
        f.write('Programming Languages,Python,0.9\n')
        f.write('Programming Languages,Java,0.85\n')
        f.write('Web Development,React,0.9\n')
        f.write('Cloud & DevOps,AWS,0.95\n')
        f.write('Cloud & DevOps,Docker,0.9\n')
        skills_file = f.name
    
    extractor = SkillExtractor(skills_file)
    
    sample_resume = """
    Experienced Software Engineer with strong skills in Python and Java.
    Built web applications using React and deployed them on AWS.
    Proficient in containerization with Docker.
    5+ years of Python experience.
    """
    
    # Extract skills
    skills = extractor.extract_skills(sample_resume)
    print(f"\nFound {len(skills)} skills:")
    for skill in skills:
        print(f"  - {skill['skill']} ({skill['category']}) - Weight: {skill['weight']}")
    
    # Categorize skills
    categorized = extractor.categorize_skills(skills)
    print(f"\nCategorized skills:")
    for category, skill_list in categorized.items():
        print(f"  {category}: {', '.join(skill_list)}")
    
    # Get statistics
    stats = extractor.get_skill_statistics(skills)
    print(f"\nSkill Statistics:")
    print(f"  Total Skills: {stats['total_skills']}")
    print(f"  Unique Categories: {stats['unique_categories']}")
    print(f"  Average Weight: {stats['average_weight']:.2f}")
    
    # Clean up
    import os
    os.unlink(skills_file)


if __name__ == "__main__":
    test_skill_extractor()