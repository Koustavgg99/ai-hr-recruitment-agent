import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from dotenv import load_dotenv
import sys

# Add the src directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from hr_agent import HRRecruitmentAgent
from reporting import ReportGenerator
from database import HRDatabase

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI HR Recruitment Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'hr_agent' not in st.session_state:
    try:
        config = {
            'google_api_key': os.getenv('GOOGLE_API_KEY'),
            'ollama_host': os.getenv('OLLAMA_HOST', 'http://localhost:11434'),
            'ollama_model': os.getenv('OLLAMA_MODEL', 'llama3.1:8b'),
            'database_path': os.getenv('DATABASE_PATH', './data/hr_recruitment.db')
        }
        
        if not config['google_api_key']:
            st.error("❌ Google API Key not found. Please set GOOGLE_API_KEY in your .env file.")
            st.stop()
        
        st.session_state.hr_agent = HRRecruitmentAgent(config)
        st.session_state.report_generator = ReportGenerator(st.session_state.hr_agent)
        st.success("✅ HR Agent initialized successfully!")
        
    except Exception as e:
        st.error(f"❌ Failed to initialize HR Agent: {e}")
        st.stop()

def main():
    st.title("🤖 AI HR Recruitment Agent")
    st.markdown("Automate your recruitment process with AI-powered sourcing, screening, and outreach.")
    
    # Sidebar navigation
    with st.sidebar:
        st.header("Navigation")
        page = st.selectbox(
            "Choose a page:",
            ["Dashboard", "Job Management", "Candidate Sourcing", "Outreach Campaigns", "Reports", "Settings"]
        )
    
    if page == "Dashboard":
        show_dashboard()
    elif page == "Job Management":
        show_job_management()
    elif page == "Candidate Sourcing":
        show_candidate_sourcing()
    elif page == "Outreach Campaigns":
        show_outreach_campaigns()
    elif page == "Reports":
        show_reports()
    elif page == "Settings":
        show_settings()

