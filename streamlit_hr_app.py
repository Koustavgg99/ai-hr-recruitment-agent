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
    DATABASE_AVAILABLE = True
except ImportError as e:
    st.error(f"Import error: {e}")
    st.error("Please ensure all required modules are in the same directory")
    DATABASE_AVAILABLE = False

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 1rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #ffeaa7;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #f5c6cb;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

class HRAutomationApp:
    """Main HR Automation Streamlit Application"""
    
    def __init__(self):
        self.init_session_state()
        
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
    
    def load_data_files(self):
        """Load and validate data files"""
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
                
            return True
            
        except Exception as e:
            st.error(f"❌ Error loading data: {e}")
            return False
    
    def dashboard_page(self):
        """Main dashboard page"""
        st.markdown('<h1 class="main-header">🎯 HR Automation Dashboard</h1>', unsafe_allow_html=True)
        
        # Load data files
        with st.expander("📁 Data Files Status", expanded=True):
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
        """Interface for adding new candidates"""
        st.subheader("➕ Add New Candidate")
        
        with st.form("add_candidate_form"):
            # Basic information
            col1, col2 = st.columns(2)
            
            with col1:
                full_name = st.text_input(
                    "Full Name *",
                    placeholder="e.g., John Doe",
                    help="Enter the candidate's full name"
                )
                
                email = st.text_input(
                    "Email Address",
                    placeholder="e.g., john.doe@example.com",
                    help="Enter the candidate's email address"
                )
                
                linkedin_url = st.text_input(
                    "LinkedIn URL *",
                    placeholder="e.g., https://linkedin.com/in/johndoe",
                    help="Enter the candidate's LinkedIn profile URL"
                )
            
            with col2:
                company = st.text_input(
                    "Current Company",
                    placeholder="e.g., Tech Solutions Inc.",
                    help="Enter the candidate's current company"
                )
                
                position = st.text_input(
                    "Current Position",
                    placeholder="e.g., Senior Software Engineer",
                    help="Enter the candidate's current job title"
                )
                
                location = st.text_input(
                    "Location",
                    placeholder="e.g., New York, NY",
                    help="Enter the candidate's location"
                )
            
            # Additional information
            st.subheader("Additional Information")
            
            col1, col2 = st.columns(2)
            
            with col1:
                skills = st.text_area(
                    "Skills (comma-separated)",
                    placeholder="e.g., Python, JavaScript, React, Node.js, AWS",
                    height=100,
                    help="List the candidate's technical skills"
                )
            
            with col2:
                experience_summary = st.text_area(
                    "Experience Summary",
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
        """Interface for creating new job descriptions"""
        st.subheader("📝 Create New Job Description")
        
        with st.form("job_creation_form"):
            # Basic job information
            col1, col2 = st.columns(2)
            
            with col1:
                job_title = st.text_input(
                    "Job Title *", 
                    placeholder="e.g., Senior Python Developer"
                )
                
                company_name = st.text_input(
                    "Company Name *",
                    placeholder="e.g., Tech Solutions Inc."
                )
                
                location = st.text_input(
                    "Location",
                    placeholder="e.g., Remote, New York, NY"
                )
            
            with col2:
                department = st.text_input(
                    "Department",
                    placeholder="e.g., Engineering, Marketing"
                )
                
                experience_level = st.selectbox(
                    "Experience Level",
                    ["Entry Level (0-2 years)", "Mid Level (3-5 years)", "Senior Level (6-10 years)", "Lead/Principal (10+ years)"]
                )
                
                employment_type = st.selectbox(
                    "Employment Type",
                    ["Full-time", "Part-time", "Contract", "Internship"]
                )
            
            # Job description
            st.subheader("Job Description")
            job_description = st.text_area(
                "Job Description *",
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
                st.subheader("Required Skills")
                required_skills_input = st.text_area(
                    "Required Skills (one per line) *",
                    height=150,
                    placeholder="""Python
Django
PostgreSQL
REST APIs
Git"""
                )
            
            with col2:
                st.subheader("Preferred Skills")
                preferred_skills_input = st.text_area(
                    "Preferred Skills (one per line)",
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
                            display_data.append({
                                'Name': candidate.get('full_name', 'Unknown'),
                                'Email': candidate.get('email', 'Not available'),
                                'Company': candidate.get('company', 'Not available'),
                                'Position': candidate.get('position', 'Not available'),
                                'Score': f"{candidate_match['score']:.2f}",
                                'Matched Skills': ', '.join(candidate_match.get('matched_skills', [])[:3])
                            })
                        
                        df = pd.DataFrame(display_data)
                        st.dataframe(df, use_container_width=True)
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
        st.subheader("📨 Bulk Email Sending")
        
        # Job selection
        job_titles = list(st.session_state.shortlists.keys())
        selected_job = st.selectbox("💼 Select Job for Bulk Email:", job_titles, key="bulk_job")
        
        if selected_job:
            candidates = st.session_state.shortlists[selected_job]
            candidates_with_email = [
                c for c in candidates 
                if c['candidate'].get('email', '').strip()
            ]
            
            st.info(f"📊 {len(candidates_with_email)} candidates have email addresses out of {len(candidates)} total candidates")
            
            if candidates_with_email:
                # Template selection
                templates = get_available_templates()
                selected_template = st.selectbox("📝 Bulk Email Template:", templates, key="bulk_template")
                
                # Candidate selection
                st.subheader("👥 Select Candidates")
                
                candidate_names = [c['candidate'].get('full_name', 'Unknown') for c in candidates_with_email]
                
                select_all = st.checkbox("✅ Select All Candidates")
                if select_all:
                    selected_candidates = st.multiselect(
                        "Candidates to email:",
                        candidate_names,
                        default=candidate_names,
                        key="bulk_candidates"
                    )
                else:
                    selected_candidates = st.multiselect(
                        "Candidates to email:",
                        candidate_names,
                        key="bulk_candidates_manual"
                    )
                
                # Send bulk emails
                if selected_candidates:
                    st.write(f"📧 Ready to send {len(selected_candidates)} emails")
                    
                    if st.button("📨 Send Bulk Emails", type="primary"):
                        if st.checkbox("⚠️ I confirm sending bulk emails", key="bulk_confirm"):
                            with st.spinner(f"Sending {len(selected_candidates)} emails..."):
                                results = email_manager.send_bulk_emails_to_job_candidates(
                                    st.session_state.shortlists,
                                    selected_job,
                                    selected_candidates,
                                    selected_template
                                )
                                
                                # Display results
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
                                    st.success("✅ Successfully sent to:")
                                    for recipient in results['sent_to']:
                                        st.write(f"   • {recipient['name']} ({recipient['email']})")
                                
                                if results.get('failed_to'):
                                    st.error("❌ Failed to send to:")
                                    for failed in results['failed_to']:
                                        st.write(f"   • {failed['name']}: {failed['reason']}")
                                
                                # Update session state
                                st.session_state.email_log.extend(email_manager.email_log)
                        else:
                            st.warning("⚠️ Please confirm before sending bulk emails")
            else:
                st.warning("⚠️ No candidates with email addresses found")
    
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
