"""
AI Content Generator for HR Automation
Generates job descriptions and skills using Ollama (local) and Google Gemini API
"""

import json
import requests
import google.generativeai as genai
from typing import Dict, List, Optional, Tuple
import streamlit as st


class AIContentGenerator:
    """AI-powered content generator for job descriptions and skills"""
    
    def __init__(self, gemini_api_key: Optional[str] = None, ollama_url: str = "http://localhost:11434"):
        """Initialize AI content generator with available services"""
        self.gemini_api_key = gemini_api_key
        self.ollama_url = ollama_url
        self.gemini_available = False
        self.ollama_available = False
        
        # Initialize Gemini if API key provided
        if self.gemini_api_key:
            try:
                genai.configure(api_key=self.gemini_api_key)
                self.gemini_model = genai.GenerativeModel('gemini-2.5-flash')
                self.gemini_available = True
            except Exception as e:
                st.warning(f"Gemini API initialization failed: {e}")
        
        # Check Ollama availability
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                self.ollama_available = True
                self.ollama_models = self._get_ollama_models()
            else:
                self.ollama_available = False
        except Exception as e:
            self.ollama_available = False
    
    def _get_ollama_models(self) -> List[str]:
        """Get available Ollama models"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
            return []
        except Exception:
            return []
    
    def get_status(self) -> Dict[str, str]:
        """Get status of available AI services"""
        status = {}
        
        if self.gemini_available:
            status["Google Gemini"] = "✅ Available"
        else:
            status["Google Gemini"] = "❌ Not configured"
        
        if self.ollama_available:
            status["Ollama (Local)"] = f"✅ Available ({len(self.ollama_models)} models)"
        else:
            status["Ollama (Local)"] = "❌ Not running"
        
        return status
    
    def generate_job_description(self, job_title: str, company_name: str, experience_level: str, 
                               employment_type: str, location: str = "", department: str = "",
                               ai_service: str = "auto") -> Optional[str]:
        """Generate detailed job description using AI"""
        
        # Create prompt
        prompt = f"""
Generate a comprehensive job description for the following position:

Job Title: {job_title}
Company: {company_name}
Experience Level: {experience_level}
Employment Type: {employment_type}
Location: {location if location else "Remote/Flexible"}
Department: {department if department else "General"}

Please create a detailed job description that includes:
1. A compelling overview of the role
2. Key responsibilities and duties (4-6 bullet points)
3. What the candidate will be working on
4. Team collaboration aspects
5. Growth opportunities

Make it professional, engaging, and specific to the role. Focus on what makes this position attractive to potential candidates.

Format the response as a well-structured job description without any markdown formatting.
"""
        
        # Try to generate with selected or best available service
        if ai_service == "gemini" and self.gemini_available:
            return self._generate_with_gemini(prompt)
        elif ai_service == "ollama" and self.ollama_available:
            return self._generate_with_ollama(prompt)
        elif ai_service == "auto":
            # Try Gemini first, then Ollama
            if self.gemini_available:
                result = self._generate_with_gemini(prompt)
                if result:
                    return result
            if self.ollama_available:
                return self._generate_with_ollama(prompt)
        
        return None
    
    def generate_skills(self, job_title: str, experience_level: str, department: str = "",
                       ai_service: str = "auto") -> Tuple[Optional[List[str]], Optional[List[str]]]:
        """Generate required and preferred skills using AI"""
        
        # Create prompt
        prompt = f"""
Generate skills for the following position:

Job Title: {job_title}
Experience Level: {experience_level}
Department: {department if department else "General"}

Please provide two lists:

1. REQUIRED SKILLS (5-8 essential skills):
List the core technical and professional skills that are absolutely necessary for this role.

2. PREFERRED SKILLS (4-6 nice-to-have skills):
List additional skills that would be beneficial but not mandatory.

Focus on:
- Technical skills specific to the role
- Relevant tools and technologies
- Soft skills important for the position
- Industry-specific knowledge

Format your response as:
REQUIRED:
- Skill 1
- Skill 2
- Skill 3
...

PREFERRED:
- Skill 1
- Skill 2
- Skill 3
...

Provide only the skills lists without additional commentary.
"""
        
        # Try to generate with selected or best available service
        content = None
        if ai_service == "gemini" and self.gemini_available:
            content = self._generate_with_gemini(prompt)
        elif ai_service == "ollama" and self.ollama_available:
            content = self._generate_with_ollama(prompt)
        elif ai_service == "auto":
            # Try Gemini first, then Ollama
            if self.gemini_available:
                content = self._generate_with_gemini(prompt)
            if not content and self.ollama_available:
                content = self._generate_with_ollama(prompt)
        
        if content:
            return self._parse_skills_response(content)
        
        return None, None
    
    def _generate_with_gemini(self, prompt: str) -> Optional[str]:
        """Generate content using Google Gemini API"""
        try:
            response = self.gemini_model.generate_content(prompt)
            return response.text
        except Exception as e:
            st.error(f"Gemini API error: {e}")
            return None
    
    def _generate_with_ollama(self, prompt: str, model: str = None) -> Optional[str]:
        """Generate content using Ollama local API"""
        try:
            # Use the first available model if none specified
            if not model and self.ollama_models:
                model = self.ollama_models[0]
            elif not model:
                return None
            
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json().get('response', '')
            return None
            
        except Exception as e:
            st.error(f"Ollama API error: {e}")
            return None
    
    def _parse_skills_response(self, content: str) -> Tuple[List[str], List[str]]:
        """Parse AI response to extract required and preferred skills"""
        try:
            lines = content.strip().split('\n')
            required_skills = []
            preferred_skills = []
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check for section headers
                if 'REQUIRED' in line.upper():
                    current_section = 'required'
                    continue
                elif 'PREFERRED' in line.upper():
                    current_section = 'preferred'
                    continue
                
                # Extract skills (remove bullet points and clean up)
                if line.startswith('-') or line.startswith('•'):
                    skill = line[1:].strip()
                    if skill and current_section == 'required':
                        required_skills.append(skill)
                    elif skill and current_section == 'preferred':
                        preferred_skills.append(skill)
            
            return required_skills, preferred_skills
            
        except Exception as e:
            st.error(f"Error parsing skills response: {e}")
            return [], []
    
    def get_preferred_service(self) -> str:
        """Get the preferred AI service based on availability"""
        if self.gemini_available:
            return "gemini"
        elif self.ollama_available:
            return "ollama"
        else:
            return "none"
    
    def is_available(self) -> bool:
        """Check if any AI service is available"""
        return self.gemini_available or self.ollama_available


# Helper function to initialize AI generator
def get_ai_generator() -> Optional[AIContentGenerator]:
    """Initialize and return AI content generator"""
    try:
        # Try to get Gemini API key from config
        gemini_api_key = None
        try:
            from config import GEMINI_API_KEY
            gemini_api_key = GEMINI_API_KEY
        except ImportError:
            pass
        
        generator = AIContentGenerator(gemini_api_key=gemini_api_key)
        
        if generator.is_available():
            return generator
        else:
            return None
            
    except Exception as e:
        st.error(f"Failed to initialize AI generator: {e}")
        return None
