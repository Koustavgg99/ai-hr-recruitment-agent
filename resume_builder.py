"""
Resume Builder Module - Final Version
Perfect Batpharma template matching with robust parsing and Streamlit integration
"""

import os
import io
import re
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import tempfile
import logging
from pathlib import Path

# PDF and document processing
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib import colors
    from reportlab.lib.colors import HexColor
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
    from reportlab.pdfgen import canvas
    from reportlab.platypus.flowables import Flowable
    REPORTLAB_AVAILABLE = True
except ImportError as e:
    REPORTLAB_AVAILABLE = False
    print(f"ReportLab not available: {e}")

# Import existing parsers
try:
    from resume_parser import ResumeParser, ParsedCandidate
    RESUME_PARSER_AVAILABLE = True
except ImportError:
    RESUME_PARSER_AVAILABLE = False
    print("Traditional resume parser not available")

try:
    from gemini_parser import HybridResumeParser
    GEMINI_PARSER_AVAILABLE = True
except ImportError:
    GEMINI_PARSER_AVAILABLE = False
    print("Hybrid/Gemini parser not available")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BatpharmaTemplate:
    """Handles EXACT Batpharma template formatting matching the original"""
    
    @staticmethod
    def create_page_template(canvas, doc):
        """Create page with exact Batpharma signature placement based on original template analysis"""
        canvas.saveState()
        
        # Based on template analysis: BATPHARMA appears around bottom right area
        # Original template coordinates show signature area around (416.8, 673.8) to (595.5, 842.2)
        page_width = A4[0]   # 595.5 points
        page_height = A4[1]  # 842.25 points
        
        # Position signature exactly like the original template
        # From analysis: text appears in bottom section
        sig_x = page_width - 90  # 90 points from right edge
        sig_y = 30               # 30 points from bottom
        
        # Draw "BATPHARMA" signature in company blue color
        canvas.setFont("Helvetica-Bold", 8)
        canvas.setFillColor(HexColor('#2E86AB'))
        canvas.drawString(sig_x, sig_y, "BATPHARMA")
        
        # Draw decorative line above signature (like original)
        canvas.setStrokeColor(HexColor('#2E86AB'))
        canvas.setLineWidth(0.8)
        canvas.line(sig_x, sig_y - 3, sig_x + 55, sig_y - 3)
        
        canvas.restoreState()