def show_dashboard():
    st.header("📊 Recruitment Dashboard")
    
    # Get pipeline status
    pipeline = st.session_state.hr_agent.get_pipeline_status()
    today_metrics = st.session_state.hr_agent.db.get_daily_metrics()
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Active Jobs", pipeline['active_jobs'])
    with col2:
        st.metric("Total Candidates", pipeline['total_candidates'])
    with col3:
        st.metric("Contacted Today", today_metrics['candidates_contacted'])
    with col4:
        response_rate = (pipeline['responded_candidates'] / pipeline['contacted_candidates'] * 100) if pipeline['contacted_candidates'] > 0 else 0
        st.metric("Response Rate", f"{response_rate:.1f}%")
    
    # Charts
    try:
        charts = st.session_state.report_generator.create_dashboard_charts()
        
        if 'trend' in charts:
            st.subheader("📈 Weekly Trend")
            st.plotly_chart(charts['trend'], use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'pipeline' in charts:
                st.subheader("📋 Job Pipeline")
                st.plotly_chart(charts['pipeline'], use_container_width=True)
        
        with col2:
            if 'response_rate' in charts:
                st.subheader("📧 Response Rate")
                st.plotly_chart(charts['response_rate'], use_container_width=True)
    
    except Exception as e:
        st.warning(f"Could not generate charts: {e}")
    
    # Recent activity
    st.subheader("🔄 Recent Activity")
    try:
        candidates_df = st.session_state.report_generator.generate_candidate_performance_table()
        if not candidates_df.empty:
            st.dataframe(candidates_df.head(10), use_container_width=True)
        else:
            st.info("No candidates in the pipeline yet. Start by adding a job and sourcing candidates!")
    except Exception as e:
        st.error(f"Error loading candidates: {e}")

def show_job_management():
    st.header("💼 Job Management")
    
    tab1, tab2 = st.tabs(["Add New Job", "Manage Existing Jobs"])
    
    with tab1:
        st.subheader("➕ Post New Job")
        
        with st.form("job_form"):
            company = st.text_input("Company Name", value="TechCorp")
            job_description = st.text_area(
                "Job Description", 
                placeholder="Paste the complete job description here...",
                height=300
            )
            
            submitted = st.form_submit_button("🔍 Analyze & Post Job")
            
            if submitted and job_description:
                with st.spinner("Analyzing job description with AI..."):
                    try:
                        job_id = st.session_state.hr_agent.process_job_description(job_description, company)
                        st.success(f"✅ Job posted successfully! Job ID: {job_id}")
                        st.balloons()
                    except Exception as e:
                        st.error(f"❌ Error posting job: {e}")
    
    with tab2:
        st.subheader("📋 Existing Jobs")
        
        try:
            jobs = st.session_state.hr_agent.db.get_jobs()
            
            if jobs:
                for job in jobs:
                    with st.expander(f"🔸 {job['title']} at {job['company']}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**Job ID:** {job['id']}")
                            st.write(f"**Location:** {job['location']}")
                            st.write(f"**Experience Level:** {job['experience_level']}")
                            st.write(f"**Posted:** {job['posted_date']}")
                        
                        with col2:
                            st.write(f"**Required Skills:** {', '.join(job['required_skills'])}")
                            candidates = st.session_state.hr_agent.db.get_candidates_by_job(job['id'])
                            st.write(f"**Candidates:** {len(candidates)}")
                            st.write(f"**Status:** {job['status'].title()}")
                        
                        if st.button(f"🔎 Source Candidates", key=f"source_{job['id']}"):
                            st.rerun()
            else:
                st.info("No jobs posted yet. Add your first job in the 'Add New Job' tab!")
        
        except Exception as e:
            st.error(f"Error loading jobs: {e}")

def show_candidate_sourcing():
    st.header("🔎 Candidate Sourcing")
    
    # Get available jobs
    jobs = st.session_state.hr_agent.db.get_jobs()
    
    if not jobs:
        st.warning("No jobs available. Please add a job first in the Job Management section.")
        return
    
    # Job selection
    job_options = {f"{job['title']} at {job['company']} (ID: {job['id']})": job['id'] for job in jobs}
    selected_job_text = st.selectbox("Select Job to Source Candidates For:", list(job_options.keys()))
    selected_job_id = job_options[selected_job_text]
    
    # Sourcing parameters
    col1, col2 = st.columns(2)
    with col1:
        max_candidates = st.slider("Maximum Candidates to Source", 5, 50, 20)
    with col2:
        min_match_score = st.slider("Minimum Match Score", 0.0, 1.0, 0.6, 0.1)
    
    # Source candidates
    if st.button("🚀 Start Candidate Sourcing"):
        with st.spinner("Sourcing candidates..."):
            try:
                candidates = st.session_state.hr_agent.source_candidates(selected_job_id, max_candidates)
                
                if candidates:
                    st.success(f"✅ Sourced {len(candidates)} candidates!")
                    
                    # Show candidates table
                    candidates_df = pd.DataFrame(candidates)
                    st.dataframe(
                        candidates_df[['name', 'email', 'skills', 'experience_years', 'location', 'match_score']], 
                        use_container_width=True
                    )
                    
                    # Generate outreach for top candidates
                    if st.button("📧 Generate Outreach Emails"):
                        with st.spinner("Generating personalized emails..."):
                            campaigns = st.session_state.hr_agent.generate_outreach_campaigns(
                                selected_job_id, min_match_score, 10
                            )
                            st.success(f"✅ Generated {len(campaigns)} outreach emails!")
                            
                            # Show preview of emails
                            for i, campaign in enumerate(campaigns[:3]):
                                with st.expander(f"📧 Email for {campaign['candidate_name']} (Score: {campaign['match_score']:.2f})"):
                                    st.text_area("Email Content:", campaign['email_content'], height=200, key=f"email_{i}")
                else:
                    st.info("No candidates found matching the criteria.")
                    
            except Exception as e:
                st.error(f"❌ Error sourcing candidates: {e}")
    
    # Show existing candidates for this job
    st.subheader("👥 Current Candidates")
    try:
        existing_candidates = st.session_state.hr_agent.db.get_candidates_by_job(selected_job_id)
        if existing_candidates:
            df = pd.DataFrame(existing_candidates)
            st.dataframe(
                df[['name', 'email', 'experience_years', 'location', 'match_score', 'response_status']], 
                use_container_width=True
            )
        else:
            st.info("No candidates sourced for this job yet.")
    except Exception as e:
        st.error(f"Error loading existing candidates: {e}")

def show_outreach_campaigns():
    st.header("📧 Outreach Campaigns")
    
    # Get available jobs
    jobs = st.session_state.hr_agent.db.get_jobs()
    
    if not jobs:
        st.warning("No jobs available. Please add a job first.")
        return
    
    # Job selection
    job_options = {f"{job['title']} at {job['company']} (ID: {job['id']})": job['id'] for job in jobs}
    selected_job_text = st.selectbox("Select Job for Outreach:", list(job_options.keys()))
    selected_job_id = job_options[selected_job_text]
    
    # Campaign settings
    col1, col2 = st.columns(2)
    with col1:
        min_match_score = st.slider("Minimum Match Score for Outreach", 0.0, 1.0, 0.7, 0.1)
    with col2:
        max_outreach = st.slider("Maximum Candidates to Contact", 1, 20, 10)
    
    # Generate campaign
    if st.button("🎯 Generate Outreach Campaign"):
        with st.spinner("Generating personalized outreach emails..."):
            try:
                campaigns = st.session_state.hr_agent.generate_outreach_campaigns(
                    selected_job_id, min_match_score, max_outreach
                )
                
                if campaigns:
                    st.success(f"✅ Generated {len(campaigns)} outreach emails!")
                    
                    # Show campaign summary
                    st.subheader("📋 Campaign Summary")
                    campaign_df = pd.DataFrame([
                        {
                            'Candidate': c['candidate_name'],
                            'Email': c['candidate_email'],
                            'Match Score': f"{c['match_score']:.2f}",
                            'Status': 'Ready to Send'
                        }
                        for c in campaigns
                    ])
                    st.dataframe(campaign_df, use_container_width=True)
                    
                    # Email previews
                    st.subheader("📧 Email Previews")
                    for i, campaign in enumerate(campaigns):
                        with st.expander(f"📧 {campaign['candidate_name']} (Score: {campaign['match_score']:.2f})"):
                            st.text_area(
                                "Generated Email:", 
                                campaign['email_content'], 
                                height=200, 
                                key=f"outreach_email_{i}"
                            )
                    
                    # Send emails (simulation)
                    if st.button("📤 Send All Emails", type="primary"):
                        with st.spinner("Sending emails..."):
                            result = st.session_state.hr_agent.send_outreach_emails(campaigns)
                            st.success(f"✅ Campaign completed: {result['sent']} emails sent!")
                            if result['failed'] > 0:
                                st.warning(f"⚠️ {result['failed']} emails failed to send.")
                else:
                    st.info("No candidates available for outreach. They may have been contacted already or don't meet the criteria.")
                    
            except Exception as e:
                st.error(f"❌ Error generating campaign: {e}")
    
    # Show outreach history
    st.subheader("📜 Outreach History")
    try:
        candidates = st.session_state.hr_agent.db.get_candidates_by_job(selected_job_id)
        contacted_candidates = [c for c in candidates if c['response_status'] != 'not_contacted']
        
        if contacted_candidates:
            history_df = pd.DataFrame([
                {
                    'Candidate': c['name'],
                    'Contact Date': c['last_contacted'] or 'Never',
                    'Status': c['response_status'].replace('_', ' ').title(),
                    'Match Score': f"{c['match_score']:.2f}"
                }
                for c in contacted_candidates
            ])
            st.dataframe(history_df, use_container_width=True)
        else:
            st.info("No outreach history for this job yet.")
    
    except Exception as e:
        st.error(f"Error loading outreach history: {e}")

def show_reports():
    st.header("📊 Reports & Analytics")
    
    tab1, tab2, tab3 = st.tabs(["Daily Report", "Executive Summary", "Export Data"])
    
    with tab1:
        st.subheader("📅 Daily Report")
        
        selected_date = st.date_input("Select Date", datetime.now())
        date_str = selected_date.strftime('%Y-%m-%d')
        
        if st.button("📊 Generate Daily Report"):
            with st.spinner("Generating report..."):
                try:
                    report = st.session_state.hr_agent.generate_daily_report(date_str)
                    
                    # Summary metrics
                    st.subheader("📈 Summary Metrics")
                    metrics_df = pd.DataFrame([
                        {'Metric': 'Candidates Sourced', 'Value': report['summary']['candidates_sourced']},
                        {'Metric': 'Candidates Shortlisted', 'Value': report['summary']['candidates_shortlisted']},
                        {'Metric': 'Candidates Contacted', 'Value': report['summary']['candidates_contacted']},
                        {'Metric': 'Responses Received', 'Value': report['summary']['responses_received']}
                    ])
                    st.dataframe(metrics_df, use_container_width=True)
                    
                    # Job breakdown
                    if report['job_breakdown']:
                        st.subheader("🎯 Job Performance Breakdown")
                        job_df = pd.DataFrame(report['job_breakdown'])
                        st.dataframe(job_df, use_container_width=True)
                    
                    # JSON export
                    st.subheader("📄 Full Report (JSON)")
                    st.json(report)
                    
                except Exception as e:
                    st.error(f"Error generating report: {e}")
    
    with tab2:
        st.subheader("👔 Executive Summary")
        
        if st.button("📋 Generate Executive Summary"):
            try:
                summary = st.session_state.report_generator.generate_executive_summary()
                
                # Overview
                st.subheader("🎯 Overview")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Active Jobs", summary['overview']['active_jobs'])
                with col2:
                    st.metric("Total Candidates", summary['overview']['total_candidates'])
                with col3:
                    st.metric("Response Rate", summary['overview']['response_rate'])
                with col4:
                    st.metric("Contact Rate", summary['overview']['contact_rate'])
                
                # Today's performance
                st.subheader("📅 Today's Performance")
                perf_df = pd.DataFrame([
                    {'Metric': k.replace('_', ' ').title(), 'Value': v}
                    for k, v in summary['today_performance'].items()
                ])
                st.dataframe(perf_df, use_container_width=True)
                
                # Top performing jobs
                if summary['top_performing_jobs']:
                    st.subheader("🏆 Top Performing Jobs")
                    top_jobs_df = pd.DataFrame(summary['top_performing_jobs'])
                    st.dataframe(top_jobs_df, use_container_width=True)
                
                # Recommendations
                if summary['recommendations']:
                    st.subheader("💡 Recommendations")
                    for rec in summary['recommendations']:
                        st.info(rec)
                
            except Exception as e:
                st.error(f"Error generating executive summary: {e}")
    
    with tab3:
        st.subheader("📤 Export Data")
        
        # Job selection for export
        jobs = st.session_state.hr_agent.db.get_jobs()
        if jobs:
            job_options = {"All Jobs": None}
            job_options.update({f"{job['title']} (ID: {job['id']})": job['id'] for job in jobs})
            
            selected_export_job = st.selectbox("Select Job to Export:", list(job_options.keys()))
            export_job_id = job_options[selected_export_job]
            
            if st.button("📊 Export to CSV"):
                try:
                    filepath = st.session_state.report_generator.export_candidates_to_csv(export_job_id)
                    st.success(f"✅ Data exported to: {filepath}")
                    
                    # Show preview
                    df = pd.read_csv(filepath)
                    st.dataframe(df.head(), use_container_width=True)
                    
                except Exception as e:
                    st.error(f"Error exporting data: {e}")

def show_settings():
    st.header("⚙️ Settings")
    
    st.subheader("🔧 Configuration")
    
    # Show current configuration (without sensitive data)
    config_display = {
        "Ollama Host": os.getenv('OLLAMA_HOST', 'http://localhost:11434'),
        "Ollama Model": os.getenv('OLLAMA_MODEL', 'llama3.1:8b'),
        "Database Path": os.getenv('DATABASE_PATH', './data/hr_recruitment.db'),
        "Google API Key": "Configured ✅" if os.getenv('GOOGLE_API_KEY') else "Not configured ❌"
    }
    
    for key, value in config_display.items():
        st.text(f"{key}: {value}")
    
    st.subheader("🧪 Test Connections")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🧠 Test Ollama Connection"):
            try:
                # Test Ollama connection
                import ollama
                client = ollama.Client(host=os.getenv('OLLAMA_HOST', 'http://localhost:11434'))
                response = client.chat(
                    model=os.getenv('OLLAMA_MODEL', 'llama3.1:8b'),
                    messages=[{"role": "user", "content": "Hello, are you working?"}]
                )
                st.success("✅ Ollama connection successful!")
                st.text(f"Response: {response['message']['content'][:100]}...")
            except Exception as e:
                st.error(f"❌ Ollama connection failed: {e}")
    
    with col2:
        if st.button("🌐 Test Gemini API"):
            try:
                import google.generativeai as genai
                genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content("Hello, test connection")
                st.success("✅ Gemini API connection successful!")
                st.text(f"Response: {response.text[:100]}...")
            except Exception as e:
                st.error(f"❌ Gemini API connection failed: {e}")
    
    st.subheader("💾 Database Management")
    
    if st.button("🗑️ Clear All Data", type="secondary"):
        if st.checkbox("I understand this will delete all data"):
            try:
                # This would clear the database
                st.warning("⚠️ This feature is disabled in demo mode")
            except Exception as e:
                st.error(f"Error clearing data: {e}")

if __name__ == "__main__":
    main()
