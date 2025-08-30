"""
Gemini AI Integration for Resume Parsing
Uses Google's Gemini AI to intelligently categorize and clean resume data
"""

import json
import logging
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

# Gemini AI imports
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class GeminiParsedCandidate:
    """Represents a candidate parsed and cleaned by Gemini AI"""
    full_name: str = ""
    email: str = ""
    phone: str = ""
    linkedin_url: str = ""
    location: str = ""
    skills: List[str] = None
    experience_summary: str = ""
    education: List[str] = None
    current_company: str = ""
    current_position: str = ""
    total_experience: str = ""
    certifications: List[str] = None
    languages: List[str] = None
    
    def __post_init__(self):
        if self.skills is None:
            self.skills = []
        if self.education is None:
            self.education = []
        if self.certifications is None:
            self.certifications = []
        if self.languages is None:
            self.languages = []

class GeminiResumeParser:
    """Resume parser using Gemini AI for intelligent data extraction"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.model = None
        self.initialized = False
        
        if api_key:
            self.initialize_gemini(api_key)
    
    def initialize_gemini(self, api_key: str) -> bool:
        """Initialize Gemini AI with API key"""
        if not GEMINI_AVAILABLE:
            logger.error("Gemini AI library not available. Install with: pip install google-generativeai")
            return False
        
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            self.api_key = api_key
            self.initialized = True
            logger.info("Gemini AI initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Gemini AI: {e}")
            return False
    
    def create_parsing_prompt(self, resume_text: str) -> str:
        """Create a structured prompt for Gemini to parse resume data"""
        prompt = f"""
You are an expert HR assistant specializing in resume parsing. Please analyze the following resume text and extract information into the specified JSON format. Be very careful to categorize information correctly and avoid mixing up different types of data.

RESUME TEXT:
{resume_text}

Please extract and categorize the information into the following JSON structure. If a field cannot be determined from the resume, leave it empty or as an empty array:

{{
    "full_name": "Full name of the candidate",
    "email": "Email address only (no other contact info)",
    "phone": "Phone number only (formatted as +1-XXX-XXX-XXXX or similar)",
    "linkedin_url": "LinkedIn profile URL only (must contain linkedin.com)",
    "location": "Current city, state/country (geographic location only)",
    "current_company": "Current/most recent company name only",
    "current_position": "Current/most recent job title only",
    "total_experience": "Total years of experience (e.g., '5 years', '3+ years')",
    "skills": ["List of technical and professional skills only - no job titles, companies, or education"],
    "experience_summary": "Brief 2-3 sentence summary of work experience and key achievements",
    "education": ["Educational qualifications only - degrees, universities, graduation years"],
    "certifications": ["Professional certifications only - no skills or education degrees"],
    "languages": ["Spoken languages only (e.g., English, Spanish, French)"]
}}

IMPORTANT PARSING RULES:
1. SKILLS should only contain technical skills, tools, programming languages, frameworks, and professional competencies
2. EDUCATION should only contain degrees, universities, schools, and academic qualifications  
3. CERTIFICATIONS should only contain professional certifications (AWS, PMP, etc.)
4. Do not put job titles, company names, or education in the skills field
5. Do not put skills or certifications in the education field
6. Extract phone numbers in a clean format
7. Only include valid LinkedIn URLs (containing linkedin.com)
8. Current company and position should be the most recent/current role
9. Experience summary should focus on achievements and responsibilities, not list skills
10. Be precise and avoid categorization errors

