#!/usr/bin/env python3
"""
Test script to verify AI HR Recruitment Agent installation
"""

import os
import sys
from dotenv import load_dotenv

def test_imports():
    """Test if all required packages can be imported"""
    print("📦 Testing package imports...")
    
    required_packages = [
        'google.generativeai',
        'ollama',
        'streamlit',
        'pandas',
        'sqlite3',
        'requests',
        'dotenv',
        'pydantic',
        'plotly'
    ]
    
    failed_imports = []
    
    for package in required_packages:
        try:
            if package == 'google.generativeai':
                import google.generativeai
            elif package == 'sqlite3':
                import sqlite3
            else:
                __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package}")
            failed_imports.append(package)
    
    if failed_imports:
        print(f"\\n❌ Failed to import: {', '.join(failed_imports)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("✅ All packages imported successfully")
    return True

def test_environment():
    """Test environment configuration"""
    print("\\n⚙️ Testing environment configuration...")
    
    load_dotenv()
    
    required_vars = {
        'GOOGLE_API_KEY': 'Google Gemini API key',
        'OLLAMA_HOST': 'Ollama host URL',
        'OLLAMA_MODEL': 'Ollama model name',
        'DATABASE_PATH': 'Database file path'
    }
    
    missing_vars = []
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            if var == 'GOOGLE_API_KEY':
                print(f"  ✅ {var}: [CONFIGURED]")
            else:
                print(f"  ✅ {var}: {value}")
        else:
            print(f"  ❌ {var}: Not set ({description})")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\\n❌ Missing environment variables: {', '.join(missing_vars)}")
        print("📝 Please update your .env file")
        return False
    
    print("✅ Environment configuration is complete")
    return True

def test_ai_services():
    """Test AI service connections"""
    print("\\n🧠 Testing AI service connections...")
    
    # Test Gemini
    try:
        import google.generativeai as genai
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Hello, this is a test")
        print("  ✅ Google Gemini API: Connected")
    except Exception as e:
        print(f"  ❌ Google Gemini API: {e}")
        return False
    
    # Test Ollama
    try:
        import ollama
        client = ollama.Client(host=os.getenv('OLLAMA_HOST', 'http://localhost:11434'))
        response = client.chat(
            model=os.getenv('OLLAMA_MODEL', 'llama3.1:8b'),
            messages=[{"role": "user", "content": "Hello, test"}]
        )
        print("  ✅ Ollama: Connected")
    except Exception as e:
        print(f"  ❌ Ollama: {e}")
        return False
    
    print("✅ All AI services are working")
    return True

def test_database():
    """Test database functionality"""
    print("\\n💾 Testing database functionality...")
    
    try:
        sys.path.append('src')
        from database import HRDatabase
        
        # Test database creation
        test_db_path = './data/test_hr_recruitment.db'
        db = HRDatabase(test_db_path)
        
        print("  ✅ Database creation: Success")
        
        # Test adding a job
        job_id = db.add_job(
            title="Test Developer",
            company="Test Company",
            description="Test job description",
            required_skills=["Python", "SQL"],
            experience_level="Mid",
            location="Remote"
        )
        
        print("  ✅ Job insertion: Success")
        
        # Test retrieving jobs
        jobs = db.get_jobs()
        if jobs and len(jobs) > 0:
            print("  ✅ Job retrieval: Success")
        else:
            print("  ❌ Job retrieval: Failed")
            return False
        
        # Clean up test database
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
        
        print("✅ Database functionality is working")
        return True
        
    except Exception as e:
        print(f"  ❌ Database test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 AI HR Recruitment Agent - Installation Test")
    print("=" * 60)
    
    tests = [
        ("Package Imports", test_imports),
        ("Environment Configuration", test_environment),
        ("AI Services", test_ai_services),
        ("Database", test_database)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\\n🔍 Running {test_name} test...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} test failed")
    
    print("\\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your installation is ready.")
        print("\\n🚀 Ready to start:")
        print("  • Web interface: python main.py web")
        print("  • CLI help: python main.py --help")
        print("  • Run demo: python demo.py")
        return 0
    else:
        print("❌ Some tests failed. Please check the error messages and fix the issues.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
