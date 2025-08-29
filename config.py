"""
Configuration Module for HR Automation System
Loads environment variables and provides configuration settings
"""

import os
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for HR Automation System"""
    
    # Gemini AI Configuration
    GEMINI_API_KEY: Optional[str] = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
    
    # Ollama Configuration  
    OLLAMA_HOST: str = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
    OLLAMA_MODEL: str = os.getenv('OLLAMA_MODEL', 'llama3.1:8b')
    
    # LinkedIn API Configuration
    LINKEDIN_CLIENT_ID: Optional[str] = os.getenv('LINKEDIN_CLIENT_ID')
    LINKEDIN_CLIENT_SECRET: Optional[str] = os.getenv('LINKEDIN_CLIENT_SECRET')
    
    # Email Configuration
    SMTP_SERVER: str = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT: int = int(os.getenv('SMTP_PORT', '587'))
    SMTP_USERNAME: Optional[str] = os.getenv('SMTP_USERNAME')
    SMTP_PASSWORD: Optional[str] = os.getenv('SMTP_PASSWORD')
    
    # Database Configuration
    DATABASE_PATH: str = os.getenv('DATABASE_PATH', './data/hr_recruitment.db')
    
    # Application Configuration
    DEBUG_MODE: bool = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    
    @classmethod
    def is_gemini_configured(cls) -> bool:
        """Check if Gemini API key is configured"""
        return cls.GEMINI_API_KEY is not None and cls.GEMINI_API_KEY.strip() != '' and not cls.GEMINI_API_KEY.endswith('_here')
    
    @classmethod
    def is_email_configured(cls) -> bool:
        """Check if email configuration is complete"""
        return all([
            cls.SMTP_USERNAME,
            cls.SMTP_PASSWORD,
            cls.SMTP_USERNAME.strip() != '',
            cls.SMTP_PASSWORD.strip() != '',
            not cls.SMTP_USERNAME.endswith('@gmail.com') or cls.SMTP_USERNAME != 'your_email@gmail.com'
        ])
    
    @classmethod
    def is_linkedin_configured(cls) -> bool:
        """Check if LinkedIn API is configured"""
        return all([
            cls.LINKEDIN_CLIENT_ID,
            cls.LINKEDIN_CLIENT_SECRET,
            cls.LINKEDIN_CLIENT_ID.strip() != '',
            cls.LINKEDIN_CLIENT_SECRET.strip() != '',
            not cls.LINKEDIN_CLIENT_ID.startswith('your_')
        ])
    
    @classmethod
    def get_status_summary(cls) -> dict:
        """Get configuration status summary"""
        return {
            'gemini_ai': '✅ Configured' if cls.is_gemini_configured() else '❌ Not configured',
            'email': '✅ Configured' if cls.is_email_configured() else '❌ Not configured',
            'linkedin': '✅ Configured' if cls.is_linkedin_configured() else '❌ Not configured',
            'database': f'✅ {cls.DATABASE_PATH}',
            'debug_mode': '🐛 Enabled' if cls.DEBUG_MODE else '🔒 Disabled'
        }

# Create a global config instance
config = Config()

# Export commonly used values
GEMINI_API_KEY = config.GEMINI_API_KEY
DEBUG_MODE = config.DEBUG_MODE