Please respond with ONLY the JSON object, no additional text or explanation.
"""
        return prompt
    
    def parse_resume_with_gemini(self, resume_text: str) -> GeminiParsedCandidate:
        """
        Parse resume using Gemini AI
        
        Args:
            resume_text: Raw resume text content
            
        Returns:
            GeminiParsedCandidate object with categorized information
        """
        if not self.initialized:
            logger.error("Gemini AI not initialized. Please provide API key.")
            return GeminiParsedCandidate()
        
        try:
            # Create the parsing prompt
            prompt = self.create_parsing_prompt(resume_text)
            
            # Generate response from Gemini
            response = self.model.generate_content(prompt)
            
            if not response or not response.text:
                logger.error("Empty response from Gemini AI")
                return GeminiParsedCandidate()
            
            # Clean the response text (remove any markdown formatting)
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text.replace('```json', '').replace('```', '').strip()
            elif response_text.startswith('```'):
                response_text = response_text.replace('```', '').strip()
            
            # Parse JSON response
            try:
                parsed_data = json.loads(response_text)
                return self.create_candidate_from_json(parsed_data)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response from Gemini: {e}")
                logger.error(f"Response was: {response_text}")
                return GeminiParsedCandidate()
                
        except Exception as e:
            logger.error(f"Error parsing resume with Gemini AI: {e}")
            return GeminiParsedCandidate()
    
    def create_candidate_from_json(self, data: Dict[str, Any]) -> GeminiParsedCandidate:
        """Create GeminiParsedCandidate from JSON data"""
        candidate = GeminiParsedCandidate()
        
        # Basic information
        candidate.full_name = str(data.get('full_name', '')).strip()
        candidate.email = str(data.get('email', '')).strip()
        candidate.phone = str(data.get('phone', '')).strip()
        candidate.linkedin_url = str(data.get('linkedin_url', '')).strip()
        candidate.location = str(data.get('location', '')).strip()
        
        # Work information
        candidate.current_company = str(data.get('current_company', '')).strip()
        candidate.current_position = str(data.get('current_position', '')).strip()
        candidate.total_experience = str(data.get('total_experience', '')).strip()
        candidate.experience_summary = str(data.get('experience_summary', '')).strip()
        
        # Lists (ensure they are actually lists)
        candidate.skills = self.clean_list_field(data.get('skills', []))
        candidate.education = self.clean_list_field(data.get('education', []))
        candidate.certifications = self.clean_list_field(data.get('certifications', []))
        candidate.languages = self.clean_list_field(data.get('languages', []))
        
        return candidate
    
    def clean_list_field(self, field_data) -> List[str]:
        """Clean and validate list fields"""
        if not field_data:
            return []
        
        if isinstance(field_data, str):
            # If it's a string, try to split it
            field_data = [item.strip() for item in field_data.split(',') if item.strip()]
        
        if isinstance(field_data, list):
            # Clean each item
            cleaned = []
            for item in field_data:
                if isinstance(item, str):
                    item = item.strip()
                    if item and len(item) > 1:  # Avoid single characters
                        cleaned.append(item)
                else:
                    # Convert to string if not already
                    item_str = str(item).strip()
                    if item_str and len(item_str) > 1:
                        cleaned.append(item_str)
            return cleaned[:20]  # Limit to 20 items max
        
        return []
    
    def validate_parsed_data(self, candidate: GeminiParsedCandidate) -> Dict[str, List[str]]:
        """
        Validate the parsed data and return any issues found
        
        Returns:
            Dictionary with field names as keys and lists of issues as values
        """
        issues = {}
        
        # Validate email format
        if candidate.email:
            email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
            if not email_pattern.match(candidate.email):
                issues.setdefault('email', []).append('Invalid email format')
        
        # Validate LinkedIn URL
        if candidate.linkedin_url:
            if 'linkedin.com' not in candidate.linkedin_url.lower():
                issues.setdefault('linkedin_url', []).append('URL does not appear to be a LinkedIn profile')
            if not candidate.linkedin_url.startswith(('http://', 'https://')):
                issues.setdefault('linkedin_url', []).append('URL missing protocol (http/https)')
        
        # Validate phone format
        if candidate.phone:
            # Basic phone validation - should contain digits
            if not re.search(r'\d{3,}', candidate.phone):
                issues.setdefault('phone', []).append('Phone number appears invalid')
        
        # Check for potential categorization errors in skills
        if candidate.skills:
            for skill in candidate.skills:
                skill_lower = skill.lower()
                # Check if education terms are in skills
                if any(term in skill_lower for term in ['university', 'college', 'bachelor', 'master', 'phd', 'degree']):
                    issues.setdefault('skills', []).append(f'Education term found in skills: {skill}')
                # Check if company names are in skills (basic check)
                if any(term in skill_lower for term in ['inc', 'corp', 'ltd', 'llc', 'company']):
                    issues.setdefault('skills', []).append(f'Company name might be in skills: {skill}')
        
        return issues
    
    def test_gemini_connection(self) -> bool:
        """Test if Gemini AI is working correctly"""
        if not self.initialized:
            return False
        
        try:
            test_prompt = "Please respond with just the word 'SUCCESS' to confirm you are working."
            response = self.model.generate_content(test_prompt)
            
            if response and response.text:
                return 'SUCCESS' in response.text.upper()
            
            return False
        except Exception as e:
            logger.error(f"Gemini connection test failed: {e}")
            return False

class HybridResumeParser:
    """
    Combines traditional parsing with Gemini AI for best results
    Falls back to traditional parsing if Gemini fails
    """
    
    def __init__(self, gemini_api_key: str = None):
        # Initialize traditional parser
        try:
            from resume_parser import ResumeParser
            self.traditional_parser = ResumeParser()
            self.traditional_available = True
        except ImportError:
            self.traditional_parser = None
            self.traditional_available = False
            logger.warning("Traditional resume parser not available")
        
        # Initialize Gemini parser
        self.gemini_parser = GeminiResumeParser(gemini_api_key)
    
    def parse_resume(self, resume_text: str, use_gemini: bool = True) -> Dict[str, Any]:
        """
        Parse resume using hybrid approach
        
        Args:
            resume_text: Raw resume text
            use_gemini: Whether to use Gemini AI (fallback to traditional if fails)
            
        Returns:
            Dictionary with parsed candidate data
        """
        result = {
            'success': False,
            'method': 'none',
            'data': {},
            'issues': [],
            'raw_text': resume_text[:500] + '...' if len(resume_text) > 500 else resume_text
        }
        
        # Try Gemini AI first (if available and requested)
        if use_gemini and self.gemini_parser.initialized:
            try:
                logger.info("Attempting to parse resume with Gemini AI...")
                gemini_result = self.gemini_parser.parse_resume_with_gemini(resume_text)
                
                if gemini_result.full_name:  # Basic check for successful parsing
                    # Validate the results
                    issues = self.gemini_parser.validate_parsed_data(gemini_result)
                    
                    result['success'] = True
                    result['method'] = 'gemini'
                    result['data'] = self.convert_to_dict(gemini_result)
                    result['issues'] = issues
                    
                    logger.info("Successfully parsed resume with Gemini AI")
                    return result
                else:
                    logger.warning("Gemini AI parsing failed - no name extracted")
            except Exception as e:
                logger.error(f"Gemini AI parsing failed: {e}")
        
        # Fallback to traditional parsing
        if self.traditional_available:
            try:
                logger.info("Falling back to traditional resume parsing...")
                traditional_result = self.traditional_parser.parse_text(resume_text)
                
                result['success'] = True
                result['method'] = 'traditional'
                result['data'] = self.convert_traditional_to_dict(traditional_result)
                result['issues'] = ['Used traditional parser - data may need manual review']
                
                logger.info("Successfully parsed resume with traditional parser")
                return result
            except Exception as e:
                logger.error(f"Traditional parsing also failed: {e}")
        
        # Both methods failed
        result['issues'] = ['Both Gemini AI and traditional parsing failed']
        logger.error("All parsing methods failed")
        return result
    
    def convert_to_dict(self, candidate: GeminiParsedCandidate) -> Dict[str, Any]:
        """Convert GeminiParsedCandidate to dictionary"""
        return {
            'full_name': candidate.full_name,
            'email': candidate.email,
            'phone': candidate.phone,
            'linkedin_url': candidate.linkedin_url,
            'location': candidate.location,
            'company': candidate.current_company,
            'position': candidate.current_position,
            'skills': ', '.join(candidate.skills) if candidate.skills else '',
            'experience_summary': candidate.experience_summary,
            'total_experience': candidate.total_experience,
            'education': ' | '.join(candidate.education) if candidate.education else '',
            'certifications': ', '.join(candidate.certifications) if candidate.certifications else '',
            'languages': ', '.join(candidate.languages) if candidate.languages else ''
        }
    
    def convert_traditional_to_dict(self, candidate) -> Dict[str, Any]:
        """Convert traditional ParsedCandidate to dictionary"""
        return {
            'full_name': candidate.full_name,
            'email': candidate.email,
            'phone': candidate.phone,
            'linkedin_url': candidate.linkedin_url,
            'location': candidate.location,
            'company': candidate.current_company,
            'position': candidate.current_position,
            'skills': ', '.join(candidate.skills) if candidate.skills else '',
            'experience_summary': candidate.experience_summary,
            'total_experience': candidate.total_experience,
            'education': ' | '.join(candidate.education) if candidate.education else '',
            'certifications': '',
            'languages': ''
        }

def install_gemini_dependency():
    """Install Google Generative AI library"""
    import subprocess
    import sys
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "google-generativeai"])
        print("✅ Successfully installed google-generativeai")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install google-generativeai: {e}")
        return False

def test_gemini_parsing():
    """Test function for Gemini parsing"""
    # This would require an actual API key to test
    print("🧪 Gemini AI Resume Parser Test")
    print("Note: Requires valid Gemini API key to test")
    
    sample_resume = """
    John Doe
    Senior Software Engineer
    john.doe@email.com
    (555) 123-4567
    https://linkedin.com/in/johndoe
    San Francisco, CA
    
    EXPERIENCE
    Senior Software Engineer - Tech Corp Inc (2021 - Present)
    - Developed web applications using Python and React
    - Led a team of 5 developers
    - Implemented CI/CD pipelines
    
    Software Engineer - StartupXYZ (2019 - 2021)
    - Built REST APIs using Node.js and Express
    - Worked with PostgreSQL and MongoDB databases
    
    SKILLS
    Python, JavaScript, React, Node.js, PostgreSQL, MongoDB, Docker, AWS, Git
    
    EDUCATION
    Bachelor of Science in Computer Science - Stanford University (2019)
    
    CERTIFICATIONS
    AWS Certified Solutions Architect
    
    LANGUAGES
    English (Native), Spanish (Fluent)
    """
    
    print("Sample resume text prepared for testing.")
    print("To test with actual API key, initialize GeminiResumeParser with your key.")

if __name__ == "__main__":
    # Check if Gemini library is available
    if not GEMINI_AVAILABLE:
        print("❌ Google Generative AI library not available")
        print("Install with: pip install google-generativeai")
    else:
        print("✅ Google Generative AI library is available")
    
    # Run test
    test_gemini_parsing()
