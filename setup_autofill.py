#!/usr/bin/env python3
"""
Setup script for HR Automation Auto-Fill Functionality
Installs all required dependencies and sets up the environment
"""

import subprocess
import sys
import os
import importlib.util
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    
    print(f"✅ Python version: {sys.version}")
    return True

def install_package(package_name, upgrade=False):
    """Install a package using pip"""
    try:
        cmd = [sys.executable, "-m", "pip", "install"]
        if upgrade:
            cmd.append("--upgrade")
        cmd.append(package_name)
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✅ Successfully installed {package_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package_name}: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_package_availability(package_name, import_name=None):
    """Check if a package is available for import"""
    if import_name is None:
        import_name = package_name
    
    try:
        spec = importlib.util.find_spec(import_name)
        if spec is not None:
            print(f"✅ {package_name} is available")
            return True
        else:
            print(f"❌ {package_name} is not available")
            return False
    except ImportError:
        print(f"❌ {package_name} is not available")
        return False

def download_spacy_model():
    """Download spaCy English model"""
    try:
        result = subprocess.run([
            sys.executable, "-m", "spacy", "download", "en_core_web_sm"
        ], capture_output=True, text=True, check=True)
        print("✅ Successfully downloaded spaCy English model")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to download spaCy model: {e}")
        print("You can try manually: python -m spacy download en_core_web_sm")
        return False

def install_requirements_file():
    """Install packages from requirements file"""
    requirements_file = Path(__file__).parent / "requirements_autofill.txt"
    
    if not requirements_file.exists():
        print(f"❌ Requirements file not found: {requirements_file}")
        return False
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ], capture_output=True, text=True, check=True)
        print("✅ Successfully installed packages from requirements file")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install from requirements file: {e}")
        return False

def check_chromedriver():
    """Check if ChromeDriver is available for Selenium"""
    try:
        result = subprocess.run(["chromedriver", "--version"], 
                              capture_output=True, text=True, check=True)
        print("✅ ChromeDriver is available")
        print(f"   Version: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️ ChromeDriver not found in PATH")
        print("   LinkedIn scraping with Selenium may not work")
        print("   Download from: https://chromedriver.chromium.org/")
        return False

def test_auto_fill_modules():
    """Test if our auto-fill modules can be imported"""
    modules_to_test = [
        ("resume_parser", "ResumeParser"),
        ("linkedin_scraper", "LinkedInProfileExtractor"),
        ("candidate_autofill", "CandidateAutoFill")
    ]
    
    all_working = True
    
    for module_name, class_name in modules_to_test:
        try:
            module = importlib.import_module(module_name)
            if hasattr(module, class_name):
                print(f"✅ {module_name}.{class_name} is available")
            else:
                print(f"❌ {class_name} not found in {module_name}")
                all_working = False
        except ImportError as e:
            print(f"❌ Cannot import {module_name}: {e}")
            all_working = False
    
    return all_working

def main():
    """Main setup function"""
    print("🚀 Setting up HR Automation Auto-Fill Functionality")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    print("\n📦 Installing required packages...")
    
    # Install from requirements file
    if install_requirements_file():
        print("✅ All packages installed successfully")
    else:
        print("❌ Some packages failed to install")
        print("You can try installing manually:")
        print("pip install PyPDF2 python-docx spacy requests beautifulsoup4 selenium")
    
    print("\n🔧 Setting up spaCy...")
    
    # Download spaCy model
    if check_package_availability("spacy"):
        download_spacy_model()
    
    print("\n🌐 Checking browser automation setup...")
    
    # Check ChromeDriver
    check_chromedriver()
    
    print("\n🧪 Testing module imports...")
    
    # Test our modules
    if test_auto_fill_modules():
        print("✅ All auto-fill modules are working")
    else:
        print("❌ Some auto-fill modules have issues")
    
    print("\n📋 Checking package availability...")
    
    # Check individual packages
    packages_to_check = [
        ("PyPDF2", "PyPDF2"),
        ("python-docx", "docx"),
        ("spacy", "spacy"),
        ("requests", "requests"),
        ("BeautifulSoup4", "bs4"),
        ("selenium", "selenium")
    ]
    
    for package_name, import_name in packages_to_check:
        check_package_availability(package_name, import_name)
    
    print("\n" + "=" * 50)
    print("🎉 Setup Complete!")
    print("\nℹ️  Next steps:")
    print("1. Run your Streamlit app: streamlit run streamlit_hr_app.py")
    print("2. Navigate to 'Candidate Management' → 'Add New Candidate'")
    print("3. Try the 'Auto-Fill (Resume/LinkedIn)' tab")
    print("\n⚠️  Important notes:")
    print("• Resume parsing works best with PDF and DOCX files")
    print("• LinkedIn scraping may be limited due to anti-bot measures")
    print("• For production use, consider LinkedIn API integration")
    
    print("\n🔧 Troubleshooting:")
    print("• If spaCy model fails to download: python -m spacy download en_core_web_sm")
    print("• If ChromeDriver issues: Download from https://chromedriver.chromium.org/")
    print("• Check logs for specific error messages")

if __name__ == "__main__":
    main()
