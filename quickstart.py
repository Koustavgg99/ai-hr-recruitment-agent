#!/usr/bin/env python3
"""
Quick Start Script for AI HR Recruitment Agent
This script helps you get started quickly with sample data
"""

import os
import sys
import json
from dotenv import load_dotenv

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def check_prerequisites():
    """Check if all prerequisites are met"""
    print("🔍 Checking prerequisites...")
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ .env file not found")
        print("📝 Please copy .env.example to .env and add your API keys")
        return False
    
    # Load environment variables
    load_dotenv()
    
    # Check Google API key
    if not os.getenv('GOOGLE_API_KEY'):
        print("❌ GOOGLE_API_KEY not found in .env file")
        print("📝 Please add your Google Gemini API key to the .env file")
        return False
    
    # Check if Ollama is running
    try:
        import requests
        response = requests.get(os.getenv('OLLAMA_HOST', 'http://localhost:11434'), timeout=5)
        print("✅ Ollama is running")
    except:
        print("❌ Ollama not running or not accessible")
        print("🚀 Please start Ollama with: ollama serve")
        return False
    
    # Check if required model is available
    try:
        import ollama
        client = ollama.Client(host=os.getenv('OLLAMA_HOST', 'http://localhost:11434'))
        models = client.list()
        model_name = os.getenv('OLLAMA_MODEL', 'llama3.1:8b')
        
        if any(model['name'] == model_name for model in models['models']):
            print(f"✅ Ollama model {model_name} is available")
        else:
            print(f"❌ Ollama model {model_name} not found")
            print(f"📥 Please pull the model with: ollama pull {model_name}")
            return False
    except Exception as e:
        print(f"❌ Error checking Ollama models: {e}")
        return False
    
    print("✅ All prerequisites met!")
    return True

def setup_sample_data():
    """Set up the system with sample data"""
    print("📊 Setting up sample data...")
    
    try:
        from hr_agent import HRRecruitmentAgent
        
        # Load configuration
        load_dotenv()
        config = {
            'google_api_key': os.getenv('GOOGLE_API_KEY'),
            'ollama_host': os.getenv('OLLAMA_HOST', 'http://localhost:11434'),
            'ollama_model': os.getenv('OLLAMA_MODEL', 'llama3.1:8b'),
            'database_path': os.getenv('DATABASE_PATH', './data/hr_recruitment.db')
        }
        
        # Initialize agent
        agent = HRRecruitmentAgent(config)
        
        # Load sample job descriptions
        with open('templates/sample_job_descriptions.json', 'r') as f:
            sample_jobs = json.load(f)
        
        # Add first sample job
        first_job = sample_jobs['job_descriptions'][0]
        job_id = agent.process_job_description(first_job['description'], first_job['company'])
        
        print(f"✅ Added sample job: {first_job['title']} (ID: {job_id})")
        
        # Source some candidates
        print("🔎 Sourcing sample candidates...")
        candidates = agent.source_candidates(job_id, 10)
        print(f"✅ Sourced {len(candidates)} candidates")
        
        # Generate sample outreach
        print("📧 Generating sample outreach...")
        campaigns = agent.generate_outreach_campaigns(job_id, 0.5, 3)
        print(f"✅ Generated {len(campaigns)} outreach emails")
        
        # Generate sample report
        print("📊 Generating sample report...")
        report = agent.generate_daily_report()
        print("✅ Sample report generated")
        
        print("\n🎉 Sample data setup completed!")
        print("🌐 You can now launch the web interface with: python main.py web")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up sample data: {e}")
        return False

def main():
    """Main quickstart function"""
    print("🤖 AI HR Recruitment Agent - Quick Start")
    print("=" * 50)
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites not met. Please fix the issues above and try again.")
        return
    
    print("\n" + "=" * 50)
    
    # Ask if user wants to set up sample data
    setup_sample = input("📊 Would you like to set up sample data for testing? (y/n): ").lower().strip()
    
    if setup_sample in ['y', 'yes']:
        if setup_sample_data():
            print("\n🚀 Quick start completed successfully!")
            print("\nNext steps:")
            print("1. 🌐 Launch web interface: python main.py web")
            print("2. 📋 Or use CLI: python main.py job list")
            print("3. 📖 Read the README.md for detailed usage instructions")
        else:
            print("\n❌ Sample data setup failed. Check the error messages above.")
    else:
        print("\n✅ Prerequisites verified! You're ready to use the HR Agent.")
        print("\nNext steps:")
        print("1. 🌐 Launch web interface: python main.py web")
        print("2. 💼 Add your first job: python main.py job add -d 'your job description'")
        print("3. 📖 Read the README.md for detailed instructions")

if __name__ == "__main__":
    main()
