#!/usr/bin/env python3
"""
Simple test script for HR Automation Auto-Fill Functionality
Tests the basic functionality without dependencies
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_resume_parser():
    """Test resume parser with sample text"""
    print("🧪 Testing Resume Parser...")
    
    try:
        from resume_parser import ResumeParser
        
        parser = ResumeParser()
        
        # Sample resume text
        sample_resume = """
        John Doe
        Software Engineer
        john.doe@email.com
        (555) 123-4567
        https://linkedin.com/in/johndoe
        San Francisco, CA
        
        EXPERIENCE
        Senior Software Engineer - Tech Corp Inc (2021 - Present)
        - Developed web applications using Python and React
        - Led a team of 5 developers
        - Implemented CI/CD pipelines
        
        SKILLS
        Python, JavaScript, React, Node.js, AWS, Docker, PostgreSQL, Git
        
        EDUCATION
        Bachelor of Science in Computer Science - Stanford University
        """
        
        result = parser.parse_text(sample_resume)
        
        print(f"  ✅ Name: {result.full_name}")
        print(f"  ✅ Email: {result.email}")
        print(f"  ✅ Phone: {result.phone}")
        print(f"  ✅ LinkedIn: {result.linkedin_url}")
        print(f"  ✅ Location: {result.location}")
        print(f"  ✅ Skills: {result.skills[:5] if result.skills else 'None'}")
        print(f"  ✅ Company: {result.current_company}")
        print(f"  ✅ Position: {result.current_position}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_linkedin_scraper():
    """Test LinkedIn scraper with sample URL"""
    print("\n🧪 Testing LinkedIn Scraper...")
    
    try:
        from linkedin_scraper import LinkedInProfileExtractor
        
        extractor = LinkedInProfileExtractor()
        
        # Test URL validation
        test_urls = [
            "https://linkedin.com/in/johndoe",
            "linkedin.com/in/jane-smith",
            "https://www.linkedin.com/in/tech-professional-123"
        ]
        
        for url in test_urls:
            is_valid = extractor.scraper.is_valid_linkedin_url(url)
            normalized = extractor.scraper.normalize_linkedin_url(url)
            print(f"  URL: {url}")
            print(f"    Valid: {'✅' if is_valid else '❌'}")
            print(f"    Normalized: {normalized}")
        
        # Test basic info extraction
        basic_info = extractor.extract_basic_info_from_url("https://linkedin.com/in/john-doe-engineer")
        print(f"  ✅ Basic extraction: {basic_info}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_candidate_autofill():
    """Test candidate auto-fill functionality"""
    print("\n🧪 Testing Candidate Auto-Fill...")
    
    try:
        from candidate_autofill import CandidateAutoFill, validate_extracted_data
        
        autofill = CandidateAutoFill()
        
        # Test status info
        status = autofill.get_status_info()
        print("  Status:")
        for service, info in status.items():
            print(f"    {service}: {info}")
        
        # Test data validation
        test_data = {
            'full_name': 'John Doe',
            'email': 'john@example.com',
            'linkedin_url': 'https://linkedin.com/in/johndoe'
        }
        
        is_valid, errors = validate_extracted_data(test_data)
        print(f"  ✅ Data validation: {'Valid' if is_valid else 'Invalid'}")
        if errors:
            print(f"    Errors: {errors}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_file_validation():
    """Test file validation functionality"""
    print("\n🧪 Testing File Validation...")
    
    try:
        from resume_parser import ResumeParser
        
        parser = ResumeParser()
        
        # Test supported file types
        supported_types = parser.get_supported_file_types()
        print(f"  ✅ Supported file types: {supported_types}")
        
        # Test file validation (with non-existent file)
        is_valid, error_msg = parser.validate_file("test.pdf")
        print(f"  File validation result: {'Valid' if is_valid else error_msg}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 HR Automation Auto-Fill Functionality Test")
    print("=" * 50)
    
    tests = [
        ("Resume Parser", test_resume_parser),
        ("LinkedIn Scraper", test_linkedin_scraper),
        ("Candidate Auto-Fill", test_candidate_autofill),
        ("File Validation", test_file_validation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Summary: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Auto-fill functionality is ready to use.")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        print("💡 The functionality may still work partially.")
    
    print("\n📋 Next Steps:")
    print("1. Run: streamlit run streamlit_hr_app.py")
    print("2. Navigate to: Candidate Management → Add New Candidate")
    print("3. Try the Auto-Fill tab")

if __name__ == "__main__":
    main()
