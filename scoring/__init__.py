"""
Scoring Module
ATS scoring and similarity calculation components
"""

__version__ = '1.0.0'
__author__ = 'ATS Resume Analyzer Team'

from .ats_score import ATSScoreCalculator, ATSScoreResult
from .similarity import SimilarityCalculator

__all__ = ['ATSScoreCalculator', 'ATSScoreResult', 'SimilarityCalculator']