"""
Resume Parser Module
Extracts candidate information from resume files (PDF, DOCX, TXT)
"""

import re
import os
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path

# File parsing libraries
try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    import spacy
    # Load English model if available
    try:
        nlp = spacy.load("en_core_web_sm")
        NLP_AVAILABLE = True
    except OSError:
        # Model not installed, use basic regex parsing
        nlp = None
        NLP_AVAILABLE = False
except ImportError:
    nlp = None
    NLP_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ParsedCandidate:
    """Represents a candidate parsed from resume"""
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
    
    def __post_init__(self):
        if self.skills is None:
            self.skills = []
        if self.education is None:
            self.education = []

class ResumeParser:
    """Main resume parser class"""
    
    def __init__(self):
        self.setup_patterns()
        
    def setup_patterns(self):
        """Setup regex patterns for information extraction"""
        # Email pattern
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        
        # Phone pattern (flexible for various formats)
        self.phone_pattern = re.compile(r'(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})')
        
        # LinkedIn URL pattern
        self.linkedin_pattern = re.compile(r'(?:https?://)?(?:www\.)?linkedin\.com/in/[A-Za-z0-9_-]+/?', re.IGNORECASE)
        
        # Name patterns (usually at the beginning of resume)
        self.name_patterns = [
            re.compile(r'^([A-Z][a-z]+ [A-Z][a-z]+)', re.MULTILINE),
            re.compile(r'^([A-Z][a-z]+ [A-Z]\. [A-Z][a-z]+)', re.MULTILINE),
            re.compile(r'^([A-Z][a-z]+ [A-Z][a-z]+ [A-Z][a-z]+)', re.MULTILINE)
        ]
        
        # Experience indicators
        self.experience_patterns = [
            re.compile(r'(\d+)\+?\s*years?\s+(?:of\s+)?experience', re.IGNORECASE),
            re.compile(r'(\d+)\+?\s*yrs?\s+(?:of\s+)?experience', re.IGNORECASE),
            re.compile(r'experience.*?(\d+)\+?\s*years?', re.IGNORECASE)
        ]
        
        # Skills section indicators
        self.skills_section_patterns = [
            re.compile(r'(?:technical\s+)?skills?\s*:?\s*([^\n]+(?:\n[^\n]+)*)', re.IGNORECASE | re.MULTILINE),
            re.compile(r'technologies?\s*:?\s*([^\n]+(?:\n[^\n]+)*)', re.IGNORECASE | re.MULTILINE),
            re.compile(r'programming\s+languages?\s*:?\s*([^\n]+(?:\n[^\n]+)*)', re.IGNORECASE | re.MULTILINE)
        ]
        
        # Common technical skills (for better extraction)
        self.common_skills = [
            'Python', 'Java', 'JavaScript', 'C++', 'C#', 'Ruby', 'PHP', 'Go', 'Rust', 'Swift',
            'React', 'Angular', 'Vue.js', 'Node.js', 'Django', 'Flask', 'Spring', 'Laravel',
            'HTML', 'CSS', 'TypeScript', 'SQL', 'PostgreSQL', 'MySQL', 'MongoDB', 'Redis',
            'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Jenkins', 'Git', 'Linux',
            'Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch', 'Pandas', 'NumPy',
            'REST API', 'GraphQL', 'Microservices', 'DevOps', 'CI/CD', 'Agile', 'Scrum'
        ]
    
    def parse_resume_file(self, file_path: str) -> ParsedCandidate:
        """
        Parse resume from file path
        
        Args:
            file_path: Path to resume file
            
        Returns:
            ParsedCandidate object with extracted information
        """
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return ParsedCandidate()
        
        # Get file extension
        file_ext = Path(file_path).suffix.lower()
        
        try:
            # Extract text based on file type
            if file_ext == '.pdf':
                text = self.extract_text_from_pdf(file_path)
            elif file_ext == '.docx':
                text = self.extract_text_from_docx(file_path)
            elif file_ext in ['.txt', '.text']:
                text = self.extract_text_from_txt(file_path)
            else:
                logger.error(f"Unsupported file type: {file_ext}")
                return ParsedCandidate()
            
            if not text.strip():
                logger.error("No text extracted from file")
                return ParsedCandidate()
            
            # Parse the extracted text
            return self.parse_text(text)
            
        except Exception as e:
            logger.error(f"Error parsing resume file: {e}")
            return ParsedCandidate()
    
    def parse_resume_content(self, content: str, filename: str = "uploaded_file") -> ParsedCandidate:
        """
        Parse resume from text content
        
        Args:
            content: Resume text content
            filename: Original filename for context
            
        Returns:
            ParsedCandidate object with extracted information
        """
        try:
            return self.parse_text(content)
        except Exception as e:
            logger.error(f"Error parsing resume content: {e}")
            return ParsedCandidate()
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        if not PDF_AVAILABLE:
            raise ImportError("PyPDF2 not available. Install with: pip install PyPDF2")
        
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
        
        return text
    
    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        if not DOCX_AVAILABLE:
            raise ImportError("python-docx not available. Install with: pip install python-docx")
        
        text = ""
        try:
            doc = Document(file_path)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
        except Exception as e:
            logger.error(f"Error extracting text from DOCX: {e}")
        
        return text
    
    def extract_text_from_txt(self, file_path: str) -> str:
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    return file.read()
            except Exception as e:
                logger.error(f"Error reading text file: {e}")
                return ""
        except Exception as e:
            logger.error(f"Error extracting text from TXT: {e}")
            return ""
    
    def parse_text(self, text: str) -> ParsedCandidate:
        """
        Parse candidate information from resume text
        
        Args:
            text: Resume text content
            
        Returns:
            ParsedCandidate object with extracted information
        """
        candidate = ParsedCandidate()
        
        # Clean text
        text = self.clean_text(text)
        
        # Extract basic information
        candidate.email = self.extract_email(text)
        candidate.phone = self.extract_phone(text)
        candidate.linkedin_url = self.extract_linkedin(text)
        candidate.full_name = self.extract_name(text)
        candidate.location = self.extract_location(text)
        
        # Extract skills
        candidate.skills = self.extract_skills(text)
        
        # Extract experience
        candidate.total_experience = self.extract_experience_years(text)
        candidate.experience_summary = self.extract_experience_summary(text)
        
        # Extract current company and position
        candidate.current_company, candidate.current_position = self.extract_current_work(text)
        
        # Extract education
        candidate.education = self.extract_education(text)
        
        return candidate
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\n+', '\n', text)
        text = re.sub(r' +', ' ', text)
        return text.strip()
    
    def extract_email(self, text: str) -> str:
        """Extract email address"""
        emails = self.email_pattern.findall(text)
        return emails[0] if emails else ""
    
    def extract_phone(self, text: str) -> str:
        """Extract phone number"""
        phones = self.phone_pattern.findall(text)
        if phones:
            # Format as (XXX) XXX-XXXX
            area, prefix, number = phones[0]
            return f"({area}) {prefix}-{number}"
        return ""
    
    def extract_linkedin(self, text: str) -> str:
        """Extract LinkedIn URL"""
        linkedin_urls = self.linkedin_pattern.findall(text)
        if linkedin_urls:
            url = linkedin_urls[0]
            # Ensure it starts with https://
            if not url.startswith('http'):
                url = 'https://' + url
            return url
        return ""
    
    def extract_name(self, text: str) -> str:
        """Extract candidate name (usually at the top)"""
        lines = text.split('\n')
        
        # Try to find name in first few lines
        for line in lines[:5]:
            line = line.strip()
            if len(line) > 0 and not any(x in line.lower() for x in ['email', 'phone', 'linkedin', 'address']):
                # Check if it looks like a name
                if re.match(r'^[A-Za-z][a-z]*\s+[A-Za-z][a-z]*(?:\s+[A-Za-z][a-z]*)?$', line):
                    return line
                
                # Try name patterns
                for pattern in self.name_patterns:
                    match = pattern.search(line)
                    if match:
                        return match.group(1)
        
        return ""
    
    def extract_location(self, text: str) -> str:
        """Extract location/address"""
        # Look for common location patterns
        location_patterns = [
            re.compile(r'([A-Za-z\s]+,\s*[A-Z]{2}(?:\s+\d{5})?)', re.MULTILINE),  # City, State ZIP
            re.compile(r'([A-Za-z\s]+,\s*[A-Za-z\s]+)', re.MULTILINE),  # City, State/Country
        ]
        
        for pattern in location_patterns:
            matches = pattern.findall(text)
            if matches:
                # Filter out common false positives
                for match in matches:
                    if not any(word in match.lower() for word in ['university', 'college', 'company', 'inc', 'corp']):
                        return match.strip()
        
        return ""
    
    def extract_skills(self, text: str) -> List[str]:
        """Extract technical skills"""
        found_skills = []
        
        # First, look for dedicated skills sections
        for pattern in self.skills_section_patterns:
            matches = pattern.findall(text)
            for match in matches:
                # Parse skills from the section
                skills_text = match.strip()
                # Split by common separators
                skills_parts = re.split(r'[,•·\n-]+', skills_text)
                for skill in skills_parts:
                    skill = skill.strip()
                    if skill and len(skill) > 1:
                        found_skills.append(skill)
        
        # Also search for common technical skills throughout the text
        text_lower = text.lower()
        for skill in self.common_skills:
            if skill.lower() in text_lower:
                # Check if it's a whole word match
                if re.search(r'\b' + re.escape(skill.lower()) + r'\b', text_lower):
                    if skill not in found_skills:
                        found_skills.append(skill)
        
        # Clean and deduplicate skills
        cleaned_skills = []
        for skill in found_skills:
            skill = re.sub(r'[^\w\s+#.-]', '', skill).strip()
            if skill and len(skill) > 1 and skill not in cleaned_skills:
                cleaned_skills.append(skill)
        
        return cleaned_skills[:20]  # Limit to top 20 skills
    
    def extract_experience_years(self, text: str) -> str:
        """Extract total years of experience"""
        for pattern in self.experience_patterns:
            match = pattern.search(text)
            if match:
                years = match.group(1)
                return f"{years} years"
        
        return ""
    
    def extract_experience_summary(self, text: str) -> str:
        """Extract a summary of work experience"""
        lines = text.split('\n')
        experience_lines = []
        
        # Look for experience/work history section
        in_experience_section = False
        for line in lines:
            line = line.strip()
            
            # Check if we're entering experience section
            if any(keyword in line.lower() for keyword in ['experience', 'employment', 'work history', 'career']):
                in_experience_section = True
                continue
            
            # Check if we're leaving experience section
            if in_experience_section and any(keyword in line.lower() for keyword in ['education', 'skills', 'projects', 'certifications']):
                break
            
            # Collect experience lines
            if in_experience_section and line and len(line) > 10:
                experience_lines.append(line)
                if len(experience_lines) >= 3:  # Limit to first few lines
                    break
        
        if experience_lines:
            return ' '.join(experience_lines)[:300]  # Limit length
        
        return ""
    
    def extract_current_work(self, text: str) -> tuple:
        """Extract current company and position"""
        lines = text.split('\n')
        
        # Look for current work in first part of resume
        for i, line in enumerate(lines[:20]):
            line = line.strip()
            
            # Look for date patterns that indicate current work
            if any(keyword in line.lower() for keyword in ['present', 'current', '2023', '2024', '2025']):
                # Look around this line for company and position
                context_lines = lines[max(0, i-3):i+3]
                
                for context_line in context_lines:
                    context_line = context_line.strip()
                    
                    # Try to identify company (often has Inc, Corp, Ltd, etc.)
                    if any(indicator in context_line.lower() for indicator in ['inc', 'corp', 'ltd', 'llc', 'company']):
                        company = context_line
                        
                        # Look for position in nearby lines
                        for pos_line in context_lines:
                            pos_line = pos_line.strip()
                            if any(title in pos_line.lower() for title in ['engineer', 'developer', 'manager', 'analyst', 'specialist', 'lead', 'senior']):
                                return company, pos_line
                        
                        return company, ""
        
        return "", ""
    
    def extract_education(self, text: str) -> List[str]:
        """Extract education information"""
        education = []
        
        # Education indicators
        education_keywords = ['university', 'college', 'bachelor', 'master', 'phd', 'degree', 'diploma']
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in education_keywords):
                if len(line) > 5 and len(line) < 150:  # Reasonable length
                    education.append(line)
                    if len(education) >= 3:  # Limit to 3 entries
                        break
        
        return education
    
    def get_supported_file_types(self) -> List[str]:
        """Get list of supported file types"""
        supported = ['.txt']
        
        if PDF_AVAILABLE:
            supported.append('.pdf')
        
        if DOCX_AVAILABLE:
            supported.append('.docx')
        
        return supported
    
    def validate_file(self, file_path: str) -> tuple:
        """
        Validate if file can be parsed
        
        Returns:
            (is_valid: bool, error_message: str)
        """
        if not os.path.exists(file_path):
            return False, "File not found"
        
        file_ext = Path(file_path).suffix.lower()
        supported_types = self.get_supported_file_types()
        
        if file_ext not in supported_types:
            return False, f"Unsupported file type. Supported: {', '.join(supported_types)}"
        
        # Check file size (limit to 10MB)
        file_size = os.path.getsize(file_path)
        if file_size > 10 * 1024 * 1024:  # 10MB
            return False, "File too large (max 10MB)"
        
        return True, ""

