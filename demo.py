#!/usr/bin/env python3
"""
AI HR Recruitment Agent - Interactive Demo
This script demonstrates all the key features of the HR agent
"""

import os
import sys
import json
import time
from dotenv import load_dotenv

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def run_demo():
    """Run an interactive demo of the HR agent"""
    print("🤖 AI HR Recruitment Agent - Interactive Demo")
    print("=" * 60)
    
    # Load configuration
    load_dotenv()
    
    try:
        from hr_agent import HRRecruitmentAgent
        from reporting import ReportGenerator
        
        config = {
            'google_api_key': os.getenv('GOOGLE_API_KEY'),
            'ollama_host': os.getenv('OLLAMA_HOST', 'http://localhost:11434'),
            'ollama_model': os.getenv('OLLAMA_MODEL', 'llama3.1:8b'),
            'database_path': os.getenv('DATABASE_PATH', './data/hr_recruitment_demo.db')
        }
        
        if not config['google_api_key']:
            print("❌ Please set up your .env file with GOOGLE_API_KEY")
            return
        
        # Initialize agent
        print("🚀 Initializing HR Agent...")
        agent = HRRecruitmentAgent(config)
        report_gen = ReportGenerator(agent)
        
        print("✅ HR Agent initialized successfully!")
        time.sleep(1)
        
        # Demo Step 1: Job Description Analysis
        print("\\n" + "=" * 60)
        print("📋 STEP 1: Job Description Analysis")
        print("=" * 60)
        
        sample_jd = """
Senior Full Stack Developer - TechFlow Inc

We are looking for a Senior Full Stack Developer to join our team. 

Requirements:
- 5+ years of experience in Python and JavaScript
- Strong knowledge of React and Django frameworks
- Experience with PostgreSQL and Redis
- AWS cloud experience required
- Docker and Kubernetes knowledge preferred
- Bachelor's degree in Computer Science or equivalent

Location: San Francisco, CA (Hybrid)
Salary: $130,000 - $170,000
"""
        
        print("Analyzing this job description:")
        print("-" * 40)
        print(sample_jd)
        print("-" * 40)
        
        job_id = agent.process_job_description(sample_jd, "TechFlow Inc")
        print(f"✅ Job analysis completed! Job ID: {job_id}")
        
        # Demo Step 2: Candidate Sourcing
        print("\\n" + "=" * 60)
        print("🔎 STEP 2: Candidate Sourcing")
        print("=" * 60)
        
        print("Searching for qualified candidates...")
        candidates = agent.source_candidates(job_id, 15)
        
        print(f"\\n📊 Found {len(candidates)} candidates:")
        for i, candidate in enumerate(candidates[:5]):
            print(f"  {i+1}. {candidate['name']} | Score: {candidate['match_score']:.2f}")
            print(f"     💼 {candidate['experience_years']} years | 📍 {candidate['location']}")
            print(f"     🔧 Skills: {', '.join(candidate['skills'][:3])}...")
            print()
        
        # Demo Step 3: Outreach Generation
        print("=" * 60)
        print("📧 STEP 3: Personalized Outreach Generation")
        print("=" * 60)
        
        print("Generating personalized outreach emails for top candidates...")
        campaigns = agent.generate_outreach_campaigns(job_id, 0.6, 3)
        
        if campaigns:
            print(f"\\n✅ Generated {len(campaigns)} personalized emails!")
            
            # Show one example email
            example_campaign = campaigns[0]
            print(f"\\n📧 Example email for {example_campaign['candidate_name']}:")
            print("-" * 50)
            print(example_campaign['email_content'])
            print("-" * 50)
        
        # Demo Step 4: Reporting
        print("\\n" + "=" * 60)
        print("📊 STEP 4: Reporting & Analytics")
        print("=" * 60)
        
        print("Generating comprehensive reports...")
        
        # Daily report
        daily_report = agent.generate_daily_report()
        print("\\n📅 Daily Report:")
        print(f"  • Candidates sourced: {daily_report['summary']['candidates_sourced']}")
        print(f"  • Candidates shortlisted: {daily_report['summary']['candidates_shortlisted']}")
        print(f"  • Outreach emails generated: {len(campaigns)}")
        
        # Executive summary
        exec_summary = report_gen.generate_executive_summary()
        print("\\n👔 Executive Summary:")
        print(f"  • Active jobs: {exec_summary['overview']['active_jobs']}")
        print(f"  • Total candidates: {exec_summary['overview']['total_candidates']}")
        print(f"  • Contact rate: {exec_summary['overview']['contact_rate']}")
        
        # Demo Step 5: Pipeline Overview
        print("\\n" + "=" * 60)
        print("🔄 STEP 5: Recruitment Pipeline Status")
        print("=" * 60)
        
        pipeline = agent.get_pipeline_status()
        print("Current pipeline status:")
        for job_detail in pipeline['jobs_detail']:
            print(f"  📋 {job_detail['title']}")
            print(f"     • Candidates: {job_detail['candidates']}")
            print(f"     • Contacted: {job_detail['contacted']}")
            print(f"     • Response rate: {job_detail['response_rate']}")
        
        # Demo Complete
        print("\\n" + "=" * 60)
        print("🎉 DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
        print("\\n🌟 What you just saw:")
        print("  ✅ AI-powered job description analysis (Gemini)")
        print("  ✅ Intelligent candidate sourcing and ranking")
        print("  ✅ Personalized email generation (Ollama)")
        print("  ✅ Comprehensive tracking and reporting")
        print("  ✅ Real-time pipeline management")
        
        print("\\n🚀 Next steps:")
        print("  1. Launch web interface: python main.py web")
        print("  2. Try the CLI commands: python main.py --help")
        print("  3. Add your own job descriptions and test with real data")
        print("  4. Integrate with real LinkedIn API for production use")
        
        print("\\n📖 For detailed documentation, see README.md")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print("Please check your configuration and try again.")

def main():
    """Main demo function"""
    print("Welcome to the AI HR Recruitment Agent Demo!")
    print("This demo will showcase all the key features of the system.\\n")
    
    confirm = input("Ready to start the demo? (y/n): ").lower().strip()
    
    if confirm in ['y', 'yes']:
        run_demo()
    else:
        print("Demo cancelled. Run this script again when you're ready!")

if __name__ == "__main__":
    main()