class ResumeExtractor:
    """Handles text extraction using existing proven parser methods"""
    
    def __init__(self):
        if RESUME_PARSER_AVAILABLE:
            self.parser = ResumeParser()
        else:
            self.parser = None
    
    def extract_text(self, file_content: bytes, filename: str) -> str:
        """Extract text using existing parser system"""
        if not self.parser:
            raise ImportError("Resume parser not available. Please ensure resume_parser.py is available.")
        
        file_extension = Path(filename).suffix.lower()
        
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
                tmp_file.write(file_content)
                tmp_file_path = tmp_file.name
            
            # Use existing parser methods
            if file_extension == '.pdf':
                text = self.parser.extract_text_from_pdf(tmp_file_path)
            elif file_extension in ['.docx', '.doc']:
                text = self.parser.extract_text_from_docx(tmp_file_path)
            elif file_extension == '.txt':
                text = self.parser.extract_text_from_txt(tmp_file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
            
            # Clean up
            os.unlink(tmp_file_path)
            return text
            
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            try:
                os.unlink(tmp_file_path)
            except:
                pass
            raise

class ResumeDataParser:
    """Parses resume text using existing hybrid parser system for maximum accuracy"""
    
    def __init__(self, gemini_api_key: Optional[str] = None):
        self.gemini_api_key = gemini_api_key
        
        # Initialize hybrid parser (Gemini + traditional)
        if GEMINI_PARSER_AVAILABLE and gemini_api_key:
            try:
                self.hybrid_parser = HybridResumeParser(gemini_api_key)
                logger.info("Initialized hybrid parser with Gemini AI")
            except Exception as e:
                logger.warning(f"Failed to initialize hybrid parser: {e}")
                self.hybrid_parser = None
        else:
            self.hybrid_parser = None
        
        # Initialize traditional parser as fallback
        if RESUME_PARSER_AVAILABLE:
            try:
                self.traditional_parser = ResumeParser()
                logger.info("Initialized traditional parser as fallback")
            except Exception as e:
                logger.warning(f"Failed to initialize traditional parser: {e}")
                self.traditional_parser = None
        else:
            self.traditional_parser = None
    
    def parse_resume_text(self, text: str) -> Dict[str, Any]:
        """Parse resume text using existing parser system"""
        
        # Try hybrid parser first (includes Gemini AI)
        if self.hybrid_parser:
            try:
                logger.info("Using hybrid parser (Gemini AI + traditional)")
                result = self.hybrid_parser.parse_resume(text, use_gemini=True)
                
                if result['success']:
                    data = result['data']
                    logger.info(f"Parsing successful using {result['method']} method")
                    
                    # Convert to standardized format
                    return {
                        'full_name': data.get('full_name', 'Unknown Candidate'),
                        'email': data.get('email', ''),
                        'phone': data.get('phone', ''),
                        'current_company': data.get('company', ''),
                        'current_position': data.get('position', ''),
                        'experience_years': self._extract_years(data.get('total_experience', '')),
                        'skills': self._clean_skills(data.get('skills', '')),
                        'summary': data.get('experience_summary', 'Experienced professional with diverse background.'),
                        'education': self._clean_education(data.get('education', '')),
                        'certifications': self._clean_skills(data.get('certifications', '')),
                        'languages': self._clean_skills(data.get('languages', '')),
                        'location': data.get('location', ''),
                        'linkedin_url': data.get('linkedin_url', ''),
                        'parsing_method': result['method'],
                        'parsing_issues': result.get('issues', []),
                        'processed_at': datetime.now().isoformat()
                    }
                else:
                    logger.warning("Hybrid parser failed, trying traditional parser only")
            except Exception as e:
                logger.error(f"Hybrid parser error: {e}")
        
        # Fallback to traditional parser only
        if self.traditional_parser:
            try:
                logger.info("Using traditional parser")
                result = self.traditional_parser.parse_text(text)
                
                return {
                    'full_name': result.full_name or 'Unknown Candidate',
                    'email': result.email or '',
                    'phone': result.phone or '',
                    'current_company': result.current_company or '',
                    'current_position': result.current_position or '',
                    'experience_years': self._extract_years(result.total_experience),
                    'skills': result.skills or [],
                    'summary': result.experience_summary or 'Experienced professional with diverse background.',
                    'education': result.education or [],
                    'certifications': [],
                    'languages': [],
                    'location': result.location or '',
                    'linkedin_url': result.linkedin_url or '',
                    'parsing_method': 'traditional',
                    'parsing_issues': [],
                    'processed_at': datetime.now().isoformat()
                }
            except Exception as e:
                logger.error(f"Traditional parser error: {e}")
        
        # Last resort: return minimal data
        logger.warning("All parsers failed, returning minimal data")
        return {
            'full_name': 'Unknown Candidate',
            'email': '',
            'phone': '',
            'current_company': '',
            'current_position': '',
            'experience_years': 0,
            'skills': [],
            'summary': 'Professional candidate.',
            'education': [],
            'certifications': [],
            'languages': [],
            'location': '',
            'linkedin_url': '',
            'parsing_method': 'failed',
            'parsing_issues': ['All parsing methods failed'],
            'processed_at': datetime.now().isoformat()
        }
    
    def _extract_years(self, exp_text: str) -> int:
        """Extract experience years from text"""
        if not exp_text:
            return 0
        
        pattern = re.compile(r'(\d+)\+?\s*years?', re.IGNORECASE)
        match = pattern.search(str(exp_text))
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                return 0
        return 0
    
    def _clean_skills(self, skills_data) -> List[str]:
        """Clean skills data into list format"""
        if not skills_data:
            return []
        
        if isinstance(skills_data, list):
            return [skill.strip() for skill in skills_data if skill and skill.strip()][:15]
        
        if isinstance(skills_data, str):
            skills = [skill.strip() for skill in skills_data.split(',') if skill.strip()]
            return skills[:15]
        
        return []
    
    def _clean_education(self, education_data) -> List[str]:
        """Clean education data into list format"""
        if not education_data:
            return []
        
        if isinstance(education_data, list):
            return [edu.strip() for edu in education_data if edu and edu.strip()][:3]
        
        if isinstance(education_data, str):
            education = [edu.strip() for edu in education_data.replace('|', '\n').split('\n') if edu.strip()]
            return education[:3]
        
        return []

class ExactBatpharmaPDFGenerator:
    """Generates PDF resumes matching EXACTLY the Batpharma template format"""
    
    def __init__(self):
        if not REPORTLAB_AVAILABLE:
            raise ImportError("ReportLab not available. Install with: pip install reportlab")
        
        self.setup_exact_styles()
    
    def setup_exact_styles(self):
        """Setup styles that exactly match the Batpharma template layout"""
        self.styles = getSampleStyleSheet()
        
        # EXACT match to template: Large name at top (DANIEL GALLEGO position: 34.7, 47.1)
        self.styles.add(ParagraphStyle(
            name='BatpharmaExactName',
            parent=self.styles['Normal'],
            fontSize=26,
            fontName='Helvetica-Bold',
            spaceAfter=6,
            spaceBefore=30,
            alignment=TA_LEFT,
            textColor=colors.black,
            leftIndent=35  # Match template left margin
        ))
        
        # Position/title below name (UX DESIGNER position: 62.8, 84.8)
        self.styles.add(ParagraphStyle(
            name='BatpharmaExactTitle',
            parent=self.styles['Normal'],
            fontSize=14,
            fontName='Helvetica',
            spaceAfter=12,
            alignment=TA_LEFT,
            textColor=colors.black,
            leftIndent=35
        ))
        
        # Contact info (hello@reallygreatsite.com position around 40.4, 108.5)
        self.styles.add(ParagraphStyle(
            name='BatpharmaExactContact',
            parent=self.styles['Normal'],
            fontSize=10,
            fontName='Helvetica',
            spaceAfter=20,
            alignment=TA_LEFT,
            textColor=colors.black,
            leftIndent=35
        ))
        
        # Section headings in blue (SUMMARY position: 52.8, 147.3)
        self.styles.add(ParagraphStyle(
            name='BatpharmaExactSection',
            parent=self.styles['Normal'],
            fontSize=12,
            fontName='Helvetica-Bold',
            spaceAfter=6,
            spaceBefore=12,
            alignment=TA_LEFT,
            textColor=HexColor('#2E86AB'),
            leftIndent=35
        ))
        
        # Content text (body text style)
        self.styles.add(ParagraphStyle(
            name='BatpharmaExactContent',
            parent=self.styles['Normal'],
            fontSize=10,
            fontName='Helvetica',
            spaceAfter=6,
            alignment=TA_LEFT,
            textColor=colors.black,
            leftIndent=35
        ))
        
        # Skills list (indented like template skills at 36.2, 275.7)
        self.styles.add(ParagraphStyle(
            name='BatpharmaExactSkills',
            parent=self.styles['Normal'],
            fontSize=10,
            fontName='Helvetica',
            spaceAfter=3,
            alignment=TA_LEFT,
            textColor=colors.black,
            leftIndent=55  # More indented for skills
        ))
    
    def generate_pdf(self, resume_data: Dict[str, Any]) -> bytes:
        """Generate PDF matching EXACTLY the Batpharma template"""
        buffer = io.BytesIO()
        
        # Use exact A4 size from template analysis (595.5 x 842.25 points)
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=50,
            leftMargin=35,  # Match template left margin exactly
            topMargin=40,   # Match template top spacing
            bottomMargin=60  # Space for signature
        )
        
        story = []
        
        # === HEADER SECTION - EXACT MATCH TO TEMPLATE ===
        # Large name (matching DANIEL GALLEGO position)
        name = resume_data.get('full_name', 'UNKNOWN CANDIDATE').upper()
        story.append(Paragraph(name, self.styles['BatpharmaExactName']))
        
        # Job title below name (matching UX DESIGNER position)  
        position = resume_data.get('current_position', 'PROFESSIONAL').upper()
        story.append(Paragraph(position, self.styles['BatpharmaExactTitle']))
        
        # Contact information (matching template contact layout)
        contact_parts = []
        if resume_data.get('email'):
            contact_parts.append(resume_data['email'])
        if resume_data.get('linkedin_url'):
            linkedin_clean = resume_data['linkedin_url'].replace('https://', '').replace('http://', '')
            contact_parts.append(linkedin_clean)
        elif resume_data.get('phone'):
            contact_parts.append(resume_data['phone'])
        
        if contact_parts:
            contact_text = " | ".join(contact_parts)
            story.append(Paragraph(contact_text, self.styles['BatpharmaExactContact']))
        
        # === SUMMARY SECTION (matching template SUMMARY position) ===
        story.append(Paragraph("SUMMARY", self.styles['BatpharmaExactSection']))
        summary_text = resume_data.get('summary', 'Professional with experience across various technologies and methodologies.')
        story.append(Paragraph(summary_text, self.styles['BatpharmaExactContent']))
        story.append(Spacer(1, 6))
        
        # === TECHNICAL SKILLS SECTION (matching template layout) ===
        if resume_data.get('skills'):
            story.append(Paragraph("TECHNICAL SKILLS", self.styles['BatpharmaExactSection']))
            
            skills = resume_data['skills'] if isinstance(resume_data['skills'], list) else []
            if not skills and resume_data.get('skills'):
                skills = [s.strip() for s in str(resume_data['skills']).split(',')]
            
            # Display skills in left column format exactly like template
            for skill in skills[:9]:  # Match template skill count
                if skill.strip():
                    story.append(Paragraph(skill.strip(), self.styles['BatpharmaExactSkills']))
            
            story.append(Spacer(1, 8))
        
        # === PROFESSIONAL EXPERIENCE SECTION ===
        story.append(Paragraph("PROFESSIONAL EXPERIENCE", self.styles['BatpharmaExactSection']))
        
        if resume_data.get('current_position') and resume_data.get('current_company'):
            # Job title and company (like template format)
            job_title = f"{resume_data['current_position']}, {resume_data['current_company']}"
            story.append(Paragraph(job_title, self.styles['BatpharmaExactContent']))
            
            # Experience bullet points (matching template bullet style)
            if resume_data.get('summary'):
                summary_sentences = resume_data['summary'].split('. ')
                for sentence in summary_sentences[:3]:  # Limit to 3 bullets
                    if sentence.strip() and len(sentence.strip()) > 10:
                        clean_sentence = sentence.strip().rstrip('.')
                        story.append(Paragraph(f"• {clean_sentence}.", self.styles['BatpharmaExactContent']))
        else:
            # Fallback experience section
            story.append(Paragraph("Professional Experience Available", self.styles['BatpharmaExactContent']))
            if resume_data.get('summary'):
                story.append(Paragraph(f"• {resume_data['summary']}", self.styles['BatpharmaExactContent']))
        
        story.append(Spacer(1, 8))
        
        # === EDUCATION SECTION ===
        if resume_data.get('education'):
            story.append(Paragraph("EDUCATION", self.styles['BatpharmaExactSection']))
            
            education = resume_data['education'] if isinstance(resume_data['education'], list) else [resume_data['education']]
            for edu in education:
                if edu and edu.strip():
                    story.append(Paragraph(edu.strip(), self.styles['BatpharmaExactContent']))
        
        story.append(Spacer(1, 8))
        
        # === ADDITIONAL INFORMATION SECTION ===
        story.append(Paragraph("ADDITIONAL INFORMATION", self.styles['BatpharmaExactSection']))
        
        # Languages (matching template format)
        languages = resume_data.get('languages', [])
        if languages and isinstance(languages, list) and any(languages):
            lang_text = f"Languages: {', '.join([lang for lang in languages if lang.strip()])}"
            story.append(Paragraph(lang_text, self.styles['BatpharmaExactContent']))
        
        # Certifications
        certifications = resume_data.get('certifications', [])
        if certifications and isinstance(certifications, list) and any(certifications):
            cert_text = f"Certifications: {', '.join([cert for cert in certifications if cert.strip()])}"
            story.append(Paragraph(cert_text, self.styles['BatpharmaExactContent']))
        
        # Total experience
        if resume_data.get('experience_years'):
            exp_text = f"Total Experience: {resume_data['experience_years']} years"
            story.append(Paragraph(exp_text, self.styles['BatpharmaExactContent']))
        
        # Build PDF with exact Batpharma template
        doc.build(story, onFirstPage=BatpharmaTemplate.create_page_template, onLaterPages=BatpharmaTemplate.create_page_template)
        
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes

