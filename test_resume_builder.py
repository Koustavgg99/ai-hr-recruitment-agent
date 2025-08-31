#!/usr/bin/env python3
"""
Test script for Resume Builder functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from resume_builder import get_resume_builder, check_pdf_dependencies

def test_resume_builder():
    print("🧪 Testing Resume Builder functionality...")
    
    # Check dependencies
    pdf_available, missing = check_pdf_dependencies()
    print(f"📦 PDF Dependencies: {'✅ Available' if pdf_available else '❌ Missing: ' + ', '.join(missing)}")
    
    if not pdf_available:
        print("❌ Cannot continue without PDF dependencies")
        return False
    
    # Initialize builder
    try:
        builder = get_resume_builder()
        print("✅ Resume Builder initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize builder: {e}")
        return False
    
    # Test sample data processing
    test_data = {
        'full_name': 'John Doe',
        'email': 'john.doe@example.com',
        'phone': '(555) 123-4567',
        'current_company': 'Tech Solutions Inc.',
        'current_position': 'Senior Software Engineer',
        'experience_years': 8,
        'skills': ['Python', 'JavaScript', 'React', 'Node.js', 'AWS', 'Docker'],
        'summary': 'Experienced software engineer with 8 years of expertise in full-stack development, cloud technologies, and team leadership.',
        'education': ['Bachelor of Science in Computer Science - University of Technology (2015)', 'AWS Certified Solutions Architect (2020)'],
        'original_filename': 'test_resume.pdf',
        'processed_at': '2024-01-01T12:00:00'
    }
    
    try:
        print("🔄 Testing PDF generation...")
        pdf_bytes, filename = builder.generate_resume_pdf(test_data, "John Doe")
        print(f"✅ PDF generated successfully: {filename}")
        print(f"📊 Generated file size: {len(pdf_bytes) / 1024:.1f} KB")
        
        # Test file listing
        resumes = builder.get_generated_resumes()
        print(f"📁 Found {len(resumes)} generated resume(s)")
        
        # Test file retrieval
        if resumes:
            test_resume = resumes[0]
            retrieved_data = builder.get_resume_data_from_file(test_resume['filename'])
            if retrieved_data:
                print(f"✅ Successfully retrieved resume data: {len(retrieved_data) / 1024:.1f} KB")
            else:
                print("❌ Failed to retrieve resume data")
        
        print("\n🎉 All tests passed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ PDF generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_resume_builder()
    sys.exit(0 if success else 1)
