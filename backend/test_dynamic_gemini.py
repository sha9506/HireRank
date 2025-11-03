"""
Test script for dynamic Gemini AI analysis
Demonstrates how the analyzer works for different job roles
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from models.gemini_analyzer import GeminiResumeAnalyzer
import json

def test_teacher_role():
    """Test analysis for a Teacher position"""
    print("=" * 80)
    print("TEST 1: Analyzing resume for TEACHER position")
    print("=" * 80)
    
    resume = {
        "name": "Sarah Johnson",
        "skills": [
            "Classroom Management",
            "Curriculum Design",
            "Google Classroom",
            "Microsoft PowerPoint",
            "Student Assessment",
            "Parent Communication",
            "Differentiated Instruction"
        ],
        "experience": [
            {
                "title": "Elementary School Teacher",
                "company": "Lincoln Elementary",
                "duration": "2018-2023",
                "description": "Taught 4th grade students, managed classroom of 25 students"
            }
        ],
        "education": [
            {
                "degree": "Bachelor of Education",
                "institution": "State University",
                "year": "2018"
            }
        ],
        "certifications": ["Teaching License", "CPR Certified"]
    }
    
    analyzer = GeminiResumeAnalyzer()
    
    try:
        result = analyzer.analyze_resume_with_gemini(
            resume,
            job_title="Elementary School Teacher",
            job_description="Looking for an experienced teacher who can manage classroom effectively and use educational technology."
        )
        
        print(f"\n✅ Matched Role: {result.get('matched_role')}")
        print(f"📊 Confidence: {result.get('role_confidence')}")
        print(f"\n📚 Skills Found:")
        for category, skills in result.get('skill_match', {}).items():
            if skills:
                print(f"   {category}: {', '.join(skills)}")
        
        print(f"\n⚠️  Skills Missing:")
        for category, skills in result.get('skill_missing', {}).items():
            if skills:
                print(f"   {category}: {', '.join(skills)}")
        
        print(f"\n💡 Recommendations: {result.get('recommendations', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def test_software_engineer_role():
    """Test analysis for a Software Engineer position"""
    print("\n" + "=" * 80)
    print("TEST 2: Analyzing resume for SOFTWARE ENGINEER position")
    print("=" * 80)
    
    resume = {
        "name": "Alex Chen",
        "skills": [
            "Python",
            "JavaScript",
            "React",
            "Django",
            "SQL",
            "Git",
            "Problem Solving"
        ],
        "experience": [
            {
                "title": "Junior Developer",
                "company": "Tech Startup",
                "duration": "2021-2023",
                "description": "Built web applications using React and Django"
            }
        ],
        "education": [
            {
                "degree": "BS Computer Science",
                "institution": "Tech University",
                "year": "2021"
            }
        ],
        "certifications": []
    }
    
    analyzer = GeminiResumeAnalyzer()
    
    try:
        result = analyzer.analyze_resume_with_gemini(
            resume,
            job_title="Full Stack Software Engineer",
            job_description="We need a full stack engineer proficient in modern web technologies, with experience in React, Node.js, and cloud platforms."
        )
        
        print(f"\n✅ Matched Role: {result.get('matched_role')}")
        print(f"📊 Confidence: {result.get('role_confidence')}")
        print(f"\n📚 Skills Found:")
        for category, skills in result.get('skill_match', {}).items():
            if skills:
                print(f"   {category}: {', '.join(skills)}")
        
        print(f"\n⚠️  Skills Missing:")
        for category, skills in result.get('skill_missing', {}).items():
            if skills:
                print(f"   {category}: {', '.join(skills)}")
        
        print(f"\n💡 Recommendations: {result.get('recommendations', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def test_data_scientist_role():
    """Test analysis for a Data Scientist position"""
    print("\n" + "=" * 80)
    print("TEST 3: Analyzing resume for DATA SCIENTIST position")
    print("=" * 80)
    
    resume = {
        "name": "Maria Garcia",
        "skills": [
            "Python",
            "Pandas",
            "NumPy",
            "Matplotlib",
            "Machine Learning",
            "SQL",
            "Jupyter Notebook",
            "Statistics"
        ],
        "experience": [
            {
                "title": "Data Analyst",
                "company": "Analytics Corp",
                "duration": "2020-2023",
                "description": "Analyzed business data, created visualizations, built predictive models"
            }
        ],
        "education": [
            {
                "degree": "MS Statistics",
                "institution": "Data University",
                "year": "2020"
            }
        ],
        "certifications": ["Google Data Analytics Certificate"]
    }
    
    analyzer = GeminiResumeAnalyzer()
    
    try:
        result = analyzer.analyze_resume_with_gemini(
            resume,
            job_title="Data Scientist",
            job_description="Seeking data scientist with strong ML skills, Python expertise, and experience with TensorFlow or PyTorch."
        )
        
        print(f"\n✅ Matched Role: {result.get('matched_role')}")
        print(f"📊 Confidence: {result.get('role_confidence')}")
        print(f"\n📚 Skills Found:")
        for category, skills in result.get('skill_match', {}).items():
            if skills:
                print(f"   {category}: {', '.join(skills)}")
        
        print(f"\n⚠️  Skills Missing:")
        for category, skills in result.get('skill_missing', {}).items():
            if skills:
                print(f"   {category}: {', '.join(skills)}")
        
        print(f"\n💡 Recommendations: {result.get('recommendations', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    print("\n🤖 DYNAMIC GEMINI AI RESUME ANALYZER TEST\n")
    print("This test demonstrates how Gemini AI intelligently analyzes resumes")
    print("for ANY job role - not just tech positions!\n")
    
    test_teacher_role()
    test_software_engineer_role()
    test_data_scientist_role()
    
    print("\n" + "=" * 80)
    print("✅ All tests completed!")
    print("=" * 80)
    print("\nNote: The analyzer now:")
    print("  1. Understands ANY job role (Teacher, Nurse, Engineer, etc.)")
    print("  2. Dynamically identifies relevant skills for that role")
    print("  3. Provides context-aware skill matching")
    print("  4. Suggests role-specific missing skills")
    print("  5. Uses AI intelligence, not rigid dictionaries!")
    print("=" * 80 + "\n")
