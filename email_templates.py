"""
Email Template System for AI HR Recruitment Agent
Handles email personalization, template rendering, and content generation
"""

import re
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from email_config import get_email_config, get_email_template

@dataclass 
class CandidateData:
    """Data structure for candidate information"""
    name: str
    email: str
    job_title: str = ""
    experience_years: str = ""
    skills: str = ""
    location: str = ""
    
    def to_dict(self) -> Dict[str, str]:
        """Convert candidate data to dictionary for template formatting"""
        return {
            'candidate_name': self.name,
            'candidate_email': self.email,
            'job_title': self.job_title,
            'experience_years': self.experience_years,
            'skills': self.skills,
            'location': self.location
        }

class EmailTemplateRenderer:
    """Handles email template rendering and personalization"""
    
    def __init__(self):
        self.config = get_email_config()
        self.company_vars = {
            'company_name': self.config.COMPANY_NAME,
            'company_website': self.config.COMPANY_WEBSITE,
            'hr_contact_name': self.config.HR_CONTACT_NAME,
            'hr_contact_email': self.config.HR_CONTACT_EMAIL,
            'hr_contact_phone': self.config.HR_CONTACT_PHONE,
            'sender_name': self.config.SENDER_NAME
        }
    
    def render_email(self, candidate: CandidateData, template_name: str = "recruitment_interest") -> Dict[str, str]:
        """
        Render personalized email for a candidate
        
        Args:
            candidate: Candidate data
            template_name: Name of email template to use
            
        Returns:
            Dictionary with 'subject' and 'body' keys
        """
        template = get_email_template(template_name)
        
        # Combine candidate data with company variables
        template_vars = {**self.company_vars, **candidate.to_dict()}
        
        # Render subject and body
        try:
            subject = template['subject'].format(**template_vars)
            body = template['body'].format(**template_vars)
            
            # Clean up any formatting issues
            body = self._clean_email_body(body)
            
            return {
                'subject': subject,
                'body': body
            }
        except KeyError as e:
            raise ValueError(f"Missing template variable: {e}")
    
    def _clean_email_body(self, body: str) -> str:
        """Clean up email body formatting"""
        # Remove excessive whitespace
        body = re.sub(r'\n\s*\n\s*\n', '\n\n', body)
        # Ensure proper line breaks
        body = body.replace('\r\n', '\n').replace('\r', '\n')
        return body.strip()
    
    def preview_email(self, candidate: CandidateData, template_name: str = "recruitment_interest") -> str:
        """
        Generate a preview of the email for testing
        
        Args:
            candidate: Candidate data
            template_name: Template to preview
            
        Returns:
            Formatted email preview string
        """
        email_content = self.render_email(candidate, template_name)
        
        preview = f"""
=== EMAIL PREVIEW ===
To: {candidate.email}
Subject: {email_content['subject']}

{email_content['body']}
=== END PREVIEW ===
        """.strip()
        
        return preview
    
    def get_available_templates(self) -> List[str]:
        """Get list of available email templates"""
        from email_config import EMAIL_TEMPLATES
        return list(EMAIL_TEMPLATES.keys())
    
    def validate_template_variables(self, template_name: str) -> Dict[str, Any]:
        """
        Validate that all required variables are available for a template
        
        Returns:
            Dictionary with validation results
        """
        template = get_email_template(template_name)
        
        # Extract variables from template
        subject_vars = re.findall(r'\{(\w+)\}', template['subject'])
        body_vars = re.findall(r'\{(\w+)\}', template['body'])
        all_vars = set(subject_vars + body_vars)
        
        # Check which variables are available
        available_vars = set(self.company_vars.keys()) | {
            'candidate_name', 'candidate_email', 'job_title', 
            'experience_years', 'skills', 'location'
        }
        
        missing_vars = all_vars - available_vars
        
        return {
            'template_name': template_name,
            'required_variables': sorted(all_vars),
            'available_variables': sorted(available_vars),
            'missing_variables': sorted(missing_vars),
            'is_valid': len(missing_vars) == 0
        }

