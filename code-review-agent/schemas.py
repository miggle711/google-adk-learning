"""
Pydantic schemas for structured code review output.

These models define the structure of data returned by the code review agents,
ensuring type safety and validation.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class FunctionInfo(BaseModel):
    """Information about a single function in the codebase."""
    
    name: str = Field(description="Function name")
    line_number: int = Field(description="Line number where function starts")
    has_docstring: bool = Field(description="Whether function has a docstring")
    docstring: Optional[str] = Field(default=None, description="The docstring text if present")
    parameters: List[str] = Field(description="List of parameter names")
    complexity: int = Field(description="Cyclomatic complexity score")
    complexity_rank: str = Field(description="Complexity grade (A-F)")
    needs_attention: bool = Field(
        description="True if missing docstring OR complexity > 5"
    )
    recommendation: str = Field(description="Specific recommendation for this function")


class SecurityIssue(BaseModel):
    """A security vulnerability found in the code."""
    
    issue_id: str = Field(description="Bandit test ID (e.g., B105)")
    test_name: str = Field(description="Name of the security test")
    severity: str = Field(description="Issue severity: HIGH, MEDIUM, or LOW")
    confidence: str = Field(description="Confidence level: HIGH, MEDIUM, or LOW")
    description: str = Field(description="Description of the security issue")
    line_number: int = Field(description="Line number where issue occurs")
    code_snippet: str = Field(description="The problematic code")
    remediation: str = Field(description="How to fix this issue")


class FileReviewReport(BaseModel):
    """Complete code review report for a single file."""
    
    file_path: str = Field(description="Path to the reviewed file")
    total_functions: int = Field(description="Total number of functions in the file")
    functions_needing_attention: int = Field(
        description="Number of functions that need attention"
    )
    average_complexity: float = Field(description="Average cyclomatic complexity")
    security_score: int = Field(
        description="Security score 0-100 (100 = no issues)",
        ge=0,
        le=100
    )
    quality_grade: str = Field(
        description="Overall quality grade: A (excellent) to F (poor)"
    )
    functions: List[FunctionInfo] = Field(description="Detailed function analysis")
    security_issues: List[SecurityIssue] = Field(
        description="Security vulnerabilities found"
    )
    summary: str = Field(description="Overall summary of the code review")
    top_priorities: List[str] = Field(
        description="Top 3-5 most important actions to take"
    )


class ProjectReviewReport(BaseModel):
    """Code review report for multiple files in a project."""
    
    project_path: str = Field(description="Path to the project directory")
    total_files: int = Field(description="Total number of files reviewed")
    total_functions: int = Field(description="Total functions across all files")
    average_security_score: float = Field(
        description="Average security score across files"
    )
    overall_quality_grade: str = Field(
        description="Overall project quality grade"
    )
    file_reports: List[FileReviewReport] = Field(
        description="Individual file review reports"
    )
    critical_issues: List[str] = Field(
        description="Most critical issues across the project"
    )
    summary: str = Field(description="Overall project review summary")
