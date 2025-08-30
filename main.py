#!/usr/bin/env python3
"""
AI HR Recruitment Agent - Command Line Interface
"""

import os
import sys
import json
import argparse
from datetime import datetime
from dotenv import load_dotenv

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from hr_agent import HRRecruitmentAgent
from reporting import ReportGenerator

def load_config():
    """Load configuration from environment variables"""
    load_dotenv()
    
    config = {
        'google_api_key': os.getenv('GOOGLE_API_KEY'),
        'ollama_host': os.getenv('OLLAMA_HOST', 'http://localhost:11434'),
        'ollama_model': os.getenv('OLLAMA_MODEL', 'llama3.1:8b'),
        'database_path': os.getenv('DATABASE_PATH', './data/hr_recruitment.db')
    }
    
    if not config['google_api_key']:
        print("❌ Error: GOOGLE_API_KEY not found in environment variables.")
        print("Please set up your .env file with your Google Gemini API key.")
        sys.exit(1)
    
    return config

def process_job_command(args):
    """Process job-related commands"""
    config = load_config()
    agent = HRRecruitmentAgent(config)
    
    if args.action == 'add':
        if not args.description:
            print("❌ Error: Job description is required")
            return
        
        company = args.company or "TechCorp"
        job_id = agent.process_job_description(args.description, company)
        print(f"✅ Job added successfully with ID: {job_id}")
    
    elif args.action == 'list':
        jobs = agent.db.get_jobs()
        if jobs:
            print("\n📋 Active Jobs:")
            for job in jobs:
                print(f"  ID: {job['id']} | {job['title']} at {job['company']}")
                print(f"    Skills: {', '.join(job['required_skills'])}")
                print(f"    Posted: {job['posted_date']}")
                print()
        else:
            print("📭 No jobs found.")

def source_candidates_command(args):
    """Source candidates for a job"""
    config = load_config()
    agent = HRRecruitmentAgent(config)
    
    job_id = args.job_id
    max_candidates = args.max_candidates or 20
    
    print(f"🔎 Sourcing candidates for job ID: {job_id}")
    
    try:
        candidates = agent.source_candidates(job_id, max_candidates)
        
        if candidates:
            print(f"✅ Found {len(candidates)} candidates:")
            for candidate in candidates[:10]:  # Show top 10
                print(f"  📋 {candidate['name']} | Score: {candidate['match_score']:.2f}")
                print(f"     Skills: {', '.join(candidate['skills'][:3])}")
                print(f"     Experience: {candidate['experience_years']} years")
                print()
        else:
            print("📭 No candidates found.")
    
    except Exception as e:
        print(f"❌ Error sourcing candidates: {e}")

def run_outreach_command(args):
    """Run outreach campaign"""
    config = load_config()
    agent = HRRecruitmentAgent(config)
    
    job_id = args.job_id
    min_score = args.min_score or 0.7
    max_outreach = args.max_outreach or 10
    
    print(f"📧 Running outreach campaign for job ID: {job_id}")
    
    try:
        # Generate campaigns
        campaigns = agent.generate_outreach_campaigns(job_id, min_score, max_outreach)
        
        if campaigns:
            print(f"✅ Generated {len(campaigns)} outreach emails")
            
            # Show previews
            if args.preview:
                for i, campaign in enumerate(campaigns[:3]):
                    print(f"\n📧 Email for {campaign['candidate_name']}:")
                    print("=" * 50)
                    print(campaign['email_content'])
                    print("=" * 50)
            
            # Send emails if not preview mode
            if not args.preview:
                result = agent.send_outreach_emails(campaigns)
                print(f"📤 Campaign completed: {result['sent']} sent, {result['failed']} failed")
        else:
            print("📭 No candidates available for outreach.")
    
    except Exception as e:
        print(f"❌ Error running outreach: {e}")

def generate_report_command(args):
    """Generate reports"""
    config = load_config()
    agent = HRRecruitmentAgent(config)
    report_gen = ReportGenerator(agent)
    
    if args.type == 'daily':
        date = args.date or datetime.now().strftime('%Y-%m-%d')
        report = agent.generate_daily_report(date)
        
        if args.format == 'json':
            print(json.dumps(report, indent=2, default=str))
        else:
            # Table format
            print(f"\n📊 Daily Report for {date}")
            print("=" * 40)
            print(f"Candidates Sourced: {report['summary']['candidates_sourced']}")
            print(f"Candidates Shortlisted: {report['summary']['candidates_shortlisted']}")
            print(f"Candidates Contacted: {report['summary']['candidates_contacted']}")
            print(f"Responses Received: {report['summary']['responses_received']}")
    
    elif args.type == 'executive':
        summary = report_gen.generate_executive_summary()
        
        print("\n👔 Executive Summary")
        print("=" * 40)
        print(f"Active Jobs: {summary['overview']['active_jobs']}")
        print(f"Total Candidates: {summary['overview']['total_candidates']}")
        print(f"Response Rate: {summary['overview']['response_rate']}")
        print(f"Contact Rate: {summary['overview']['contact_rate']}")
        
        if summary['recommendations']:
            print("\n💡 Recommendations:")
            for rec in summary['recommendations']:
                print(f"  • {rec}")

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description='AI HR Recruitment Agent')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Job management commands
    job_parser = subparsers.add_parser('job', help='Job management commands')
    job_parser.add_argument('action', choices=['add', 'list'], help='Action to perform')
    job_parser.add_argument('--description', '-d', help='Job description (for add action)')
    job_parser.add_argument('--company', '-c', help='Company name')
    
    # Candidate sourcing commands
    source_parser = subparsers.add_parser('source', help='Source candidates for a job')
    source_parser.add_argument('job_id', type=int, help='Job ID to source candidates for')
    source_parser.add_argument('--max-candidates', type=int, help='Maximum number of candidates to source')
    
    # Outreach commands
    outreach_parser = subparsers.add_parser('outreach', help='Run outreach campaigns')
    outreach_parser.add_argument('job_id', type=int, help='Job ID for outreach')
    outreach_parser.add_argument('--min-score', type=float, help='Minimum match score for outreach')
    outreach_parser.add_argument('--max-outreach', type=int, help='Maximum number of candidates to contact')
    outreach_parser.add_argument('--preview', action='store_true', help='Preview emails without sending')
    
    # Report commands
    report_parser = subparsers.add_parser('report', help='Generate reports')
    report_parser.add_argument('type', choices=['daily', 'executive'], help='Type of report')
    report_parser.add_argument('--date', help='Date for report (YYYY-MM-DD)')
    report_parser.add_argument('--format', choices=['json', 'table'], default='table', help='Output format')
    
    # Web interface command
    web_parser = subparsers.add_parser('web', help='Launch web interface')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Route to appropriate function
    if args.command == 'job':
        process_job_command(args)
    elif args.command == 'source':
        source_candidates_command(args)
    elif args.command == 'outreach':
        run_outreach_command(args)
    elif args.command == 'report':
        generate_report_command(args)
    elif args.command == 'web':
        print("🚀 Launching web interface...")
        os.system("streamlit run src/streamlit_app.py")

if __name__ == "__main__":
    main()
