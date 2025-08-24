"""
HR Automation - Email Configuration
Updated with user-provided Gmail credentials for direct email sending
"""

import os
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class EmailConfig:
    """Email configuration dataclass"""
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = "ankitatestuser123@gmail.com"
    SMTP_PASSWORD: str = "zrgcvwpqzpvfrele"  # App password
    
    # Company information
    COMPANY_NAME: str = "XYZ"
    COMPANY_WEBSITE: str = "xyz.com"
    
    # HR contact information
    SENDER_NAME: str = "ANKITA"
    HR_CONTACT_NAME: str = "ANKITA"
    HR_CONTACT_EMAIL: str = "ankitatestuser123@gmail.com"
    HR_CONTACT_PHONE: str = "678432198"

# Email templates for different purposes
EMAIL_TEMPLATES = {
    "recruitment_interest": {
        "subject": "Exciting Opportunity at {company_name} - We're Interested in Your Profile!",
        "body": """Dear {candidate_name},

I hope this email finds you well.

We have been through your profile, and I'm pleased to inform you that your profile is well-suited for exciting opportunities we currently have at {company_name}.

Your background in {job_title} with {experience_years} of experience, particularly your expertise in {skills}, aligns perfectly with what we're looking for in our growing team.

We would love to discuss how your talents could contribute to our innovative projects and help drive our company's success. Our team is always looking for passionate professionals who can make a meaningful impact.

If you're interested in exploring new career opportunities, I'd be delighted to schedule a brief call to discuss:
• The exciting projects you would be working on
• Our competitive compensation and benefits package
• Our collaborative and innovative work environment
• Growth opportunities within our organization

Please feel free to reply to this email or contact me directly at {hr_contact_email} or {hr_contact_phone} if you'd like to learn more.

We look forward to the possibility of welcoming you to our team!

Best regards,

{sender_name}
{company_name}
Talent Acquisition Team
Email: {hr_contact_email}
Phone: {hr_contact_phone}
Website: {company_website}

P.S. We believe in creating an inclusive workplace where everyone can thrive. We'd love to hear about your career aspirations and how we can support your professional growth."""
    },
    
    "interview_invitation": {
        "subject": "Interview Invitation - {job_title} Position at {company_name}",
        "body": """Dear {candidate_name},

Thank you for your interest in the {job_title} position at {company_name}. After reviewing your profile and background, we are impressed with your qualifications and would like to invite you for a telephonic interview.

Interview Details:
• Position: {job_title}
• Interview Type: Telephonic Discussion
• Duration: Approximately 30-45 minutes

We will discuss:
• Your professional background and experience
• The role and responsibilities
• Our company culture and values
• Next steps in the process

Please reply to this email with your availability for the next few days, and we will coordinate a suitable time for both of us.

If you have any questions before the interview, please don't hesitate to reach out.

Looking forward to speaking with you soon!

Best regards,

{sender_name}
{company_name}
Talent Acquisition Team
Email: {hr_contact_email}
Phone: {hr_contact_phone}
Website: {company_website}"""
    },
    
    "follow_up": {
        "subject": "Following up - {job_title} Opportunity at {company_name}",
        "body": """Dear {candidate_name},

I hope this email finds you well. I wanted to follow up on our previous communication regarding the {job_title} opportunity at {company_name}.

We remain very interested in your profile and would love to hear from you if you're still considering new career opportunities.

If now is not the right time, we completely understand. However, if you're interested in learning more about this exciting opportunity, please feel free to reach out at your convenience.

We believe your skills in {skills} would be a great addition to our team, and we'd be happy to discuss how this role could align with your career goals.

Thank you for your time, and I look forward to hearing from you.

Best regards,

{sender_name}
{company_name}
Talent Acquisition Team
Email: {hr_contact_email}
Phone: {hr_contact_phone}"""
    }
}

def get_email_config() -> EmailConfig:
    """Get email configuration instance"""
    return EmailConfig()

def get_email_template(template_name: str) -> Dict[str, str]:
    """Get email template by name"""
    if template_name not in EMAIL_TEMPLATES:
        raise ValueError(f"Template '{template_name}' not found. Available templates: {list(EMAIL_TEMPLATES.keys())}")
    
    return EMAIL_TEMPLATES[template_name]

def get_available_templates() -> list:
    """Get list of available email templates"""
    return list(EMAIL_TEMPLATES.keys())

# Test configuration
def test_email_config():
    """Test email configuration"""
    config = get_email_config()
    print("Email Configuration:")
    print(f"SMTP Server: {config.SMTP_SERVER}:{config.SMTP_PORT}")
    print(f"Username: {config.SMTP_USERNAME}")
    print(f"Company: {config.COMPANY_NAME}")
    print(f"Sender: {config.SENDER_NAME}")
    print(f"Available templates: {get_available_templates()}")

if __name__ == "__main__":
    test_email_config()
