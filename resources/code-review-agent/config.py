"""
Configuration for the code review agent.

Centralized configuration for models, thresholds, and behavior.
"""

import os
from typing import List


class Config:
    """Configuration settings for the code review agent."""
    
    # LLM Model Configuration
    MODEL_NAME: str = "gemini-2.5-flash-lite"
    
    # Complexity Thresholds
    COMPLEXITY_THRESHOLD_LOW: int = 5  # A-B grade
    COMPLEXITY_THRESHOLD_MEDIUM: int = 10  # C grade
    COMPLEXITY_THRESHOLD_HIGH: int = 20  # D grade
    # Above 20 is F grade
    
    # Security Scoring
    SECURITY_SCORE_DEDUCTION_HIGH: int = 25
    SECURITY_SCORE_DEDUCTION_MEDIUM: int = 10
    SECURITY_SCORE_DEDUCTION_LOW: int = 5
    
    # Quality Grade Thresholds
    QUALITY_GRADE_EXCELLENT_SECURITY: int = 95  # A grade
    QUALITY_GRADE_GOOD_SECURITY: int = 80  # B grade
    QUALITY_GRADE_FAIR_SECURITY: int = 60  # C grade
    QUALITY_GRADE_POOR_SECURITY: int = 40  # D grade
    # Below 40 is F grade
    
    # File Patterns
    PYTHON_FILE_PATTERNS: List[str] = ["*.py"]
    EXCLUDE_PATTERNS: List[str] = [
        "**/__pycache__/**",
        "**/.venv/**",
        "**/venv/**",
        "**/.git/**",
        "**/node_modules/**",
        "**/.pytest_cache/**",
    ]
    
    # Tool Timeouts (seconds)
    AST_TIMEOUT: int = 30
    RADON_TIMEOUT: int = 30
    BANDIT_TIMEOUT: int = 60
    
    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    
    # Session Configuration
    APP_NAME: str = "code_review_agent"
    DEFAULT_USER_ID: str = "default_user"
    
    @classmethod
    def get_quality_grade(
        cls,
        security_score: int,
        avg_complexity: float,
        missing_docstrings_ratio: float
    ) -> str:
        """
        Calculate overall quality grade based on multiple factors.
        
        Args:
            security_score: Security score 0-100
            avg_complexity: Average cyclomatic complexity
            missing_docstrings_ratio: Ratio of functions without docstrings (0-1)
            
        Returns:
            Quality grade A-F
        """
        # Start with security score as base
        if security_score >= cls.QUALITY_GRADE_EXCELLENT_SECURITY and \
           avg_complexity <= cls.COMPLEXITY_THRESHOLD_LOW and \
           missing_docstrings_ratio < 0.1:
            return "A"
        
        if security_score >= cls.QUALITY_GRADE_GOOD_SECURITY and \
           avg_complexity <= cls.COMPLEXITY_THRESHOLD_MEDIUM and \
           missing_docstrings_ratio < 0.3:
            return "B"
        
        if security_score >= cls.QUALITY_GRADE_FAIR_SECURITY and \
           avg_complexity <= cls.COMPLEXITY_THRESHOLD_HIGH and \
           missing_docstrings_ratio < 0.5:
            return "C"
        
        if security_score >= cls.QUALITY_GRADE_POOR_SECURITY:
            return "D"
        
        return "F"


# Create a singleton instance
config = Config()
