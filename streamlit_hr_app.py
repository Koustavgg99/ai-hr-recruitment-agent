"""
HR Automation - Streamlit Web Application
Comprehensive interface for candidate shortlisting, document generation, and email outreach
"""

import streamlit as st

# Page configuration - MUST BE FIRST
st.set_page_config(
    page_title="HR Automation System",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Now import other modules
import pandas as pd
import json
from datetime import datetime
import os
from typing import Dict, List, Any
import plotly.express as px
import plotly.graph_objects as go

# Import our modules
try:
    from candidate_shortlisting import CandidateShortlister
    from word_generator import CandidateDocumentGenerator
    from enhanced_email_system import EnhancedEmailManager
    from hr_email_config import get_available_templates, get_email_template
    from database_manager import CandidateDatabase, get_database
    from ai_content_generator import get_ai_generator
    DATABASE_AVAILABLE = True
    AI_GENERATOR_AVAILABLE = True
except ImportError as e:
    st.error(f"Import error: {e}")
    st.error("Please ensure all required modules are in the same directory")
    DATABASE_AVAILABLE = False
    AI_GENERATOR_AVAILABLE = False

# Enhanced Custom CSS with modern design
st.markdown("""
<style>
    /* Global styles - Enhanced responsive design */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 100%;
        overflow-x: auto;
    }
    
    /* Responsive container for mobile devices */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem !important;
            padding: 0.5rem 0.25rem !important;
            line-height: 1.1 !important;
        }
        
        .block-container {
            padding-left: 0.5rem;
            padding-right: 0.5rem;
        }
    }
    
    /* Container width fix */
    .main .block-container {
        max-width: 100%;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    
    /* Header styles - Fixed for proper display */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin: 1rem auto 2rem auto;
        padding: 1rem 0.5rem;
        position: relative;
        max-width: 100%;
        word-wrap: break-word;
        overflow-wrap: break-word;
        white-space: normal;
        line-height: 1.2;
    }
    
    .main-header::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 100px;
        height: 3px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 2px;
    }
    
    .sub-header {
        font-size: 1.8rem;
        color: #2c3e50;
        font-weight: 600;
        margin-bottom: 1.5rem;
        border-left: 4px solid #3498db;
        padding-left: 1rem;
    }
    
    /* Card-like containers */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        border: 1px solid #e1e8ed;
        margin: 0.5rem 0;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    }
    
    /* Status boxes */
    .success-box {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        color: #155724;
        padding: 1.2rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
        box-shadow: 0 2px 5px rgba(40, 167, 69, 0.2);
    }
    
    .warning-box {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        color: #856404;
        padding: 1.2rem;
        border-radius: 8px;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
        box-shadow: 0 2px 5px rgba(255, 193, 7, 0.2);
    }
    
    .error-box {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        color: #721c24;
        padding: 1.2rem;
        border-radius: 8px;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
        box-shadow: 0 2px 5px rgba(220, 53, 69, 0.2);
    }
    
    .info-box {
        background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
        color: #0c5460;
        padding: 1.2rem;
        border-radius: 8px;
        border-left: 4px solid #17a2b8;
        margin: 1rem 0;
        box-shadow: 0 2px 5px rgba(23, 162, 184, 0.2);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f8f9fa;
    }
    
    /* Button enhancements */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
        border: none;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    /* Form styling */
    .stSelectbox label, .stTextInput label, .stTextArea label {
        font-weight: 600;
        color: #2c3e50;
    }
    
    /* Metrics styling */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border: 1px solid #dee2e6;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: 600;
    }
    
    /* Data loading indicator */
    .data-status {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 0.5rem 1rem;
        background: #e8f5e8;
        border-radius: 6px;
        border-left: 3px solid #28a745;
        margin: 0.5rem 0;
    }
    
    .loading-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border: 2px solid #f3f3f3;
        border-top: 2px solid #3498db;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
</style>
""", unsafe_allow_html=True)

class HRAutomationApp:
    """Main HR Automation Streamlit Application"""
    
    def __init__(self):
        self.init_session_state()
        self.auto_load_data_files()
        
    def init_session_state(self):
        """Initialize session state variables"""
        if 'shortlists' not in st.session_state:
            st.session_state.shortlists = {}
        if 'candidates_data' not in st.session_state:
            st.session_state.candidates_data = []
        if 'jobs_data' not in st.session_state:
            st.session_state.jobs_data = []
        if 'email_log' not in st.session_state:
            st.session_state.email_log = []
        if 'selected_candidates' not in st.session_state:
            st.session_state.selected_candidates = []
        if 'team_members' not in st.session_state:
            st.session_state.team_members = []
    
    def auto_load_data_files(self):
        """Auto-load data files silently on app startup"""
        if 'data_loaded' not in st.session_state:
            try:
                # Load connections.csv
                if os.path.exists("connections.csv"):
                    df = pd.read_csv("connections.csv")
                    st.session_state.candidates_data = df.to_dict('records')
                
                # Load job descriptions
                job_files = [f for f in os.listdir('.') if f.startswith('job_') and f.endswith('.json')]
                if job_files:
                    jobs = []
                    for job_file in job_files:
                        with open(job_file, 'r', encoding='utf-8') as f:
                            job_data = json.load(f)
                            jobs.append(job_data)
                    st.session_state.jobs_data = jobs
                
                # Load existing shortlists if available
                if os.path.exists("shortlists.json"):
                    with open("shortlists.json", "r", encoding="utf-8") as f:
                        st.session_state.shortlists = json.load(f)
                
                # Load existing team members if available
                if os.path.exists("team_members.json"):
                    with open("team_members.json", "r", encoding="utf-8") as f:
                        st.session_state.team_members = json.load(f)
                
                st.session_state.data_loaded = True
                
            except Exception as e:
                pass  # Fail silently on startup
    
    def load_data_files(self):
        """Load and validate data files with user feedback"""
        try:
            # Load connections.csv
            if os.path.exists("connections.csv"):
                df = pd.read_csv("connections.csv")
                st.session_state.candidates_data = df.to_dict('records')
                st.success(f"✅ Loaded {len(df)} candidates from connections.csv")
            else:
                st.error("❌ connections.csv not found")
                return False
            
            # Load job descriptions
            job_files = [f for f in os.listdir('.') if f.startswith('job_') and f.endswith('.json')]
            if job_files:
                jobs = []
                for job_file in job_files:
                    with open(job_file, 'r', encoding='utf-8') as f:
                        job_data = json.load(f)
                        jobs.append(job_data)
                st.session_state.jobs_data = jobs
                st.success(f"✅ Loaded {len(jobs)} job descriptions")
            else:
                st.warning("⚠️ No job description files found (job_*.json)")
            
            # Load existing shortlists if available
            if os.path.exists("shortlists.json"):
                with open("shortlists.json", "r", encoding="utf-8") as f:
                    st.session_state.shortlists = json.load(f)
                st.success(f"✅ Loaded existing shortlists")
                
            return True
            
        except Exception as e:
            st.error(f"❌ Error loading data: {e}")
            return False
    
    def dashboard_page(self):
        """Main dashboard page"""
        st.markdown('<h1 class="main-header">🎯 HR Automation Dashboard</h1>', unsafe_allow_html=True)  
        # Load data files
        with st.expander("📁 Data Files ", expanded=True):
            if st.button("🔄 Refresh Data"):
                self.load_data_files()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    label="👥 Total Candidates",
                    value=len(st.session_state.candidates_data)
                )
            with col2:
                st.metric(
                    label="💼 Job Descriptions",
                    value=len(st.session_state.jobs_data)
                )
            with col3:
                st.metric(
                    label="📊 Generated Shortlists",
                    value=len(st.session_state.shortlists)
                )
        
        # Quick stats
        if st.session_state.shortlists:
            st.subheader("📈 Shortlist Statistics")
            
            # Create statistics
            total_matches = sum(len(candidates) for candidates in st.session_state.shortlists.values())
            avg_matches = total_matches / len(st.session_state.shortlists) if st.session_state.shortlists else 0
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("🎯 Total Matches", total_matches)
            with col2:
                st.metric("📊 Average per Job", f"{avg_matches:.1f}")
            with col3:
                candidates_with_email = sum(
                    1 for job_candidates in st.session_state.shortlists.values()
                    for candidate_match in job_candidates
                    if candidate_match['candidate'].get('email', '').strip()
                )
                st.metric("📧 With Email", candidates_with_email)
            with col4:
                st.metric("📝 Email Logs", len(st.session_state.email_log))
            
            # Visualization
            if total_matches > 0:
                st.subheader("📊 Matches by Job")
                
                job_names = list(st.session_state.shortlists.keys())
                match_counts = [len(candidates) for candidates in st.session_state.shortlists.values()]
                
                fig = px.bar(
                    x=job_names,
                    y=match_counts,
                    title="Candidate Matches by Job Position",
                    labels={'x': 'Job Position', 'y': 'Number of Matches'}
                )
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
    
    def candidate_management_page(self):
        """Candidate management and addition page"""
        st.markdown('<h2 class="main-header">👤 Candidate Management</h2>', unsafe_allow_html=True)
        
        if not DATABASE_AVAILABLE:
            st.error("❌ Database functionality is not available. Please ensure database_manager.py is in the directory.")
            return
        
        # Initialize database
        try:
            db = get_database()
            st.success("✅ Database connection established")
        except Exception as e:
            st.error(f"❌ Database connection failed: {e}")
            return
        
        tab1, tab2, tab3 = st.tabs(["➕ Add New Candidate", "👥 View All Candidates", "🔍 Search Candidates"])
        
        with tab1:
            self.add_candidate_interface(db)
        
        with tab2:
            self.view_all_candidates(db)
        
        with tab3:
            self.search_candidates_interface(db)
    
    def add_candidate_interface(self, db):
        """Interface for adding new candidates with manual and auto-fill options"""
        st.subheader("➕ Add New Candidate")

        # Initialize tab state for automatic switching
        if 'active_candidate_tab' not in st.session_state:
            st.session_state.active_candidate_tab = "auto"  # Default to Auto-Fill tab
        
        # Check if we should switch to manual entry tab after extraction
        if st.session_state.get('switch_to_manual_entry', False):
            st.session_state.active_candidate_tab = "manual"  # Switch to Manual Entry tab
            st.session_state.switch_to_manual_entry = False  # Reset the flag
        
        # Tab selection using radio buttons for programmatic control
        tab_choice = st.radio(
            "Choose Entry Method:",
            ["✍️ Manual Entry", "🤖 Auto-Fill (Resume/LinkedIn)"],
            index=0 if st.session_state.active_candidate_tab == "manual" else 1,
            horizontal=True,
            help="Select how you want to add candidate information"
        )
        
        # Update active tab based on user selection
        if tab_choice == "✍️ Manual Entry":
            st.session_state.active_candidate_tab = "manual"
        else:
            st.session_state.active_candidate_tab = "auto"
        
        # Display appropriate interface based on selection
        if st.session_state.active_candidate_tab == "auto":
            # Lazy import to avoid Streamlit import issues at module import time
            try:
                from candidate_autofill import CandidateAutoFill, validate_extracted_data
                
                # Import configuration and initialize auto-fill
                try:
                    from config import config, GEMINI_API_KEY
                    env_gemini_api_key = GEMINI_API_KEY
                except ImportError:
                    env_gemini_api_key = None
                
                # Initialize auto-fill with API key from environment configuration
                autofill = CandidateAutoFill(gemini_api_key=env_gemini_api_key)
                
                status_info = autofill.get_status_info()
                st.write("**Auto-Fill Status:**")
                for service, status in status_info.items():
                    st.write(f"• {service}: {status}")
                
                # Show Gemini AI status
                if env_gemini_api_key and autofill.hybrid_parser:
                    st.success("")
                elif env_gemini_api_key:
                    st.warning("🤖 Gemini AI Enhanced Parsing: ⚠️ Failed to initialize")
                else:
                    st.info("🤖 Gemini AI Enhanced Parsing: ➖ Not configured")

                extracted = autofill.render_autofill_interface()
                if extracted:
                    # Allow user to push extracted values into the manual form below via session_state
                    st.session_state["prefill_candidate_data"] = extracted
                    # Set flag to switch to manual entry tab
                    st.session_state.switch_to_manual_entry = True
                    st.success("✅ Extracted data is ready. Switching to Manual Entry tab to review and save.")
                    st.rerun()  # Trigger rerun to switch tab
            except Exception as e:
                st.warning(f"Auto-fill interface unavailable: {e}")
        
        elif st.session_state.active_candidate_tab == "manual":
            # Pre-fill with extracted data if available
            prefill = st.session_state.get("prefill_candidate_data", {})

            with st.form("add_candidate_form"):
                # Basic information
                col1, col2 = st.columns(2)

                with col1:
                    full_name = st.text_input(
                        "Full Name *",
                        value=prefill.get('full_name', ''),
                        placeholder="e.g., John Doe",
                        help="Enter the candidate's full name"
                    )

                    email = st.text_input(
                        "Email Address",
                        value=prefill.get('email', ''),
                        placeholder="e.g., john.doe@example.com",
                        help="Enter the candidate's email address"
                    )

                    linkedin_url = st.text_input(
                        "LinkedIn URL *",
                        value=prefill.get('linkedin_url', ''),
                        placeholder="e.g., https://linkedin.com/in/johndoe",
                        help="Enter the candidate's LinkedIn profile URL"
                    )

                with col2:
                    company = st.text_input(
                        "Current Company",
                        value=prefill.get('company', ''),
                        placeholder="e.g., Tech Solutions Inc.",
                        help="Enter the candidate's current company"
                    )

                    position = st.text_input(
                        "Current Position",
                        value=prefill.get('position', ''),
                        placeholder="e.g., Senior Software Engineer",
                        help="Enter the candidate's current job title"
                    )

                    location = st.text_input(
                        "Location",
                        value=prefill.get('location', ''),
                        placeholder="e.g., New York, NY",
                        help="Enter the candidate's location"
                    )

                # Additional information
                st.subheader("Additional Information")

                col1, col2 = st.columns(2)

                with col1:
                    skills = st.text_area(
                        "Skills (comma-separated)",
                        value=prefill.get('skills', ''),
                        placeholder="e.g., Python, JavaScript, React, Node.js, AWS",
                        height=100,
                        help="List the candidate's technical skills"
                    )

                with col2:
                    experience_summary = st.text_area(
                        "Experience Summary",
                        value=prefill.get('experience_summary', ''),
                        placeholder="Brief summary of candidate's experience...",
                        height=100,
                        help="Provide a brief summary of the candidate's experience"
                    )

                # Connected date
                connected_on = st.date_input(
                    "Connected On",
                    value=datetime.now().date(),
                    help="Date when you connected with this candidate"
                )

                # Submit button
                submitted = st.form_submit_button("✨ Add Candidate", type="primary")

                if submitted:
                    # Validate required fields
                    if not full_name or not linkedin_url:
                        st.error("❌ Please fill in all required fields (marked with *)")
                        return

                    # Validate LinkedIn URL format
                    if not linkedin_url.startswith(('http://', 'https://')):
                        st.error("❌ Please enter a valid LinkedIn URL starting with http:// or https://")
                        return

                    # Prepare candidate data
                    candidate_data = {
                        'full_name': full_name.strip(),
                        'email': email.strip(),
                        'linkedin_url': linkedin_url.strip(),
                        'company': company.strip(),
                        'position': position.strip(),
                        'location': location.strip(),
                        'skills': skills.strip(),
                        'experience_summary': experience_summary.strip(),
                        'connected_on': connected_on.strftime('%d-%b-%y')
                    }

                    # Add candidate to database and CSV
                    try:
                        with st.spinner("Adding candidate to database and CSV..."):
                            candidate_id = db.add_candidate(candidate_data)

                            if candidate_id:
                                st.success(f"✅ Candidate '{full_name}' added successfully!")
                                st.success(f"🆔 Assigned Database ID: {candidate_id}")
                                st.info("📄 Candidate has been added to both database and CSV file")

                                # Show confirmation details
                                with st.expander("👁️ Added Candidate Details", expanded=True):
                                    col1, col2 = st.columns(2)

                                    with col1:
                                        st.write(f"**Name:** {candidate_data['full_name']}")
                                        st.write(f"**Email:** {candidate_data['email'] or 'Not provided'}")
                                        st.write(f"**Company:** {candidate_data['company'] or 'Not provided'}")
                                        st.write(f"**Position:** {candidate_data['position'] or 'Not provided'}")

                                    with col2:
                                        st.write(f"**Location:** {candidate_data['location'] or 'Not provided'}")
                                        st.write(f"**LinkedIn:** [Profile Link]({candidate_data['linkedin_url']})")
                                        st.write(f"**Connected:** {candidate_data['connected_on']}")
                                        st.write(f"**Database ID:** {candidate_id}")

                                    if candidate_data['skills']:
                                        st.write(f"**Skills:** {candidate_data['skills']}")

                                    if candidate_data['experience_summary']:
                                        st.write(f"**Experience:** {candidate_data['experience_summary']}")

                                # Clear prefill after successful add
                                if 'prefill_candidate_data' in st.session_state:
                                    del st.session_state['prefill_candidate_data']

                                # Update session state if needed
                                try:
                                    self.load_data_files()
                                except:
                                    pass  # Ignore if CSV loading fails

                            else:
                                st.warning("⚠️ Candidate may already exist with this LinkedIn URL")

                    except Exception as e:
                        st.error(f"❌ Error adding candidate: {str(e)}")
    
    def view_all_candidates(self, db):
        """Interface for viewing all candidates"""
        st.subheader("👥 All Candidates")
        
        try:
            # Get total count
            total_candidates = db.get_candidates_count()
            st.info(f"📊 Total candidates in database: {total_candidates}")
            
            if total_candidates > 0:
                # Load all candidates
                with st.spinner("Loading candidates from database..."):
                    candidates = db.get_all_candidates()
                
                if candidates:
                    # Display options
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        show_count = st.selectbox(
                            "Show candidates:",
                            [10, 25, 50, 100, "All"],
                            index=1
                        )
                    
                    with col2:
                        sort_by = st.selectbox(
                            "Sort by:",
                            ["Created Date (Newest)", "Created Date (Oldest)", "Name (A-Z)", "Name (Z-A)", "Company"]
                        )
                    
                    with col3:
                        if st.button("🔄 Refresh"):
                            st.rerun()
                    
                    # Sort candidates
                    if sort_by == "Name (A-Z)":
                        candidates.sort(key=lambda x: x['full_name'].lower())
                    elif sort_by == "Name (Z-A)":
                        candidates.sort(key=lambda x: x['full_name'].lower(), reverse=True)
                    elif sort_by == "Company":
                        candidates.sort(key=lambda x: (x['company'] or '').lower())
                    elif sort_by == "Created Date (Oldest)":
                        candidates.sort(key=lambda x: x['created_at'])
                    # Default: Created Date (Newest) - already sorted by database query
                    
                    # Limit display count
                    if show_count != "All":
                        candidates = candidates[:int(show_count)]
                    
                    # Display candidates
                    st.write(f"Showing {len(candidates)} of {total_candidates} candidates:")
                    
                    for i, candidate in enumerate(candidates, 1):
                        with st.expander(f"{i}. {candidate['full_name']} - {candidate['company'] or 'No Company'}"):
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.write(f"**👤 Name:** {candidate['full_name']}")
                                st.write(f"**📧 Email:** {candidate['email'] or 'Not provided'}")
                                st.write(f"**🏢 Company:** {candidate['company'] or 'Not provided'}")
                                st.write(f"**💼 Position:** {candidate['position'] or 'Not provided'}")
                            
                            with col2:
                                st.write(f"**📍 Location:** {candidate['location'] or 'Not provided'}")
                                st.write(f"**🔗 LinkedIn:** [Profile]({candidate['linkedin_url']})")
                                st.write(f"**📅 Connected:** {candidate['connected_on'] or 'Not provided'}")
                                st.write(f"**🆔 Database ID:** {candidate['id']}")
                            
                            with col3:
                                if candidate['skills']:
                                    st.write(f"**🔧 Skills:** {candidate['skills'][:100]}{'...' if len(candidate['skills']) > 100 else ''}")
                                
                                if candidate['experience_summary']:
                                    st.write(f"**📝 Experience:** {candidate['experience_summary'][:100]}{'...' if len(candidate['experience_summary']) > 100 else ''}")
                                
                                st.write(f"**🕒 Added:** {candidate['created_at'][:16] if candidate['created_at'] else 'Unknown'}")
                            
                            # Action buttons
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                if st.button(f"✏️ Edit", key=f"edit_candidate_{candidate['id']}"):
                                    st.info("Edit functionality will be available in a future update.")
                            
                            with col2:
                                if st.button(f"🗑️ Delete", key=f"delete_candidate_{candidate['id']}"):
                                    if st.session_state.get(f"confirm_delete_candidate_{candidate['id']}", False):
                                        if db.delete_candidate(candidate['id']):
                                            st.success(f"✅ Deleted {candidate['full_name']}")
                                            st.rerun()
                                        else:
                                            st.error("❌ Failed to delete candidate")
                                    else:
                                        st.session_state[f"confirm_delete_candidate_{candidate['id']}"] = True
                                        st.warning("⚠️ Click again to confirm deletion")
                else:
                    st.warning("No candidates found in database")
            else:
                st.info("📝 No candidates in the database yet. Add your first candidate using the 'Add New Candidate' tab.")
        
        except Exception as e:
            st.error(f"❌ Error loading candidates: {str(e)}")
    
    def search_candidates_interface(self, db):
        """Interface for searching candidates"""
        st.subheader("🔍 Search Candidates")
        
        # Search input
        col1, col2 = st.columns([3, 1])
        
        with col1:
            search_term = st.text_input(
                "Search candidates by name, company, or position:",
                placeholder="e.g., John, Google, Engineer",
                help="Enter any part of name, company name, or position title"
            )
        
        with col2:
            search_button = st.button("🔍 Search", type="primary")
        
        # Perform search
        if search_term and (search_button or True):  # Search as user types
            try:
                with st.spinner(f"Searching for '{search_term}'..."):
                    results = db.search_candidates(search_term)
                
                if results:
                    st.success(f"✅ Found {len(results)} candidate(s) matching '{search_term}'")
                    
                    # Display search results
                    for i, candidate in enumerate(results, 1):
                        with st.expander(f"{i}. {candidate['full_name']} - {candidate['company'] or 'No Company'}"):
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.write(f"**👤 Name:** {candidate['full_name']}")
                                st.write(f"**📧 Email:** {candidate['email'] or 'Not provided'}")
                                st.write(f"**🏢 Company:** {candidate['company'] or 'Not provided'}")
                                st.write(f"**💼 Position:** {candidate['position'] or 'Not provided'}")
                            
                            with col2:
                                st.write(f"**📍 Location:** {candidate['location'] or 'Not provided'}")
                                st.write(f"**🔗 LinkedIn:** [Profile]({candidate['linkedin_url']})")
                                st.write(f"**📅 Connected:** {candidate['connected_on'] or 'Not provided'}")
                                st.write(f"**🆔 Database ID:** {candidate['id']}")
                            
                            with col3:
                                if candidate['skills']:
                                    st.write(f"**🔧 Skills:** {candidate['skills'][:100]}{'...' if len(candidate['skills']) > 100 else ''}")
                                
                                if candidate['experience_summary']:
                                    st.write(f"**📝 Experience:** {candidate['experience_summary'][:100]}{'...' if len(candidate['experience_summary']) > 100 else ''}")
                                
                                st.write(f"**🕒 Added:** {candidate['created_at'][:16] if candidate['created_at'] else 'Unknown'}")
                else:
                    st.warning(f"🔍 No candidates found matching '{search_term}'")
                    st.info("💡 Try searching with different keywords like name, company, or job title.")
            
            except Exception as e:
                st.error(f"❌ Search error: {str(e)}")
        
        elif search_term == "":
            st.info("💡 Enter a search term to find candidates by name, company, or position.")
    
    def job_management_page(self):
        """Job management and creation page"""
        st.markdown('<h2 class="main-header">💼 Job Management</h2>', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["📝 Create New Job", "📋 Manage Existing Jobs"])
        
        with tab1:
            self.create_job_interface()
        
        with tab2:
            self.manage_existing_jobs()
    
    def create_job_interface(self):
        """Interface for creating new job descriptions with AI assistance"""
        st.subheader("📝 Create New Job Description")
        
        # Initialize AI generator
        ai_generator = None
        if AI_GENERATOR_AVAILABLE:
            try:
                ai_generator = get_ai_generator()
                if ai_generator:
                    st.success("🤖 AI Content Generation Available")
                    # Show AI service status
                    status = ai_generator.get_status()
                    status_cols = st.columns(len(status))
                    for i, (service, status_text) in enumerate(status.items()):
                        with status_cols[i]:
                            st.write(f"**{service}:** {status_text}")
                else:
                    st.warning("⚠️ AI services not available. Check Ollama or Gemini API configuration.")
            except Exception as e:
                st.error(f"❌ AI generator initialization failed: {e}")
        
        # Initialize session state for generated content
        if 'ai_generated_description' not in st.session_state:
            st.session_state.ai_generated_description = ""
        if 'ai_generated_required_skills' not in st.session_state:
            st.session_state.ai_generated_required_skills = ""
        if 'ai_generated_preferred_skills' not in st.session_state:
            st.session_state.ai_generated_preferred_skills = ""
        
        # Shared basic job information fields (used for both AI generation and form)
        st.subheader("📋 Basic Job Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            job_title = st.text_input(
                "Job Title *", 
                placeholder="e.g., Senior Python Developer",
                key="shared_job_title"
            )
            
            company_name = st.text_input(
                "Company Name *",
                placeholder="e.g., Tech Solutions Inc.",
                key="shared_company_name"
            )
        
        with col2:
            experience_level = st.selectbox(
                "Experience Level *",
                ["Entry Level (0-2 years)", "Mid Level (3-5 years)", "Senior Level (6-10 years)", "Lead/Principal (10+ years)"],
                key="shared_experience_level"
            )
            
            department = st.text_input(
                "Department",
                placeholder="e.g., Engineering, Marketing",
                key="shared_department"
            )
        
        # AI Generation buttons (using shared fields)
        if ai_generator:
            st.markdown("### 🤖 AI Content Generation")
            st.info("💡 Use the basic job information above to generate AI content below.")
            
            # AI generation buttons
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🤖 Generate Job Description", key="generate_description_btn"):
                    if job_title and company_name:
                        with st.spinner("🤖 Generating job description..."):
                            try:
                                generated_description = ai_generator.generate_job_description(
                                    job_title=job_title,
                                    company_name=company_name,
                                    experience_level=experience_level,
                                    employment_type="Full-time",
                                    location="",
                                    department=department
                                )
                                if generated_description:
                                    st.session_state.ai_generated_description = generated_description
                                    st.success("✅ Job description generated!")
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to generate job description.")
                            except Exception as e:
                                st.error(f"❌ Error: {e}")
                    else:
                        st.warning("⚠️ Please fill in Job Title and Company Name first.")
            
            with col2:
                if st.button("🤖 Generate Skills", key="generate_skills_btn"):
                    if job_title:
                        with st.spinner("🤖 Generating skills..."):
                            try:
                                required_skills, preferred_skills = ai_generator.generate_skills(
                                    job_title=job_title,
                                    experience_level=experience_level,
                                    department=department
                                )
                                if required_skills:
                                    st.session_state.ai_generated_required_skills = "\n".join(required_skills)
                                if preferred_skills:
                                    st.session_state.ai_generated_preferred_skills = "\n".join(preferred_skills)
                                
                                if required_skills or preferred_skills:
                                    st.success("✅ Skills generated!")
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to generate skills.")
                            except Exception as e:
                                st.error(f"❌ Error: {e}")
                    else:
                        st.warning("⚠️ Please fill in Job Title first.")
            
            with col3:
                if st.button("🗑️ Clear AI Content", key="clear_ai_content"):
                    st.session_state.ai_generated_description = ""
                    st.session_state.ai_generated_required_skills = ""
                    st.session_state.ai_generated_preferred_skills = ""
                    st.success("✅ AI content cleared!")
                    st.rerun()
        
        st.markdown("---")
        
        # Single unified form
        with st.form("job_creation_form"):
            # Additional job information (location and employment type)
            col1, col2 = st.columns(2)
            
            with col1:
                location = st.text_input(
                    "Location",
                    placeholder="e.g., Remote, New York, NY"
                )
            
            with col2:
                employment_type = st.selectbox(
                    "Employment Type",
                    ["Full-time", "Part-time", "Contract", "Internship"]
                )
            
            # Job description
            st.subheader("📄 Job Description")
            job_description = st.text_area(
                "Job Description *",
                value=st.session_state.ai_generated_description,
                height=200,
                placeholder="""Describe the role, responsibilities, and what the candidate will be doing...
                
Example:
We are looking for a Senior Python Developer to join our engineering team. You will be responsible for:
- Developing and maintaining web applications
- Collaborating with cross-functional teams
- Writing clean, maintainable code
- Mentoring junior developers"""
            )
            
            # Skills and requirements
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🔧 Required Skills")
                required_skills_input = st.text_area(
                    "Required Skills (one per line) *",
                    value=st.session_state.ai_generated_required_skills,
                    height=150,
                    placeholder="""Python
Django
PostgreSQL
REST APIs
Git"""
                )
            
            with col2:
                st.subheader("⭐ Preferred Skills")
                preferred_skills_input = st.text_area(
                    "Preferred Skills (one per line)",
                    value=st.session_state.ai_generated_preferred_skills,
                    height=150,
                    placeholder="""React
Docker
AWS
Machine Learning
Agile/Scrum"""
                )
            
            # Additional information
            st.subheader("Additional Information")
            
            col1, col2 = st.columns(2)
            with col1:
                salary_range = st.text_input(
                    "Salary Range",
                    placeholder="e.g., $80,000 - $120,000"
                )
                
                benefits = st.text_area(
                    "Benefits",
                    height=100,
                    placeholder="Health insurance, 401k, flexible hours..."
                )
            
            with col2:
                reporting_to = st.text_input(
                    "Reports To",
                    placeholder="e.g., Engineering Manager"
                )
                
                team_size = st.text_input(
                    "Team Size",
                    placeholder="e.g., 5-person engineering team"
                )
            
            # Submit button
            submitted = st.form_submit_button("✨ Create Job Description", type="primary")
            
            if submitted:
                # Validate required fields
                if not job_title or not company_name or not job_description or not required_skills_input:
                    st.error("❌ Please fill in all required fields (marked with *)")
                    return
                
                # Process skills
                required_skills = [skill.strip() for skill in required_skills_input.split('\n') if skill.strip()]
                preferred_skills = [skill.strip() for skill in preferred_skills_input.split('\n') if skill.strip()]
                
                # Create job data structure
                job_data = {
                    "title": job_title,
                    "company": company_name,
                    "department": department,
                    "location": location,
                    "experience_level": experience_level,
                    "employment_type": employment_type,
                    "description": job_description,
                    "skills_required": required_skills,
                    "skills_preferred": preferred_skills,
                    "salary_range": salary_range,
                    "benefits": benefits,
                    "reporting_to": reporting_to,
                    "team_size": team_size,
                    "created_date": datetime.now().isoformat(),
                    "status": "active"
                }
                
                # Save job to file
                try:
                    # Create safe filename
                    safe_title = "".join(c for c in job_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                    safe_title = safe_title.replace(' ', '_')
                    filename = f"job_{safe_title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(job_data, f, indent=2, ensure_ascii=False)
                    
                    # Add to session state
                    st.session_state.jobs_data.append(job_data)
                    
                    st.success(f"✅ Job description created successfully!")
                    st.success(f"📄 Saved as: {filename}")
                    
                    # Show preview
                    with st.expander("👁️ Preview Created Job Description", expanded=True):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**Title:** {job_data['title']}")
                            st.write(f"**Company:** {job_data['company']}")
                            st.write(f"**Location:** {job_data['location']}")
                            st.write(f"**Experience:** {job_data['experience_level']}")
                            st.write(f"**Type:** {job_data['employment_type']}")
                        
                        with col2:
                            st.write(f"**Required Skills ({len(required_skills)}):**")
                            for skill in required_skills:
                                st.write(f"  • {skill}")
                            
                            if preferred_skills:
                                st.write(f"**Preferred Skills ({len(preferred_skills)}):**")
                                for skill in preferred_skills:
                                    st.write(f"  • {skill}")
                        
                        st.write("**Description:**")
                        st.write(job_data['description'])
                    
                except Exception as e:
                    st.error(f"❌ Error saving job description: {e}")
    
    def manage_existing_jobs(self):
        """Interface for managing existing job descriptions"""
        st.subheader("📋 Existing Job Descriptions")
        
        if not st.session_state.jobs_data:
            st.info("📝 No job descriptions found. Create your first job description in the 'Create New Job' tab.")
            return
        
        # Display existing jobs
        for i, job in enumerate(st.session_state.jobs_data):
            with st.expander(f"💼 {job.get('title', 'Untitled Job')} - {job.get('company', 'Unknown Company')}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**📋 Title:** {job.get('title', 'N/A')}")
                    st.write(f"**🏢 Company:** {job.get('company', 'N/A')}")
                    st.write(f"**📍 Location:** {job.get('location', 'N/A')}")
                    st.write(f"**⏰ Type:** {job.get('employment_type', 'N/A')}")
                
                with col2:
                    st.write(f"**📊 Experience:** {job.get('experience_level', 'N/A')}")
                    st.write(f"**🏛️ Department:** {job.get('department', 'N/A')}")
                    st.write(f"**💰 Salary:** {job.get('salary_range', 'Not specified')}")
                    st.write(f"**📅 Created:** {job.get('created_date', 'N/A')[:10] if job.get('created_date') else 'N/A'}")
                
                with col3:
                    required_skills = job.get('skills_required', [])
                    preferred_skills = job.get('skills_preferred', [])
                    
                    if required_skills:
                        st.write(f"**🔧 Required Skills ({len(required_skills)}):**")
                        skills_text = ", ".join(required_skills[:5])
                        if len(required_skills) > 5:
                            skills_text += f" (+{len(required_skills) - 5} more)"
                        st.write(skills_text)
                    
                    if preferred_skills:
                        st.write(f"**⭐ Preferred Skills ({len(preferred_skills)}):**")
                        skills_text = ", ".join(preferred_skills[:5])
                        if len(preferred_skills) > 5:
                            skills_text += f" (+{len(preferred_skills) - 5} more)"
                        st.write(skills_text)
                
                # Description
                if job.get('description'):
                    st.write("**📄 Description:**")
                    st.write(job['description'][:200] + "..." if len(job['description']) > 200 else job['description'])
                
                # Action buttons
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button(f"🎯 Generate Shortlist", key=f"shortlist_{i}"):
                        st.info(f"Generating shortlist for {job['title']}...")
                        # This will trigger shortlisting for this specific job
                        try:
                            shortlister = CandidateShortlister("connections.csv")
                            matches = shortlister.find_matches_for_job(job, 0.1, 20)
                            st.session_state.shortlists[job['title']] = matches
                            st.success(f"✅ Generated {len(matches)} matches!")
                        except Exception as e:
                            st.error(f"❌ Error: {e}")
                
                with col2:
                    if st.button(f"✏️ Edit Job", key=f"edit_{i}"):
                        st.info("Edit functionality will be available in the next update.")
                
                with col3:
                    if st.button(f"🗑️ Delete Job", key=f"delete_{i}"):
                        if st.session_state.get(f"confirm_delete_{i}", False):
                            # Remove from session state
                            st.session_state.jobs_data.pop(i)
                            st.success(f"✅ Job deleted successfully!")
                            st.rerun()
                        else:
                            st.session_state[f"confirm_delete_{i}"] = True
                            st.warning("⚠️ Click again to confirm deletion")
        
        # Bulk operations
        if len(st.session_state.jobs_data) > 1:
            st.subheader("🔄 Bulk Operations")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🎯 Generate All Shortlists"):
                    with st.spinner("Generating shortlists for all jobs..."):
                        try:
                            shortlister = CandidateShortlister("connections.csv")
                            new_shortlists = {}
                            
                            progress_bar = st.progress(0)
                            for i, job in enumerate(st.session_state.jobs_data):
                                matches = shortlister.find_matches_for_job(job, 0.1, 20)
                                new_shortlists[job['title']] = matches
                                progress_bar.progress((i + 1) / len(st.session_state.jobs_data))
                            
                            st.session_state.shortlists.update(new_shortlists)
                            progress_bar.empty()
                            
                            total_matches = sum(len(matches) for matches in new_shortlists.values())
                            st.success(f"✅ Generated {total_matches} total matches across {len(new_shortlists)} jobs!")
                            
                        except Exception as e:
                            st.error(f"❌ Error: {e}")
            
            with col2:
                if st.button("💾 Export All Jobs"):
                    try:
                        export_data = {
                            "jobs": st.session_state.jobs_data,
                            "exported_at": datetime.now().isoformat(),
                            "total_jobs": len(st.session_state.jobs_data)
                        }
                        
                        json_str = json.dumps(export_data, indent=2, ensure_ascii=False)
                        st.download_button(
                            label="📥 Download Jobs JSON",
                            data=json_str,
                            file_name=f"all_jobs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json"
                        )
                    except Exception as e:
                        st.error(f"❌ Export error: {e}")
    
    def shortlisting_page(self):
        """Candidate shortlisting page"""
        st.markdown('<h2 class="main-header">🎯 Candidate Shortlisting</h2>', unsafe_allow_html=True)
        
        if not st.session_state.candidates_data:
            st.warning("⚠️ No candidate data loaded. Please load data first.")
            if st.button("🔄 Load Data"):
                self.load_data_files()
            return
        
        if not st.session_state.jobs_data:
            st.warning("⚠️ No job descriptions loaded. Please add job description files (job_*.json).")
            return
        
        # Configuration
        st.subheader("⚙️ Shortlisting Configuration")
        
        col1, col2 = st.columns(2)
        with col1:
            min_score_threshold = st.slider(
                "🎯 Minimum Score Threshold",
                min_value=0.0,
                max_value=1.0,
                value=0.1,
                step=0.05,
                help="Minimum matching score for candidates to be included"
            )
        
        with col2:
            max_candidates = st.slider(
                "👥 Maximum Candidates per Job",
                min_value=5,
                max_value=50,
                value=20,
                step=5,
                help="Maximum number of candidates to shortlist per job"
            )
        
        # Job selection
        st.subheader("💼 Select Jobs to Process")
        
        job_options = {}
        for job in st.session_state.jobs_data:
            title = job.get('title', 'Unknown Job')
            job_options[title] = job
        
        selected_jobs = st.multiselect(
            "Choose job positions:",
            options=list(job_options.keys()),
            default=list(job_options.keys())[:3] if len(job_options) > 3 else list(job_options.keys())
        )
        
        # Generate shortlists
        if st.button("🚀 Generate Shortlists", type="primary"):
            if not selected_jobs:
                st.error("❌ Please select at least one job position")
                return
            
            with st.spinner("🔄 Processing shortlists..."):
                try:
                    shortlister = CandidateShortlister("connections.csv")
                    
                    # Process selected jobs
                    selected_job_data = [job_options[job_title] for job_title in selected_jobs]
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    new_shortlists = {}
                    for i, job in enumerate(selected_job_data):
                        job_title = job.get('title', f'Job {i+1}')
                        status_text.text(f"Processing: {job_title}")
                        
                        matches = shortlister.find_matches_for_job(
                            job, 
                            min_score_threshold,
                            max_candidates
                        )
                        new_shortlists[job_title] = matches
                        
                        progress_bar.progress((i + 1) / len(selected_job_data))
                    
                    # Update session state
                    st.session_state.shortlists.update(new_shortlists)
                    
                    # Save to file
                    with open("shortlists.json", "w", encoding="utf-8") as f:
                        json.dump(st.session_state.shortlists, f, indent=2, ensure_ascii=False)
                    
                    status_text.empty()
                    progress_bar.empty()
                    
                    st.markdown('<div class="success-box">✅ Shortlists generated successfully!</div>', 
                              unsafe_allow_html=True)
                    
                    # Display summary
                    total_matches = sum(len(candidates) for candidates in new_shortlists.values())
                    st.info(f"🎯 Generated {total_matches} total matches across {len(new_shortlists)} job positions")
                    
                except Exception as e:
                    st.error(f"❌ Error generating shortlists: {e}")
        
        # Display existing shortlists
        if st.session_state.shortlists:
            st.subheader("📊 Current Shortlists")
            
            for job_title, candidates in st.session_state.shortlists.items():
                with st.expander(f"💼 {job_title} ({len(candidates)} matches)"):
                    if candidates:
                        # Create DataFrame for display
                        display_data = []
                        for candidate_match in candidates:
                            candidate = candidate_match['candidate']
                            # Try multiple possible field names for LinkedIn URL
                            linkedin_url = candidate.get('linkedin_url', candidate.get('URL', candidate.get('url', 'Not available')))
                            if linkedin_url and linkedin_url != 'Not available' and 'linkedin' in linkedin_url.lower():
                                linkedin_display = linkedin_url  # Store the actual URL for clickable links
                            else:
                                linkedin_display = 'Not available'
                            
                            display_data.append({
                                'Name': candidate.get('full_name', 'Unknown'),
                                'Email': candidate.get('email', 'Not available'),
                                'Company': candidate.get('company', 'Not available'),
                                'Position': candidate.get('position', 'Not available'),
                                'LinkedIn': linkedin_display,
                                'Score': f"{candidate_match['score']:.2f}",
                                'Matched Skills': ', '.join(candidate_match.get('matched_skills', [])[:3])
                            })
                        
                        df = pd.DataFrame(display_data)
                        
                        # Configure column types for clickable links
                        column_config = {
                            "LinkedIn": st.column_config.LinkColumn(
                                "LinkedIn Profile",
                                help="Click to open LinkedIn profile in new tab",
                                display_text="🔗 LinkedIn"
                            ),
                            "Email": st.column_config.TextColumn(
                                "Email",
                                help="Candidate's email address"
                            ),
                            "Score": st.column_config.NumberColumn(
                                "Match Score",
                                help="Candidate matching score",
                                format="%.2f"
                            )
                        }
                        
                        st.data_editor(
                            df, 
                            use_container_width=True,
                            column_config=column_config,
                            disabled=True,  # Make it read-only
                            hide_index=True
                        )
                    else:
                        st.info("No matches found for this position")
    
    def email_page(self):
        """Email management page"""
        st.markdown('<h2 class="main-header">📧 Email Management</h2>', unsafe_allow_html=True)
        
        if not st.session_state.shortlists:
            st.warning("⚠️ No shortlists available. Please generate shortlists first.")
            return
        
        # Initialize email manager
        try:
            email_manager = EnhancedEmailManager()
            st.success("✅ Email system initialized successfully")
        except Exception as e:
            st.error(f"❌ Error initializing email system: {e}")
            return
        
        # Email sending tabs
        tab1, tab2, tab3 = st.tabs(["📧 Send Individual Email", "📨 Bulk Email Sending", "📋 Email Templates"])
        
        with tab1:
            self.individual_email_interface(email_manager)
        
        with tab2:
            self.bulk_email_interface(email_manager)
        
        with tab3:
            self.email_templates_interface()
    
    def individual_email_interface(self, email_manager):
        """Interface for sending individual emails"""
        st.subheader("📧 Send Individual Email")
        
        # Job selection
        job_titles = list(st.session_state.shortlists.keys())
        selected_job = st.selectbox("💼 Select Job Position:", job_titles)
        
        if selected_job:
            candidates = st.session_state.shortlists[selected_job]
            candidate_options = {}
            
            for candidate_match in candidates:
                candidate = candidate_match['candidate']
                name = candidate.get('full_name', 'Unknown')
                email = candidate.get('email', '').strip()
                if email:
                    candidate_options[f"{name} ({email})"] = {
                        'name': name,
                        'email': email
                    }
            
            if candidate_options:
                selected_candidate_key = st.selectbox(
                    "👤 Select Candidate:",
                    list(candidate_options.keys())
                )
                
                if selected_candidate_key:
                    candidate_info = candidate_options[selected_candidate_key]
                    
                    # Template selection
                    templates = get_available_templates()
                    selected_template = st.selectbox("📝 Email Template:", templates)
                    
                    # Preview email
                    if st.button("👁️ Preview Email"):
                        preview = email_manager.preview_email(
                            candidate_info['name'],
                            selected_job,
                            selected_template
                        )
                        st.text_area("Email Preview:", preview, height=300)
                    
                    # Send email
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("📧 Send Email", type="primary"):
                            with st.spinner("Sending email..."):
                                success = email_manager.send_manual_email(
                                    candidate_info['name'],
                                    candidate_info['email'],
                                    selected_job,
                                    selected_template
                                )
                                
                                if success:
                                    st.success(f"✅ Email sent successfully to {candidate_info['name']}")
                                    # Update email log in session state
                                    st.session_state.email_log.extend(email_manager.email_log)
                                else:
                                    st.error(f"❌ Failed to send email to {candidate_info['name']}")
                    
                    with col2:
                        if st.button("💾 Save Email Log"):
                            email_manager.save_email_log()
                            st.success("📄 Email log saved successfully")
            else:
                st.warning("⚠️ No candidates with email addresses found for this job")
    
    def bulk_email_interface(self, email_manager):
        """Interface for bulk email sending"""
        st.subheader("📨 Enhanced Bulk Email Sending")
        
        # Option to select from all candidates or job-specific
        st.markdown('<div class="info-box">💡 <strong>Tip:</strong> You can send emails to candidates from all jobs or filter by specific job positions.</div>', unsafe_allow_html=True)
        
        email_mode = st.radio(
            "📧 Email Sending Mode:",
            ["Job-Specific Candidates", "All Candidates with Emails", "Cross-Job Selection"],
            help="Choose how you want to select candidates for bulk emailing"
        )
        
        # Initialize candidate pool based on mode
        if email_mode == "All Candidates with Emails":
            # Get all candidates with emails from all jobs
            all_candidates_with_email = []
            for job_title, candidates in st.session_state.shortlists.items():
                for candidate_match in candidates:
                    if candidate_match['candidate'].get('email', '').strip():
                        candidate_match['source_job'] = job_title
                        all_candidates_with_email.append(candidate_match)
            
            st.info(f"📊 Found {len(all_candidates_with_email)} total candidates with email addresses across all jobs")
            candidate_pool = all_candidates_with_email
            
        elif email_mode == "Cross-Job Selection":
            # Let user select multiple jobs first
            job_titles = list(st.session_state.shortlists.keys())
            selected_jobs = st.multiselect(
                "💼 Select Job Positions:",
                job_titles,
                default=job_titles[:2] if len(job_titles) >= 2 else job_titles
            )
            
            cross_job_candidates = []
            for job_title in selected_jobs:
                candidates = st.session_state.shortlists[job_title]
                for candidate_match in candidates:
                    if candidate_match['candidate'].get('email', '').strip():
                        candidate_match['source_job'] = job_title
                        cross_job_candidates.append(candidate_match)
            
            st.info(f"📊 Found {len(cross_job_candidates)} candidates with emails from {len(selected_jobs)} selected jobs")
            candidate_pool = cross_job_candidates
            
        else:  # Job-Specific Candidates
            job_titles = list(st.session_state.shortlists.keys())
            selected_job = st.selectbox("💼 Select Job for Bulk Email:", job_titles, key="bulk_job")
            
            if selected_job:
                candidates = st.session_state.shortlists[selected_job]
                candidates_with_email = [
                    c for c in candidates 
                    if c['candidate'].get('email', '').strip()
                ]
                # Add source job info
                for candidate_match in candidates_with_email:
                    candidate_match['source_job'] = selected_job
                
                st.info(f"📊 {len(candidates_with_email)} candidates have email addresses out of {len(candidates)} total candidates")
                candidate_pool = candidates_with_email
            else:
                candidate_pool = []
        
        if candidate_pool:
            # Template selection
            st.subheader("📝 Email Template Selection")
            templates = get_available_templates()
            selected_template = st.selectbox(
                "📝 Select Email Template:", 
                templates, 
                key="bulk_template",
                help="Choose the email template to use for all selected candidates"
            )
            
            # Enhanced candidate selection interface
            st.subheader("👥 Candidate Selection")
            
            # Filtering options
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Score filter
                if candidate_pool:
                    scores = [c.get('score', 0) for c in candidate_pool]
                    min_score = st.slider(
                        "🎯 Minimum Match Score",
                        min_value=0.0,
                        max_value=max(scores) if scores else 1.0,
                        value=0.0,
                        step=0.05,
                        help="Filter candidates by minimum matching score"
                    )
            
            with col2:
                # Company filter
                companies = list(set([c['candidate'].get('company', 'Unknown') for c in candidate_pool]))
                selected_companies = st.multiselect(
                    "🏢 Filter by Company",
                    companies,
                    default=companies,
                    help="Select specific companies to include"
                )
            
            with col3:
                # Job source filter (for cross-job mode)
                if email_mode in ["All Candidates with Emails", "Cross-Job Selection"]:
                    job_sources = list(set([c.get('source_job', 'Unknown') for c in candidate_pool]))
                    selected_job_sources = st.multiselect(
                        "💼 Filter by Source Job",
                        job_sources,
                        default=job_sources,
                        help="Filter by the job position that matched this candidate"
                    )
                else:
                    selected_job_sources = [selected_job] if 'selected_job' in locals() else []
            
            # Apply filters
            filtered_candidates = []
            for candidate_match in candidate_pool:
                candidate = candidate_match['candidate']
                score = candidate_match.get('score', 0)
                company = candidate.get('company', 'Unknown')
                source_job = candidate_match.get('source_job', 'Unknown')
                
                if (score >= min_score and 
                    company in selected_companies and 
                    (not selected_job_sources or source_job in selected_job_sources)):
                    filtered_candidates.append(candidate_match)
            
            st.info(f"📊 {len(filtered_candidates)} candidates match your filters")
            
            if filtered_candidates:
                # Display candidate selection with enhanced information
                st.markdown("**Select candidates to email:**")
                
                # Selection controls
                col1, col2, col3 = st.columns(3)
                with col1:
                    select_all_filtered = st.checkbox("✅ Select All Filtered Candidates")
                with col2:
                    select_top_n = st.checkbox("🔝 Select Top N by Score")
                with col3:
                    if select_top_n:
                        top_n = st.number_input("Number to select:", min_value=1, max_value=len(filtered_candidates), value=min(10, len(filtered_candidates)))
                
                # Create candidate options with enhanced display
                candidate_options = {}
                display_candidates = filtered_candidates.copy()
                
                # Sort by score for better display
                display_candidates.sort(key=lambda x: x.get('score', 0), reverse=True)
                
                for i, candidate_match in enumerate(display_candidates):
                    candidate = candidate_match['candidate']
                    name = candidate.get('full_name', 'Unknown')
                    email = candidate.get('email', '').strip()
                    company = candidate.get('company', 'No Company')
                    score = candidate_match.get('score', 0)
                    source_job = candidate_match.get('source_job', 'Unknown Job')
                    
                    # Create enhanced display string
                    if email_mode == "Job-Specific Candidates":
                        display_name = f"{name} | {company} | Score: {score:.2f} | {email}"
                    else:
                        display_name = f"{name} | {company} | {source_job} | Score: {score:.2f} | {email}"
                    
                    candidate_options[display_name] = {
                        'candidate_match': candidate_match,
                        'name': name,
                        'email': email,
                        'company': company,
                        'score': score,
                        'source_job': source_job
                    }
                
                # Determine default selection
                default_selection = []
                if select_all_filtered:
                    default_selection = list(candidate_options.keys())
                elif select_top_n and 'top_n' in locals():
                    default_selection = list(candidate_options.keys())[:top_n]
                
                selected_candidate_keys = st.multiselect(
                    "Select candidates:",
                    list(candidate_options.keys()),
                    default=default_selection,
                    key="enhanced_bulk_candidates",
                    help="Select the candidates you want to email. Use Ctrl+Click to select multiple."
                )
                
                # Preview selected candidates
                if selected_candidate_keys:
                    with st.expander(f"👁️ Preview Selected Candidates ({len(selected_candidate_keys)} selected)", expanded=False):
                        preview_data = []
                        for key in selected_candidate_keys:
                            candidate_info = candidate_options[key]
                            preview_data.append({
                                'Name': candidate_info['name'],
                                'Email': candidate_info['email'],
                                'Company': candidate_info['company'],
                                'Score': f"{candidate_info['score']:.2f}",
                                'Source Job': candidate_info['source_job']
                            })
                        
                        preview_df = pd.DataFrame(preview_data)
                        st.dataframe(preview_df, use_container_width=True)
                
                # Send bulk emails
                if selected_candidate_keys:
                    st.markdown("---")
                    st.subheader(f"🚀 Ready to Send {len(selected_candidate_keys)} Emails")
                    
                    # Email preview option
                    if st.button("👁️ Preview Email Template"):
                        sample_candidate = candidate_options[selected_candidate_keys[0]]
                        preview = email_manager.preview_email(
                            sample_candidate['name'],
                            sample_candidate['source_job'],
                            selected_template
                        )
                        st.text_area("Email Preview (for first selected candidate):", preview, height=200)
                    
                    # Confirmation and sending
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        confirm_send = st.checkbox(
                            f"⚠️ I confirm sending {len(selected_candidate_keys)} emails",
                            help="Please confirm before sending bulk emails"
                        )
                    
                    with col2:
                        send_with_delay = st.checkbox(
                            "⏰ Add delay between emails",
                            value=True,
                            help="Add a small delay between emails to avoid being flagged as spam"
                        )
                    
                    if st.button("📨 Send Bulk Emails", type="primary", disabled=not confirm_send):
                        with st.spinner(f"Sending {len(selected_candidate_keys)} emails..."):
                            # Prepare candidates for email manager
                            selected_candidates_for_email = [candidate_options[key]['name'] for key in selected_candidate_keys]
                            
                            # Create a custom shortlist for the email manager
                            if email_mode == "Job-Specific Candidates":
                                email_shortlists = {selected_job: candidate_pool}
                                target_job = selected_job
                            else:
                                # For cross-job emails, group by source job
                                email_shortlists = {}
                                for key in selected_candidate_keys:
                                    candidate_info = candidate_options[key]
                                    source_job = candidate_info['source_job']
                                    if source_job not in email_shortlists:
                                        email_shortlists[source_job] = []
                                    email_shortlists[source_job].append(candidate_info['candidate_match'])
                                
                                # Use the most common source job as target
                                target_job = max(email_shortlists.keys(), key=lambda x: len(email_shortlists[x]))
                            
                            # Send emails
                            results = email_manager.send_bulk_emails_to_job_candidates(
                                email_shortlists,
                                target_job,
                                selected_candidates_for_email,
                                selected_template
                            )
                            
                            # Display results
                            st.markdown("---")
                            st.subheader("📊 Bulk Email Results")
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("✅ Sent Successfully", results.get('emails_sent', 0))
                            with col2:
                                st.metric("❌ Failed", results.get('emails_failed', 0))
                            with col3:
                                st.metric("📊 Total Processed", results.get('total_candidates', 0))
                            
                            # Show detailed results
                            if results.get('sent_to'):
                                with st.expander("✅ Successfully sent to:", expanded=True):
                                    for recipient in results['sent_to']:
                                        st.write(f"   • {recipient['name']} ({recipient['email']})")
                            
                            if results.get('failed_to'):
                                with st.expander("❌ Failed to send to:", expanded=True):
                                    for failed in results['failed_to']:
                                        st.write(f"   • {failed['name']}: {failed['reason']}")
                            
                            # Update session state
                            st.session_state.email_log.extend(email_manager.email_log)
                            
                            # Success message
                            if results.get('emails_sent', 0) > 0:
                                st.success(f"🎉 Successfully sent {results.get('emails_sent', 0)} emails!")
            else:
                st.warning("⚠️ No candidates match your current filters. Try adjusting the filter criteria.")        
        else:
            st.warning("⚠️ No candidates with email addresses found for the selected criteria.")
    
    def email_templates_interface(self):
        """Interface for managing email templates"""
        st.subheader("📋 Email Templates")
        
        templates = get_available_templates()
        
        for template_name in templates:
            with st.expander(f"📝 {template_name.replace('_', ' ').title()}"):
                try:
                    template = get_email_template(template_name)
                    
                    st.write("**Subject:**")
                    st.code(template['subject'])
                    
                    st.write("**Body:**")
                    st.text_area(f"Body for {template_name}:", template['body'], height=200, key=f"template_{template_name}")
                    
                except Exception as e:
                    st.error(f"Error loading template: {e}")
    
    def documents_page(self):
        """Document generation page"""
        st.markdown('<h2 class="main-header">📄 Document Generation</h2>', unsafe_allow_html=True)
        
        if not st.session_state.shortlists:
            st.warning("⚠️ No shortlists available. Please generate shortlists first.")
            return
        
        st.subheader("📋 Select Candidates for Document Generation")
        
        # Job selection
        job_titles = list(st.session_state.shortlists.keys())
        selected_job = st.selectbox("💼 Select Job Position:", job_titles, key="doc_job")
        
        if selected_job:
            candidates = st.session_state.shortlists[selected_job]
            
            st.write(f"👥 {len(candidates)} candidates available for {selected_job}")
            
            # Candidate selection
            candidate_options = {}
            for i, candidate_match in enumerate(candidates):
                candidate = candidate_match['candidate']
                name = candidate.get('full_name', f'Candidate {i+1}')
                score = candidate_match.get('score', 0)
                candidate_options[f"{name} (Score: {score:.2f})"] = candidate_match
            
            selected_candidates_keys = st.multiselect(
                "Select candidates for document generation:",
                list(candidate_options.keys())
            )
            
            if selected_candidates_keys:
                selected_candidate_matches = [candidate_options[key] for key in selected_candidates_keys]
                
                # Document options
                col1, col2 = st.columns(2)
                with col1:
                    doc_format = st.selectbox(
                        "📄 Document Format:",
                        ["Word Document (.docx)", "Text File (.txt)"]
                    )
                
                with col2:
                    include_enhanced = st.checkbox(
                        "🔍 Include Enhanced Profile Data",
                        help="Include additional profile information if available"
                    )
                
                # Generate documents
                if st.button("📄 Generate Documents", type="primary"):
                    with st.spinner(f"Generating documents for {len(selected_candidate_matches)} candidates..."):
                        try:
                            doc_generator = CandidateDocumentGenerator()
                            
                            generated_files = []
                            progress_bar = st.progress(0)
                            
                            for i, candidate_match in enumerate(selected_candidate_matches):
                                candidate = candidate_match['candidate']
                                candidate_name = candidate.get('full_name', f'Candidate_{i+1}')
                                
                                if doc_format == "Word Document (.docx)":
                                    filename = doc_generator.generate_candidate_summary(
                                        candidate_match,
                                        selected_job,
                                        candidate_name.replace(' ', '_')
                                    )
                                else:
                                    # Generate text file
                                    filename = f"{candidate_name.replace(' ', '_')}_summary.txt"
                                    doc_generator.generate_text_summary(
                                        candidate_match,
                                        selected_job,
                                        filename
                                    )
                                
                                generated_files.append(filename)
                                progress_bar.progress((i + 1) / len(selected_candidate_matches))
                            
                            progress_bar.empty()
                            
                            st.success(f"✅ Generated {len(generated_files)} documents successfully!")
                            
                            # List generated files
                            st.subheader("📁 Generated Files:")
                            for filename in generated_files:
                                if os.path.exists(filename):
                                    file_size = os.path.getsize(filename)
                                    st.write(f"📄 {filename} ({file_size} bytes)")
                                else:
                                    st.write(f"⚠️ {filename} (file may not exist)")
                            
                        except Exception as e:
                            st.error(f"❌ Error generating documents: {e}")
    
    def team_members_page(self):
        """Team members management page"""
        st.markdown('<h2 class="main-header">👥 Team Members</h2>', unsafe_allow_html=True)
        
        # Initialize team members in session state
        if 'team_members' not in st.session_state:
            st.session_state.team_members = []
        
        # Team overview metrics
        st.subheader("📊 Team Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("👥 Total Members", len(st.session_state.team_members))
        with col2:
            active_members = sum(1 for member in st.session_state.team_members if member.get('status') == 'Active')
            st.metric("✅ Active Members", active_members)
        with col3:
            departments = set(member.get('department', 'Unknown') for member in st.session_state.team_members)
            st.metric("🏢 Departments", len(departments))
        with col4:
            roles = set(member.get('role', 'Unknown') for member in st.session_state.team_members)
            st.metric("💼 Roles", len(roles))
        
        # Tabs for team management features
        tab1, tab2 = st.tabs(["👥 View All Members", "📊 Team Analytics"])
        
        with tab1:
            self.view_team_members()
        
        with tab2:
            self.team_analytics()
    
    
    def view_team_members(self):
        """Interface for viewing all team members"""
        st.subheader("👥 All Team Members")
        
        if not st.session_state.team_members:
            st.info("📝 No team members added yet. Add your first team member using the 'Add Team Member' tab.")
            return
        
        # Filters and sorting
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Department filter
            departments = sorted(set(member.get('department', 'Unknown') for member in st.session_state.team_members))
            selected_departments = st.multiselect(
                "Filter by Department:",
                departments,
                default=departments
            )
        
        with col2:
            # Status filter
            statuses = sorted(set(member.get('status', 'Unknown') for member in st.session_state.team_members))
            selected_statuses = st.multiselect(
                "Filter by Status:",
                statuses,
                default=statuses
            )
        
        with col3:
            # Employment type filter
            employment_types = sorted(set(member.get('employment_type', 'Unknown') for member in st.session_state.team_members))
            selected_employment_types = st.multiselect(
                "Filter by Employment Type:",
                employment_types,
                default=employment_types
            )
        
        with col4:
            # Sort options
            sort_by = st.selectbox(
                "Sort by:",
                ["Name (A-Z)", "Name (Z-A)", "Department", "Role", "Start Date (Recent)", "Start Date (Oldest)"]
            )
        
        # Filter team members
        filtered_members = [
            member for member in st.session_state.team_members
            if (member.get('department', 'Unknown') in selected_departments and
                member.get('status', 'Unknown') in selected_statuses and
                member.get('employment_type', 'Unknown') in selected_employment_types)
        ]
        
        # Sort team members
        if sort_by == "Name (A-Z)":
            filtered_members.sort(key=lambda x: x['full_name'].lower())
        elif sort_by == "Name (Z-A)":
            filtered_members.sort(key=lambda x: x['full_name'].lower(), reverse=True)
        elif sort_by == "Department":
            filtered_members.sort(key=lambda x: x.get('department', 'Unknown').lower())
        elif sort_by == "Role":
            filtered_members.sort(key=lambda x: x.get('role', 'Unknown').lower())
        elif sort_by == "Start Date (Recent)":
            filtered_members.sort(key=lambda x: x.get('start_date', '1900-01-01'), reverse=True)
        else:  # Start Date (Oldest)
            filtered_members.sort(key=lambda x: x.get('start_date', '1900-01-01'))
        
        st.info(f"📊 Showing {len(filtered_members)} of {len(st.session_state.team_members)} team members")
        
        # Display team members
        for i, member in enumerate(filtered_members, 1):
            # Create status indicator
            status_emoji = {"Active": "🟢", "Inactive": "🔴", "On Leave": "🟡"}
            status_icon = status_emoji.get(member.get('status'), "⚪")
            
            with st.expander(f"{status_icon} {i}. {member['full_name']} - {member.get('role', 'Unknown Role')} ({member.get('department', 'Unknown Dept')})"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**👤 Name:** {member['full_name']}")
                    st.write(f"**📧 Email:** {member['email']}")
                    st.write(f"**📱 Phone:** {member.get('phone', 'Not provided')}")
                    st.write(f"**💼 Role:** {member.get('role', 'Not specified')}")
                
                with col2:
                    st.write(f"**🏢 Department:** {member.get('department', 'Not specified')}")
                    st.write(f"**📊 Status:** {status_icon} {member.get('status', 'Unknown')}")
                    st.write(f"**📅 Start Date:** {member.get('start_date', 'Not specified')}")
                    st.write(f"**📍 Location:** {member.get('location', 'Not specified')}")
                
                with col3:
                    st.write(f"**👔 Employment Type:** {member.get('employment_type', 'Not specified')}")
                    st.write(f"**👨‍💼 Reports To:** {member.get('manager', 'Not specified')}")
                    linkedin_url = member.get('linkedin_url')
                    if linkedin_url:
                        st.write(f"**🔗 LinkedIn:** [Profile Link]({linkedin_url})")
                    else:
                        st.write(f"**🔗 LinkedIn:** Not provided")
                    st.write(f"**🆔 Member ID:** {member.get('id', 'Unknown')}")
                    st.write(f"**🕒 Added:** {member.get('created_at', 'Unknown')[:16] if member.get('created_at') else 'Unknown'}")
                
                # Skills and notes
                if member.get('skills'):
                    st.write(f"**🔧 Skills:** {member['skills']}")
                
                if member.get('notes'):
                    st.write(f"**📝 Notes:** {member['notes']}")
                
    
    def team_analytics(self):
        """Team analytics and insights"""
        st.subheader("📊 Team Analytics")
        
        if not st.session_state.team_members:
            st.info("📝 No team members to analyze. Add team members first.")
            return
        
        # Department distribution
        st.subheader("🏢 Department Distribution")
        dept_counts = {}
        for member in st.session_state.team_members:
            dept = member.get('department', 'Unknown')
            dept_counts[dept] = dept_counts.get(dept, 0) + 1
        
        if dept_counts:
            dept_df = pd.DataFrame(list(dept_counts.items()), columns=['Department', 'Count'])
            fig1 = px.pie(dept_df, values='Count', names='Department', title='Team Members by Department')
            st.plotly_chart(fig1, use_container_width=True)
        
        # Status distribution
        st.subheader("📊 Status Distribution")
        status_counts = {}
        for member in st.session_state.team_members:
            status = member.get('status', 'Unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        if status_counts:
            col1, col2 = st.columns(2)
            
            with col1:
                status_df = pd.DataFrame(list(status_counts.items()), columns=['Status', 'Count'])
                fig2 = px.bar(status_df, x='Status', y='Count', title='Team Members by Status')
                st.plotly_chart(fig2, use_container_width=True)
            
            with col2:
                # Employment type distribution
                employment_counts = {}
                for member in st.session_state.team_members:
                    emp_type = member.get('employment_type', 'Unknown')
                    employment_counts[emp_type] = employment_counts.get(emp_type, 0) + 1
                
                if employment_counts:
                    emp_df = pd.DataFrame(list(employment_counts.items()), columns=['Employment Type', 'Count'])
                    fig3 = px.bar(emp_df, x='Employment Type', y='Count', title='Team Members by Employment Type')
                    st.plotly_chart(fig3, use_container_width=True)
        
        # Recent additions
        st.subheader("📅 Recent Additions")
        recent_members = sorted(
            st.session_state.team_members, 
            key=lambda x: x.get('created_at', '1900-01-01T00:00:00'), 
            reverse=True
        )[:5]  # Last 5 added
        
        if recent_members:
            for member in recent_members:
                created_date = member.get('created_at', 'Unknown')
                if created_date != 'Unknown':
                    created_date = created_date[:10]  # Just the date part
                st.write(f"• **{member['full_name']}** ({member.get('role', 'Unknown Role')}) - Added: {created_date}")
        
        # Export team data
        st.subheader("💾 Export Team Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 Export Team List"):
                if st.session_state.team_members:
                    # Create CSV data
                    team_data = []
                    for member in st.session_state.team_members:
                        team_data.append({
                            'ID': member.get('id', ''),
                            'Name': member.get('full_name', ''),
                            'Email': member.get('email', ''),
                            'Phone': member.get('phone', ''),
                            'Role': member.get('role', ''),
                            'Department': member.get('department', ''),
                            'Status': member.get('status', ''),
                            'Start Date': member.get('start_date', ''),
                            'Manager': member.get('manager', ''),
                            'Location': member.get('location', ''),
                            'Employment Type': member.get('employment_type', ''),
                            'Skills': member.get('skills', ''),
                            'Notes': member.get('notes', '')
                        })
                    
                    csv_df = pd.DataFrame(team_data)
                    csv_str = csv_df.to_csv(index=False)
                    
                    st.download_button(
                        label="📥 Download Team CSV",
                        data=csv_str,
                        file_name=f"team_members_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
        
        with col2:
            if st.button("📋 Export Team JSON"):
                if st.session_state.team_members:
                    json_str = json.dumps(st.session_state.team_members, indent=2, ensure_ascii=False)
                    st.download_button(
                        label="📥 Download Team JSON",
                        data=json_str,
                        file_name=f"team_members_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )

    def analytics_page(self):
        """Analytics and reporting page"""
        st.markdown('<h2 class="main-header">📈 Analytics & Reports</h2>', unsafe_allow_html=True)
        
        if not st.session_state.shortlists:
            st.warning("⚠️ No data available for analytics. Please generate shortlists first.")
            return
        
        # Overview metrics
        st.subheader("📊 Overview Metrics")
        
        total_candidates = len(st.session_state.candidates_data)
        total_matches = sum(len(candidates) for candidates in st.session_state.shortlists.values())
        total_jobs = len(st.session_state.shortlists)
        emails_sent = len(st.session_state.email_log)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("👥 Total Candidates", total_candidates)
        with col2:
            st.metric("🎯 Total Matches", total_matches)
        with col3:
            st.metric("💼 Jobs Processed", total_jobs)
        with col4:
            st.metric("📧 Emails Sent", emails_sent)
        
        # Detailed analytics
        st.subheader("📈 Detailed Analytics")
        
        # Job performance chart
        if st.session_state.shortlists:
            job_data = []
            for job_title, candidates in st.session_state.shortlists.items():
                candidates_with_email = sum(1 for c in candidates if c['candidate'].get('email', '').strip())
                avg_score = sum(c.get('score', 0) for c in candidates) / len(candidates) if candidates else 0
                
                job_data.append({
                    'Job': job_title,
                    'Total Matches': len(candidates),
                    'With Email': candidates_with_email,
                    'Average Score': avg_score
                })
            
            df = pd.DataFrame(job_data)
            
            # Charts
            col1, col2 = st.columns(2)
            
            with col1:
                fig1 = px.bar(df, x='Job', y='Total Matches', title='Matches per Job Position')
                fig1.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                fig2 = px.bar(df, x='Job', y='Average Score', title='Average Match Score by Job')
                fig2.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig2, use_container_width=True)
            
            # Email status chart
            if candidates_with_email > 0:
                email_data = pd.DataFrame({
                    'Status': ['With Email', 'Without Email'],
                    'Count': [
                        sum(df['With Email']),
                        sum(df['Total Matches']) - sum(df['With Email'])
                    ]
                })
                
                fig3 = px.pie(email_data, values='Count', names='Status', 
                            title='Candidates Email Availability')
                st.plotly_chart(fig3, use_container_width=True)
        
        # Email analytics
        if st.session_state.email_log:
            st.subheader("📧 Email Analytics")
            
            email_df = pd.DataFrame(st.session_state.email_log)
            
            if not email_df.empty:
                # Email success rate
                success_rate = email_df['success'].mean() * 100 if 'success' in email_df.columns else 0
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("📈 Email Success Rate", f"{success_rate:.1f}%")
                
                with col2:
                    st.metric("📅 Last Email Sent", 
                             email_df['timestamp'].max() if 'timestamp' in email_df.columns else "N/A")
                
                # Email timeline
                if 'timestamp' in email_df.columns:
                    email_df['date'] = pd.to_datetime(email_df['timestamp']).dt.date
                    daily_emails = email_df.groupby('date').size().reset_index(name='count')
                    
                    fig4 = px.line(daily_emails, x='date', y='count', 
                                 title='Emails Sent Over Time')
                    st.plotly_chart(fig4, use_container_width=True)
        
        # Export data
        st.subheader("💾 Export Data")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Export Shortlists"):
                if st.session_state.shortlists:
                    json_str = json.dumps(st.session_state.shortlists, indent=2, ensure_ascii=False)
                    st.download_button(
                        label="📥 Download Shortlists JSON",
                        data=json_str,
                        file_name=f"shortlists_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
        
        with col2:
            if st.button("📧 Export Email Log"):
                if st.session_state.email_log:
                    json_str = json.dumps(st.session_state.email_log, indent=2, ensure_ascii=False)
                    st.download_button(
                        label="📥 Download Email Log JSON",
                        data=json_str,
                        file_name=f"email_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
        
        with col3:
            if st.button("📈 Export Analytics"):
                if st.session_state.shortlists:
                    # Create summary report
                    report = {
                        'generated_at': datetime.now().isoformat(),
                        'total_candidates': total_candidates,
                        'total_matches': total_matches,
                        'total_jobs': total_jobs,
                        'emails_sent': emails_sent,
                        'job_statistics': job_data if 'job_data' in locals() else []
                    }
                    
                    json_str = json.dumps(report, indent=2, ensure_ascii=False)
                    st.download_button(
                        label="📥 Download Analytics Report",
                        data=json_str,
                        file_name=f"analytics_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )

def main():
    """Main application function"""
    app = HRAutomationApp()
    
    # Sidebar navigation
    st.sidebar.title("🎯 HR Automation")
    st.sidebar.markdown("---")
    
    # Load data on startup
    if st.sidebar.button("🔄 Load Data Files"):
        app.load_data_files()
    
    # Navigation
    pages = {
        "🏠 Dashboard": app.dashboard_page,
        "👤 Candidate Management": app.candidate_management_page,
        "💼 Job Management": app.job_management_page,
        "🎯 Candidate Shortlisting": app.shortlisting_page,
        "📧 Email Management": app.email_page,
        "📄 Document Generation": app.documents_page,
        "👥 Team Members": app.team_members_page,
        "📈 Analytics & Reports": app.analytics_page
    }
    
    selected_page = st.sidebar.selectbox("Navigate to:", list(pages.keys()))
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📁 Data Status")
    st.sidebar.metric("👥 Candidates", len(st.session_state.candidates_data))
    st.sidebar.metric("💼 Jobs", len(st.session_state.jobs_data))
    st.sidebar.metric("📊 Shortlists", len(st.session_state.shortlists))
    
    # Run selected page
    pages[selected_page]()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("🤖 **HR Automation System v1.0**")
    st.sidebar.markdown("Built with Streamlit")

if __name__ == "__main__":
    main()