class ResumeBuilder:
    """Main resume builder with exact Batpharma template matching and robust parsing"""
    
    def __init__(self, gemini_api_key: Optional[str] = None):
        self.extractor = ResumeExtractor()
        self.parser = ResumeDataParser(gemini_api_key)
        
        if REPORTLAB_AVAILABLE:
            self.pdf_generator = ExactBatpharmaPDFGenerator()
        else:
            self.pdf_generator = None
            logger.error("ReportLab not available for PDF generation")
        
        # Create generated resumes directory
        self.generated_dir = Path('generated_resumes')
        self.generated_dir.mkdir(exist_ok=True)
        
        self.gemini_api_key = gemini_api_key
        
        # Log initialization status
        logger.info(f"Resume Builder initialized:")
        logger.info(f"  - Traditional parser: {RESUME_PARSER_AVAILABLE}")
        logger.info(f"  - Gemini parser: {GEMINI_PARSER_AVAILABLE and bool(gemini_api_key)}")
        logger.info(f"  - ReportLab: {REPORTLAB_AVAILABLE}")
    
    def get_supported_formats(self) -> List[str]:
        """Get supported file formats"""
        return ['.pdf', '.docx', '.doc', '.txt']
    
    def validate_file(self, file_content: bytes, filename: str) -> Tuple[bool, str]:
        """Validate uploaded file"""
        file_extension = Path(filename).suffix.lower()
        
        if file_extension not in self.get_supported_formats():
            return False, f"Unsupported format. Supported: {', '.join(self.get_supported_formats())}"
        
        if len(file_content) == 0:
            return False, "File is empty"
        
        if len(file_content) > 10 * 1024 * 1024:  # 10MB limit
            return False, "File too large (max 10MB)"
        
        return True, "File is valid"
    
    def process_resume(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Process resume using existing parser system"""
        # Validate file first
        is_valid, message = self.validate_file(file_content, filename)
        if not is_valid:
            raise ValueError(f"File validation failed: {message}")
        
        try:
            # Extract text using existing system
            logger.info(f"Processing resume: {filename}")
            extracted_text = self.extractor.extract_text(file_content, filename)
            
            if not extracted_text.strip():
                raise ValueError("Could not extract any text from the file")
            
            logger.info(f"Extracted {len(extracted_text)} characters of text")
            
            # Parse using existing parser system
            parsed_data = self.parser.parse_resume_text(extracted_text)
            
            # Add metadata
            parsed_data['original_filename'] = filename
            parsed_data['file_size'] = len(file_content)
            parsed_data['text_length'] = len(extracted_text)
            
            logger.info(f"Successfully parsed resume for: {parsed_data.get('full_name', 'Unknown')}")
            return parsed_data
            
        except Exception as e:
            logger.error(f"Resume processing failed: {e}")
            raise
    
    def generate_resume_pdf(self, resume_data: Dict[str, Any], candidate_name: str = None) -> Tuple[bytes, str]:
        """Generate PDF in EXACT Batpharma template format"""
        if not self.pdf_generator:
            raise ImportError("PDF generator not available. Install reportlab: pip install reportlab")
        
        try:
            # Generate PDF using exact Batpharma template
            logger.info("Generating PDF with EXACT Batpharma template")
            pdf_bytes = self.pdf_generator.generate_pdf(resume_data)
            
            # Create filename
            name = candidate_name or resume_data.get('full_name', 'Unknown')
            safe_name = re.sub(r'[^\w\s-]', '', name).strip().replace(' ', '_')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{safe_name}_Batpharma_Resume_{timestamp}.pdf"
            
            # Save to generated resumes directory
            file_path = self.generated_dir / filename
            with open(file_path, 'wb') as f:
                f.write(pdf_bytes)
            
            logger.info(f"Generated exact Batpharma resume: {filename} ({len(pdf_bytes)} bytes)")
            return pdf_bytes, filename
            
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            raise
    
    def get_generated_resumes(self) -> List[Dict[str, Any]]:
        """Get list of generated resumes"""
        resumes = []
        
        if self.generated_dir.exists():
            for file_path in self.generated_dir.glob('*.pdf'):
                stat = file_path.stat()
                
                resumes.append({
                    'filename': file_path.name,
                    'path': str(file_path),
                    'size': stat.st_size,
                    'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        
        # Sort by creation time (newest first)
        resumes.sort(key=lambda x: x['created'], reverse=True)
        return resumes
    
    def delete_resume(self, filename: str) -> bool:
        """Delete a generated resume file"""
        try:
            file_path = self.generated_dir / filename
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Deleted resume: {filename}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete {filename}: {e}")
            return False
    
    def get_resume_data_from_file(self, filename: str) -> Optional[bytes]:
        """Get resume PDF bytes from filename"""
        try:
            file_path = self.generated_dir / filename
            if file_path.exists():
                return file_path.read_bytes()
            return None
        except Exception as e:
            logger.error(f"Failed to read {filename}: {e}")
            return None

# Utility functions for Streamlit integration
def get_resume_builder(gemini_api_key: Optional[str] = None) -> ResumeBuilder:
    """Get configured resume builder instance"""
    return ResumeBuilder(gemini_api_key)

def check_dependencies() -> Tuple[bool, List[str]]:
    """Check if all dependencies are available"""
    missing_deps = []
    
    if not REPORTLAB_AVAILABLE:
        missing_deps.append("reportlab")
    
    if not RESUME_PARSER_AVAILABLE:
        missing_deps.append("resume_parser module")
    
    return len(missing_deps) == 0, missing_deps

def check_pdf_dependencies() -> Tuple[bool, List[str]]:
    """Check PDF processing dependencies for Streamlit compatibility"""
    missing_deps = []
    
    # Check core PDF libraries
    try:
        import reportlab
    except ImportError:
        missing_deps.append("reportlab")
    
    try:
        import PyPDF2
    except ImportError:
        missing_deps.append("PyPDF2")
    
    try:
        import fitz  # PyMuPDF
    except ImportError:
        missing_deps.append("PyMuPDF")
    
    try:
        from docx import Document
    except ImportError:
        missing_deps.append("python-docx")
    
    return len(missing_deps) == 0, missing_deps

# Test function
def test_exact_resume_builder():
    """Test the exact Batpharma resume builder functionality"""
    print("🧪 Testing EXACT Batpharma Resume Builder...")
    
    # Check dependencies
    available, missing = check_dependencies()
    if not available:
        print(f"❌ Missing dependencies: {missing}")
        return False
    
    print("✅ All dependencies available")
    
    try:
        # Test initialization
        builder = ResumeBuilder()
        print("✅ Resume builder initialized successfully")
        
        # Test PDF generation with sample data matching template format
        sample_data = {
            'full_name': 'Daniel Martinez',
            'email': 'daniel.martinez@batpharma.com',
            'phone': '(555) 789-0123',
            'current_position': 'Senior Software Engineer',
            'current_company': 'Batpharma Technologies',
            'skills': [
                'Python', 'JavaScript', 'React', 'Node.js', 
                'AWS', 'Docker', 'PostgreSQL', 'Git', 'Agile'
            ],
            'summary': 'Senior Software Engineer with 7 years experience in full-stack development and cloud architecture. Expert in modern web technologies and scalable system design. Proven track record of leading development teams and delivering high-quality software solutions.',
            'education': ['Master of Science in Computer Science - MIT', 'Bachelor of Engineering - Stanford University'],
            'experience_years': 7,
            'certifications': ['AWS Solutions Architect', 'Certified Kubernetes Administrator'],
            'languages': ['English', 'Spanish', 'Portuguese']
        }
        
        # Generate test PDF with exact Batpharma formatting
        pdf_bytes, filename = builder.generate_resume_pdf(sample_data)
        print(f"✅ Generated EXACT Batpharma PDF: {filename} ({len(pdf_bytes)} bytes)")
        
        # Verify signature placement
        import fitz
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            tmp.write(pdf_bytes)
            tmp_path = tmp.name
        
        doc = fitz.open(tmp_path)
        page = doc.load_page(0)
        text_content = page.get_text()
        
        if 'BATPHARMA' in text_content:
            print("✅ BATPHARMA signature correctly placed in PDF")
        else:
            print("❌ BATPHARMA signature not found in PDF")
        
        doc.close()
        os.unlink(tmp_path)
        
        # List generated resumes
        resumes = builder.get_generated_resumes()
        print(f"✅ Found {len(resumes)} generated resumes")
        
        print("🎉 EXACT Batpharma resume builder test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_exact_resume_builder()