class EmailPersonalizer:
    """Advanced email personalization features"""
    
    def __init__(self):
        self.renderer = EmailTemplateRenderer()
    
    def enhance_candidate_data(self, candidate: CandidateData) -> CandidateData:
        """
        Enhance candidate data with additional personalization
        
        Args:
            candidate: Basic candidate data
            
        Returns:
            Enhanced candidate data
        """
        # Clean up skills formatting
        if candidate.skills:
            skills = candidate.skills.strip()
            # Ensure proper formatting of skills list
            if ',' in skills and not skills.endswith('.'):
                candidate.skills = skills
            elif skills and not skills.endswith('.'):
                candidate.skills = skills
        
        # Format experience years
        if candidate.experience_years:
            years = str(candidate.experience_years).strip()
            if years.isdigit():
                num_years = int(years)
                if num_years == 1:
                    candidate.experience_years = "1 year"
                else:
                    candidate.experience_years = f"{num_years} years"
        
        # Clean up job title
        if candidate.job_title:
            candidate.job_title = candidate.job_title.strip().title()
        
        return candidate
    
    def generate_personalized_subject_variations(self, candidate: CandidateData) -> List[str]:
        """
        Generate multiple subject line variations for A/B testing
        
        Args:
            candidate: Candidate data
            
        Returns:
            List of subject line variations
        """
        config = self.renderer.config
        variations = [
            f"Exciting Opportunity at {config.COMPANY_NAME} - We're Interested in Your Profile!",
            f"{candidate.name}, Your {candidate.job_title} Experience Caught Our Attention",
            f"Perfect Match: {candidate.job_title} Role at {config.COMPANY_NAME}",
            f"We'd Love to Chat - Opportunity at {config.COMPANY_NAME}",
            f"Your Skills in {candidate.skills.split(',')[0] if candidate.skills else 'Tech'} Are Exactly What We Need"
        ]
        
        return [subj for subj in variations if len(subj) <= 78]  # Email subject length limit

def create_sample_candidate() -> CandidateData:
    """Create a sample candidate for testing"""
    return CandidateData(
        name="John Smith",
        email="john.smith@email.com",
        job_title="Software Engineer",
        experience_years="5",
        skills="Python, JavaScript, React",
        location="New York"
    )

# Example usage and testing functions
def test_email_rendering():
    """Test email template rendering"""
    print("=== Testing Email Template System ===\n")
    
    # Create test candidate
    candidate = create_sample_candidate()
    
    # Initialize renderer
    renderer = EmailTemplateRenderer()
    
    # Test email rendering
    print("1. Testing email rendering...")
    email_content = renderer.render_email(candidate)
    print(f"Subject: {email_content['subject']}")
    print(f"Body length: {len(email_content['body'])} characters")
    print("✓ Email rendering successful\n")
    
    # Test email preview
    print("2. Testing email preview...")
    preview = renderer.preview_email(candidate)
    print("✓ Email preview generated\n")
    
    # Test template validation
    print("3. Testing template validation...")
    validation = renderer.validate_template_variables("recruitment_interest")
    print(f"Template valid: {validation['is_valid']}")
    if validation['missing_variables']:
        print(f"Missing variables: {validation['missing_variables']}")
    print("✓ Template validation complete\n")
    
    # Test personalization
    print("4. Testing personalization...")
    personalizer = EmailPersonalizer()
    enhanced_candidate = personalizer.enhance_candidate_data(candidate)
    subject_variations = personalizer.generate_personalized_subject_variations(enhanced_candidate)
    print(f"Generated {len(subject_variations)} subject variations")
    print("✓ Personalization complete\n")
    
    print("=== All Tests Passed ===")

if __name__ == "__main__":
    test_email_rendering()
