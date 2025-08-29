"""
Candidate Auto-Fill Module
Provides interface and logic for automatically filling candidate information
from resume files and LinkedIn profiles
"""

import streamlit as st
import tempfile
import os
from typing import Dict, Optional, Any
import logging

# Import our parsing modules
try:
    from resume_parser import ResumeParser, ParsedCandidate
    RESUME_PARSER_AVAILABLE = True
except ImportError:
    RESUME_PARSER_AVAILABLE = False

try:
    from linkedin_scraper import LinkedInProfileExtractor, LinkedInProfile
    LINKEDIN_SCRAPER_AVAILABLE = True
except ImportError:
    LINKEDIN_SCRAPER_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CandidateAutoFill:
    """Handles auto-fill functionality for candidate forms"""
    
    def __init__(self, gemini_api_key: str = None):
        self.resume_parser = None
        self.linkedin_extractor = None
        self.hybrid_parser = None
        self.gemini_api_key = gemini_api_key
        
        # Initialize traditional parsers if available
        if RESUME_PARSER_AVAILABLE:
            try:
                self.resume_parser = ResumeParser()
            except Exception as e:
                logger.warning(f"Failed to initialize resume parser: {e}")
        
        if LINKEDIN_SCRAPER_AVAILABLE:
            try:
                self.linkedin_extractor = LinkedInProfileExtractor()
            except Exception as e:
                logger.warning(f"Failed to initialize LinkedIn extractor: {e}")
        
        # Initialize hybrid parser with Gemini AI if API key is provided
        if gemini_api_key:
            try:
                from gemini_parser import HybridResumeParser
                self.hybrid_parser = HybridResumeParser(gemini_api_key)
                logger.info("Gemini AI hybrid parser initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini AI parser: {e}")
    
    def render_autofill_interface(self) -> Dict[str, Any]:
        """
        Render the auto-fill interface and return extracted data
        
        Returns:
            Dictionary with extracted candidate information
        """
        st.subheader("🤖 Auto-Fill Options")
        
        # Check availability
        if not RESUME_PARSER_AVAILABLE and not LINKEDIN_SCRAPER_AVAILABLE:
            st.error("❌ Auto-fill modules not available. Please install required dependencies.")
            st.code("pip install PyPDF2 python-docx requests beautifulsoup4")
            return {}
        
        # Auto-fill method selection
        autofill_method = st.radio(
            "Choose auto-fill method:",
            ["📄 Upload Resume", "🔗 LinkedIn Profile URL"],
            horizontal=True
        )
        
        extracted_data = {}
        
        if autofill_method == "📄 Upload Resume":
            extracted_data = self.render_resume_upload()
        elif autofill_method == "🔗 LinkedIn Profile URL":
            extracted_data = self.render_linkedin_input()
        
        return extracted_data
    
    def render_resume_upload(self) -> Dict[str, Any]:
        """Render resume upload interface"""
        if not RESUME_PARSER_AVAILABLE or not self.resume_parser:
            st.error("❌ Resume parser not available")
            st.code("pip install PyPDF2 python-docx spacy")
            return {}
        
        st.write("📄 **Upload Resume File**")
        
        # Show supported file types
        supported_types = self.resume_parser.get_supported_file_types()
        st.info(f"Supported formats: {', '.join(supported_types)}")
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Choose resume file",
            type=[ext[1:] for ext in supported_types],  # Remove dot from extensions
            help="Upload a resume in PDF, DOCX, or TXT format"
        )
        
        if uploaded_file is not None:
            # Show file details
            file_details = {
                "Filename": uploaded_file.name,
                "File size": f"{uploaded_file.size:,} bytes",
                "File type": uploaded_file.type
            }
            
            with st.expander("📋 File Details", expanded=True):
                for key, value in file_details.items():
                    st.write(f"**{key}:** {value}")
            
            # Process button
            if st.button("🚀 Extract Information from Resume", type="primary"):
                return self.process_resume_file(uploaded_file)
        
        return {}
    
    def render_linkedin_input(self) -> Dict[str, Any]:
        """Render LinkedIn URL input interface"""
        if not LINKEDIN_SCRAPER_AVAILABLE or not self.linkedin_extractor:
            st.error("❌ LinkedIn scraper not available")
            st.code("pip install requests beautifulsoup4 selenium")
            return {}
        
        st.write("🔗 **LinkedIn Profile URL**")
        
        # LinkedIn URL input
        linkedin_url = st.text_input(
            "LinkedIn Profile URL",
            placeholder="e.g., https://linkedin.com/in/johndoe",
            help="Enter the candidate's LinkedIn profile URL"
        )
        
        if linkedin_url:
            # Validate URL format
            if self.linkedin_extractor.scraper.is_valid_linkedin_url(linkedin_url):
                st.success("✅ Valid LinkedIn URL format")
                
                # Show available extraction methods
                available_methods = self.linkedin_extractor.get_available_methods()
                st.info(f"Available extraction methods: {', '.join(available_methods)}")
                
                # Process button
                if st.button("🚀 Extract Information from LinkedIn", type="primary"):
                    return self.process_linkedin_url(linkedin_url)
            else:
                st.error("❌ Invalid LinkedIn URL format. Please use format: https://linkedin.com/in/username")
        
        return {}
    
    def process_resume_file(self, uploaded_file) -> Dict[str, Any]:
        """Process uploaded resume file and extract information"""
        try:
            with st.spinner("🔍 Extracting information from resume..."):
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_file_path = tmp_file.name
                
                try:
                    # First extract raw text from the file
                    if self.resume_parser:
                        # Get file extension
                        file_ext = os.path.splitext(uploaded_file.name)[1].lower()
                        
                        # Extract text based on file type
                        if file_ext == '.pdf':
                            raw_text = self.resume_parser.extract_text_from_pdf(tmp_file_path)
                        elif file_ext == '.docx':
                            raw_text = self.resume_parser.extract_text_from_docx(tmp_file_path)
                        elif file_ext in ['.txt', '.text']:
                            raw_text = self.resume_parser.extract_text_from_txt(tmp_file_path)
                        else:
                            raw_text = ""
                        
                        # Use Gemini AI parser if available, otherwise fall back to traditional
                        if self.hybrid_parser and raw_text:
                            result = self.hybrid_parser.parse_resume(raw_text, use_gemini=True)
                            
                            if result['success']:
                                extracted_data = result['data']
                                parsing_method = result['method']
                                issues = result.get('issues', {})
                                
                                # Show parsing method used
                                if parsing_method == 'gemini':
                                    st.success("🤖 Using Gemini AI for intelligent data categorization...")
                                    # Display any data quality issues found
                                    if issues:
                                        with st.expander("⚠️ Data Quality Checks", expanded=False):
                                            for field, field_issues in issues.items():
                                                if field_issues:
                                                    st.warning(f"**{field.title()}:** {'; '.join(field_issues)}")
                                elif parsing_method == 'traditional':
                                    st.info("🔄 Used traditional parsing (Gemini AI unavailable)")
                            else:
                                st.error("❌ Both AI and traditional parsing failed")
                                return {}
                        else:
                            # Traditional parsing only
                            st.info("🔄 Using traditional resume parsing...")
                            parsed_candidate = self.resume_parser.parse_resume_file(tmp_file_path)
                            
                            # Convert to dictionary format
                            extracted_data = {
                                'full_name': parsed_candidate.full_name,
                                'email': parsed_candidate.email,
                                'linkedin_url': parsed_candidate.linkedin_url,
                                'company': parsed_candidate.current_company,
                                'position': parsed_candidate.current_position,
                                'location': parsed_candidate.location,
                                'skills': ', '.join(parsed_candidate.skills) if parsed_candidate.skills else '',
                                'experience_summary': parsed_candidate.experience_summary,
                                'phone': parsed_candidate.phone,
                                'total_experience': parsed_candidate.total_experience,
                                'education': ' | '.join(parsed_candidate.education) if parsed_candidate.education else ''
                            }
                    
                    # Clean empty values
                    extracted_data = {k: v for k, v in extracted_data.items() if v}
                    
                    if extracted_data:
                        st.success(f"✅ Successfully extracted information from {uploaded_file.name}")
                        self.show_extracted_data(extracted_data, "Resume")
                        return extracted_data
                    else:
                        st.warning("⚠️ No information could be extracted from the resume. Please check the file format and content.")
                        return {}
                
                finally:
                    # Clean up temporary file
                    try:
                        os.unlink(tmp_file_path)
                    except:
                        pass
        
        except Exception as e:
            st.error(f"❌ Error processing resume: {str(e)}")
            return {}
    
    def process_linkedin_url(self, linkedin_url: str) -> Dict[str, Any]:
        """Process LinkedIn URL and extract information"""
        try:
            with st.spinner("🔍 Extracting information from LinkedIn profile..."):
                # Extract profile information
                profile = self.linkedin_extractor.extract_profile(linkedin_url)
                
                # Convert to dictionary format
                extracted_data = {
                    'full_name': profile.full_name,
                    'linkedin_url': profile.linkedin_url,
                    'company': profile.current_company,
                    'position': profile.current_position or profile.headline,
                    'location': profile.location,
                    'skills': ', '.join(profile.skills) if profile.skills else '',
                    'experience_summary': profile.about[:300] if profile.about else ''
                }
                
                # Clean empty values
                extracted_data = {k: v for k, v in extracted_data.items() if v}
                
                if extracted_data and extracted_data.get('full_name'):
                    st.success(f"✅ Successfully extracted information from LinkedIn profile")
                    self.show_extracted_data(extracted_data, "LinkedIn")
                    return extracted_data
                else:
                    # Fallback to basic URL extraction
                    basic_info = self.linkedin_extractor.extract_basic_info_from_url(linkedin_url)
                    if basic_info.get('full_name'):
                        st.warning("⚠️ Limited information extracted. LinkedIn blocks most scraping attempts.")
                        st.info("💡 You can manually fill in additional details below.")
                        self.show_extracted_data(basic_info, "LinkedIn (Basic)")
                        return basic_info
                    else:
                        st.warning("⚠️ Unable to extract information from LinkedIn profile. This is common due to LinkedIn's anti-scraping measures.")
                        st.info("💡 You can manually enter the information below.")
                        return {'linkedin_url': linkedin_url}
        
        except Exception as e:
            st.error(f"❌ Error processing LinkedIn profile: {str(e)}")
            return {'linkedin_url': linkedin_url}
    
    def show_extracted_data(self, data: Dict[str, Any], source: str):
        """Display extracted data in a nice format"""
        st.subheader(f"📊 Extracted Information from {source}")
        
        with st.expander("👁️ View Extracted Data", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                if data.get('full_name'):
                    st.write(f"**👤 Name:** {data['full_name']}")
                if data.get('email'):
                    st.write(f"**📧 Email:** {data['email']}")
                if data.get('phone'):
                    st.write(f"**📞 Phone:** {data['phone']}")
                if data.get('linkedin_url'):
                    st.write(f"**🔗 LinkedIn:** [Profile]({data['linkedin_url']})")
            
            with col2:
                if data.get('company'):
                    st.write(f"**🏢 Company:** {data['company']}")
                if data.get('position'):
                    st.write(f"**💼 Position:** {data['position']}")
                if data.get('location'):
                    st.write(f"**📍 Location:** {data['location']}")
                if data.get('total_experience'):
                    st.write(f"**⏱️ Experience:** {data['total_experience']}")
            
            if data.get('skills'):
                st.write(f"**🔧 Skills:** {data['skills']}")
            
            if data.get('experience_summary'):
                st.write(f"**📝 Experience Summary:** {data['experience_summary'][:200]}{'...' if len(data['experience_summary']) > 200 else ''}")
            
            if data.get('education'):
                st.write(f"**🎓 Education:** {data['education']}")
        
        st.success("💡 Review the extracted information and modify as needed before saving.")
    
    def merge_with_form_data(self, extracted_data: Dict[str, Any], form_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge extracted data with manually entered form data
        Form data takes precedence over extracted data
        """
        merged_data = extracted_data.copy()
        
        # Override with form data where provided
        for key, value in form_data.items():
            if value and str(value).strip():  # Only use non-empty form values
                merged_data[key] = value
        
        return merged_data
    
    def get_status_info(self) -> Dict[str, str]:
        """Get status information about available auto-fill methods"""
        status = {
            "Resume Parser": "❌ Not Available",
            "LinkedIn Scraper": "❌ Not Available"
        }
        
        if RESUME_PARSER_AVAILABLE and self.resume_parser:
            supported_types = self.resume_parser.get_supported_file_types()
            status["Resume Parser"] = f"✅ Available ({', '.join(supported_types)})"
        
        if LINKEDIN_SCRAPER_AVAILABLE and self.linkedin_extractor:
            methods = self.linkedin_extractor.get_available_methods()
            status["LinkedIn Scraper"] = f"✅ Available ({', '.join(methods)})"
        
        return status

def render_dependency_help():
    """Render help for installing missing dependencies"""
    st.subheader("📦 Setup Auto-Fill Dependencies")
    
    st.write("To enable auto-fill functionality, install the following packages:")
    
    # Resume parsing dependencies
    st.write("**For Resume Parsing:**")
    st.code("pip install PyPDF2 python-docx spacy")
    st.code("python -m spacy download en_core_web_sm")
    
    # LinkedIn scraping dependencies
    st.write("**For LinkedIn Profile Extraction:**")
    st.code("pip install requests beautifulsoup4 selenium")
    
    st.warning("⚠️ **Note about LinkedIn Scraping:**")
    st.write("""
    LinkedIn actively blocks automated scraping to protect user privacy. 
    The LinkedIn extraction feature may have limited success and is provided 
    as a convenience tool. For production use, consider:
    
    1. **LinkedIn API Integration**: Official API access (requires approval)
    2. **Manual Entry**: Use the manual form for reliable data entry
    3. **Resume Upload**: More reliable than LinkedIn scraping
    """)

def test_autofill_functionality():
    """Test function for the auto-fill functionality"""
    if 'autofill_test_mode' not in st.session_state:
        st.session_state.autofill_test_mode = False
    
    st.subheader("🧪 Test Auto-Fill Functionality")
    
    if st.button("🧪 Enable Test Mode"):
        st.session_state.autofill_test_mode = True
    
    if st.session_state.autofill_test_mode:
        autofill = CandidateAutoFill()
        
        # Show status
        st.write("**📊 Auto-Fill Status:**")
        status_info = autofill.get_status_info()
        for service, status in status_info.items():
            st.write(f"  • {service}: {status}")
        
        # Test interface
        st.write("**🎯 Test Interface:**")
        extracted_data = autofill.render_autofill_interface()
        
        if extracted_data:
            st.write("**✅ Extracted Data:**")
            st.json(extracted_data)

# Utility functions for integration
def create_candidate_from_extracted_data(extracted_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert extracted data to candidate format for database"""
    candidate_data = {}
    
    # Map extracted fields to database fields
    field_mapping = {
        'full_name': 'full_name',
        'email': 'email',
        'linkedin_url': 'linkedin_url',
        'company': 'company',
        'position': 'position',
        'location': 'location',
        'skills': 'skills',
        'experience_summary': 'experience_summary',
        'phone': 'phone',  # Additional field not in original schema
        'total_experience': 'total_experience',  # Additional field
        'education': 'education'  # Additional field
    }
    
    for extracted_key, db_key in field_mapping.items():
        value = extracted_data.get(extracted_key, '')
        if value and str(value).strip():
            candidate_data[db_key] = str(value).strip()
    
    return candidate_data

def validate_extracted_data(data: Dict[str, Any]) -> tuple:
    """
    Validate extracted candidate data
    
    Returns:
        (is_valid: bool, error_messages: List[str])
    """
    errors = []
    
    # Check required fields
    if not data.get('full_name', '').strip():
        errors.append("Full name is required")
    
    if not data.get('linkedin_url', '').strip():
        errors.append("LinkedIn URL is required")
    
    # Validate email format if provided
    email = data.get('email', '').strip()
    if email:
        import re
        email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        if not email_pattern.match(email):
            errors.append("Invalid email format")
    
    # Validate LinkedIn URL format
    linkedin_url = data.get('linkedin_url', '').strip()
    if linkedin_url:
        if not linkedin_url.startswith(('http://', 'https://')):
            errors.append("LinkedIn URL must start with http:// or https://")
        elif 'linkedin.com' not in linkedin_url.lower():
            errors.append("Must be a valid LinkedIn URL")
    
    return len(errors) == 0, errors

if __name__ == "__main__":
    # This would be called from Streamlit app
    print("Auto-Fill Module Test")
    
    # Test dependency availability
    print(f"Resume Parser Available: {RESUME_PARSER_AVAILABLE}")
    print(f"LinkedIn Scraper Available: {LINKEDIN_SCRAPER_AVAILABLE}")
    
    if RESUME_PARSER_AVAILABLE:
        parser = ResumeParser()
        print(f"Supported resume types: {parser.get_supported_file_types()}")
    
    if LINKEDIN_SCRAPER_AVAILABLE:
        extractor = LinkedInProfileExtractor()
        print(f"Available LinkedIn methods: {extractor.get_available_methods()}")
    
    # Test validation
    test_data = {
        'full_name': 'John Doe',
        'email': 'john@example.com',
        'linkedin_url': 'https://linkedin.com/in/johndoe'
    }
    
    is_valid, errors = validate_extracted_data(test_data)
    print(f"Test data validation: {'✅ Valid' if is_valid else '❌ Invalid'}")
    if errors:
        print(f"Errors: {errors}")