def install_dependencies():
    """Install required dependencies"""
    import subprocess
    import sys
    
    dependencies = [
        "PyPDF2",
        "python-docx",
        "spacy"
    ]
    
    for dep in dependencies:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
        except Exception as e:
            logger.error(f"Failed to install {dep}: {e}")
    
    # Try to download spacy model
    try:
        subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
    except Exception as e:
        logger.warning(f"Failed to download spacy model: {e}")

# Test function
def test_parser():
    """Test the resume parser with sample text"""
    parser = ResumeParser()
    
    sample_resume = """
    John Doe
    Software Engineer
    john.doe@email.com
    (555) 123-4567
    https://linkedin.com/in/johndoe
    San Francisco, CA
    
    EXPERIENCE
    Senior Software Engineer - Tech Corp Inc (2021 - Present)
    - Developed web applications using Python and React
    - Led a team of 5 developers
    - Implemented CI/CD pipelines
    
    SKILLS
    Python, JavaScript, React, Node.js, AWS, Docker, PostgreSQL, Git
    
    EDUCATION
    Bachelor of Science in Computer Science - Stanford University
    """
    
    result = parser.parse_text(sample_resume)
    
    print("=== Resume Parser Test Results ===")
    print(f"Name: {result.full_name}")
    print(f"Email: {result.email}")
    print(f"Phone: {result.phone}")
    print(f"LinkedIn: {result.linkedin_url}")
    print(f"Location: {result.location}")
    print(f"Skills: {result.skills}")
    print(f"Experience: {result.total_experience}")
    print(f"Company: {result.current_company}")
    print(f"Position: {result.current_position}")
    print(f"Education: {result.education}")

if __name__ == "__main__":
    # Check dependencies
    missing_deps = []
    if not PDF_AVAILABLE:
        missing_deps.append("PyPDF2")
    if not DOCX_AVAILABLE:
        missing_deps.append("python-docx")
    if not NLP_AVAILABLE:
        missing_deps.append("spacy (with en_core_web_sm model)")
    
    if missing_deps:
        print(f"Missing dependencies: {', '.join(missing_deps)}")
        print("Install with: pip install PyPDF2 python-docx spacy")
        print("Then: python -m spacy download en_core_web_sm")
    else:
        print("All dependencies available!")
    
    # Run test
    test_parser()
