"""
AI HR Recruitment Agent

An intelligent recruitment automation system that leverages AI to streamline 
the entire hiring process - from job description analysis to candidate outreach.

Key Components:
- HRRecruitmentAgent: Main agent class with AI integration
- HRDatabase: Database operations and schema
- ReportGenerator: Analytics and reporting
- StreamlitApp: Web interface

Dependencies:
- Google Gemini API for job analysis
- Ollama for local AI processing
- Streamlit for web interface
"""

__version__ = "1.0.0"
__author__ = "AI HR Automation Team"
__description__ = "AI-powered recruitment automation system"

# Main exports
from .hr_agent import HRRecruitmentAgent, AIService, MockLinkedInAPI
from .database import HRDatabase, Candidate, Job
from .reporting import ReportGenerator

__all__ = [
    'HRRecruitmentAgent',
    'AIService', 
    'MockLinkedInAPI',
    'HRDatabase',
    'Candidate',
    'Job',
    'ReportGenerator'
]
