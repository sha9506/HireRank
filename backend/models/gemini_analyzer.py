"""
Gemini AI Resume Analyzer
Analyzes structured resume JSON data using Google's Gemini API
"""

import os
import json
import logging
from typing import Dict, List, Optional
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    logger.warning("GEMINI_API_KEY not found in environment variables")


class GeminiResumeAnalyzer:
    """
    Analyzes resume JSON data using Google Gemini AI to classify tech stacks
    and detect job roles.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Gemini analyzer
        
        Args:
            api_key: Optional Gemini API key. If not provided, uses env variable.
        """
        self.api_key = api_key or GEMINI_API_KEY
        if self.api_key:
            genai.configure(api_key=self.api_key)
        
        # Initialize the Gemini model (using latest flash model for fast responses)
        self.model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Define tech stack categories for reference (but Gemini will think beyond these)
        self.tech_categories = {
            "frontend": [
                "React", "ReactJS", "Angular", "Vue", "VueJS", "Next.js", "Nuxt.js",
                "HTML", "CSS", "JavaScript", "TypeScript", "jQuery", "Bootstrap",
                "Tailwind", "SASS", "LESS", "Webpack", "Vite", "Svelte", "Ember"
            ],
            "backend": [
                "Django", "Flask", "FastAPI", "Node.js", "Express", "Spring Boot",
                "Spring", "Java", "Python", "Ruby on Rails", "PHP", "Laravel",
                ".NET", "ASP.NET", "Go", "Golang", "Rust", "Scala", "Kotlin"
            ],
            "database": [
                "SQL", "MySQL", "PostgreSQL", "MongoDB", "Redis", "Cassandra",
                "Oracle", "SQL Server", "SQLite", "DynamoDB", "Elasticsearch",
                "Neo4j", "MariaDB", "CouchDB", "Firebase"
            ],
            "infra": [
                "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Jenkins", "GitLab CI",
                "GitHub Actions", "CircleCI", "Terraform", "Ansible", "Chef", "Puppet",
                "Nginx", "Apache", "Linux", "CI/CD", "DevOps", "Microservices"
            ]
        }
    
    def _create_analysis_prompt(self, resume_json: Dict, job_title: str = None, job_description: str = None) -> str:
        """
        Create a detailed prompt for Gemini to analyze the resume
        
        Args:
            resume_json: Structured resume data
            job_title: Target job role (e.g., "Teacher", "Software Engineer", "Data Scientist")
            job_description: Optional detailed job description
            
        Returns:
            Formatted prompt string
        """
        # Build job context
        job_context = ""
        if job_title:
            job_context = f"\n**Target Job Role:** {job_title}"
        if job_description:
            job_context += f"\n**Job Description:** {job_description}"
        
        prompt = f"""You are an expert recruiter and career advisor with deep knowledge across ALL industries and professions. Analyze the following resume and provide intelligent skill matching for the target role.

**Resume Data:**
```json
{json.dumps(resume_json, indent=2)}
```
{job_context}

**Your Task:**
1. **Understand the Target Role Dynamically:**
   - If the role is "Teacher": Identify skills like Classroom Management, Curriculum Design, Educational Technology, Communication, Assessment, Subject Expertise, etc.
   - If the role is "Software Engineer": Identify technical skills like programming languages, frameworks, databases, infrastructure, etc.
   - If the role is "Data Scientist": Identify ML/AI skills, statistics, Python, R, data visualization, etc.
   - If the role is "Marketing Manager": Identify digital marketing, SEO, analytics, content strategy, social media, etc.
   - If the role is "Nurse": Identify patient care, medical procedures, certifications, healthcare software, etc.
   - **BE INTELLIGENT**: Use your knowledge to understand what skills are ACTUALLY needed for ANY role given, don't be limited by predefined categories.

2. **Categorize Skills Flexibly:**
   For technical roles, use:
   - **frontend**: Web UI technologies (React, Angular, Vue, HTML, CSS, JavaScript, TypeScript, etc.)
   - **backend**: Server-side frameworks and languages (Django, Flask, Node.js, Python, Java, AI/ML frameworks, etc.)
   - **database**: Databases and data tools (SQL, MongoDB, PostgreSQL, Pandas, NumPy, Excel, etc.)
   - **infra**: Infrastructure, DevOps, cloud platforms (AWS, Docker, Kubernetes, CI/CD, etc.)
   
   For non-technical roles, use:
   - **frontend**: Customer-facing, communication, presentation skills
   - **backend**: Core competencies, methodologies, domain expertise
   - **database**: Tools, systems, software proficiency
   - **infra**: Supporting skills, certifications, management abilities

3. **Intelligent Skill Matching:**
   - Extract ALL relevant skills from the resume (technical AND soft skills)
   - Match them against what the target role ACTUALLY requires
   - If the role is "Teacher" and they have "Google Classroom", that's a match!
   - If the role is "Data Scientist" and they have "TensorFlow", that's a match!
   - Think beyond rigid dictionaries - use your AI intelligence!

4. **Identify Missing Skills:**
   - Based on the target role, what important skills are MISSING?
   - Be practical and industry-aware
   - For "Teacher": Missing skills might be "Smart Board Training", "Special Education Methods"
   - For "Software Engineer": Missing skills might be "Docker", "Unit Testing"

**Output Format (MUST be valid JSON):**
```json
{{
  "frontend": ["list of relevant skills found - adapt to role context"],
  "backend": ["list of core competency skills found - adapt to role context"],
  "database": ["list of tools/systems skills found - adapt to role context"],
  "infra": ["list of supporting skills found - adapt to role context"],
  "matched_role": "The target job title or best matching role",
  "role_confidence": "high/medium/low",
  "skill_match": {{
    "frontend": ["skills they have that match the role"],
    "backend": ["skills they have that match the role"],
    "database": ["skills they have that match the role"],
    "infra": ["skills they have that match the role"]
  }},
  "skill_missing": {{
    "frontend": ["important skills missing for this role"],
    "backend": ["important skills missing for this role"],
    "database": ["important skills missing for this role"],
    "infra": ["important skills missing for this role"]
  }},
  "recommendations": "Brief, personalized recommendation for improving their candidacy for this specific role"
}}
```

**Critical Instructions:**
- BE DYNAMIC: Don't just match against a fixed dictionary - THINK about what skills the role needs!
- USE CONTEXT: If job_title is "Teacher", think about teaching skills. If it's "DevOps Engineer", think about infrastructure.
- EXTRACT EVERYTHING: Find both explicit skills (listed in skills section) AND implicit skills (from experience descriptions)
- BE PRACTICAL: Only suggest missing skills that are truly important for the role
- ONLY return valid JSON, nothing else
- If a category has no skills, use an empty array []
- Adapt the category meanings to fit the role (technical vs non-technical)
"""
        return prompt
    
    def analyze_resume_with_gemini(self, resume_json: Dict, job_title: str = None, job_description: str = None) -> Dict:
        """
        Analyze resume JSON using Gemini AI with dynamic job role understanding
        
        Args:
            resume_json: Structured resume data with fields like:
                - name: str
                - skills: List[str]
                - experience: List[Dict]
                - education: List[Dict]
                - projects: List[Dict] (optional)
            job_title: Target job role (e.g., "Teacher", "Software Engineer", "Data Scientist")
            job_description: Optional detailed job description
        
        Returns:
            Dict containing:
                - frontend: List[str] - Relevant skills (context-aware)
                - backend: List[str] - Core competency skills (context-aware)
                - database: List[str] - Tools/systems skills (context-aware)
                - infra: List[str] - Supporting skills (context-aware)
                - matched_role: str - Target or detected job role
                - skill_match: Dict - Skills the candidate has by category
                - skill_missing: Dict - Skills the candidate should learn
                - recommendations: str - Personalized recommendations
                
        Raises:
            ValueError: If API key is not configured
            Exception: For API errors
        """
        if not self.api_key:
            raise ValueError(
                "Gemini API key not configured. Set GEMINI_API_KEY environment variable."
            )
        
        try:
            logger.info(f"Analyzing resume for: {resume_json.get('name', 'Unknown')} - Target role: {job_title or 'Auto-detect'}")
            
            # Create the prompt with job context
            prompt = self._create_analysis_prompt(resume_json, job_title, job_description)
            
            # Generate content using Gemini
            logger.info("Sending request to Gemini API...")
            response = self.model.generate_content(prompt)
            
            # Extract the response text
            response_text = response.text.strip()
            logger.info("Received response from Gemini API")
            
            # Parse JSON from response
            # Remove markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif response_text.startswith("```"):
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            # Parse JSON
            result = json.loads(response_text)
            
            # Validate required fields
            required_fields = [
                "frontend", "backend", "database", "infra", 
                "matched_role", "skill_match", "skill_missing"
            ]
            for field in required_fields:
                if field not in result:
                    logger.warning(f"Missing field in Gemini response: {field}")
                    if field in ["frontend", "backend", "database", "infra"]:
                        result[field] = []
                    elif field in ["skill_match", "skill_missing"]:
                        result[field] = {
                            "frontend": [], "backend": [], 
                            "database": [], "infra": []
                        }
                    elif field == "matched_role":
                        result[field] = "General Developer"
            
            logger.info(f"Successfully analyzed resume. Role: {result.get('matched_role')}")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response as JSON: {e}")
            logger.error(f"Response text: {response_text}")
            
            # Fallback: return basic classification based on skills
            return self._fallback_analysis(resume_json, job_title)
            
        except Exception as e:
            logger.error(f"Error calling Gemini API: {str(e)}")
            
            # Fallback to basic analysis
            return self._fallback_analysis(resume_json, job_title)
    
    def _fallback_analysis(self, resume_json: Dict, job_title: str = None) -> Dict:
        """
        Fallback analysis when Gemini API fails
        Uses simple keyword matching
        
        Args:
            resume_json: Resume data
            job_title: Target job role for context
            
        Returns:
            Basic classification result
        """
        logger.info(f"Using fallback analysis method for role: {job_title or 'Auto-detect'}")
        
        skills = resume_json.get("skills", [])
        skills_lower = [s.lower() for s in skills]
        
        # Classify skills
        result = {
            "frontend": [],
            "backend": [],
            "database": [],
            "infra": []
        }
        
        for skill in skills:
            skill_lower = skill.lower()
            
            # Check each category
            for category, keywords in self.tech_categories.items():
                for keyword in keywords:
                    if keyword.lower() in skill_lower or skill_lower in keyword.lower():
                        if skill not in result[category]:
                            result[category].append(skill)
                        break
        
        # Determine role - use job_title if provided
        if job_title:
            matched_role = job_title
        else:
            has_frontend = len(result["frontend"]) > 0
            has_backend = len(result["backend"]) > 0
            has_database = len(result["database"]) > 0
            has_infra = len(result["infra"]) > 0
            
            if has_frontend and has_backend and has_database:
                matched_role = "Full Stack Developer"
            elif has_frontend and has_backend:
                matched_role = "Full Stack Developer"
            elif has_frontend:
                matched_role = "Frontend Developer"
            elif has_backend:
                matched_role = "Backend Developer"
            elif has_infra:
                matched_role = "DevOps Engineer"
            elif has_database:
                matched_role = "Database Developer"
            else:
                matched_role = "General Developer"
        
        result["matched_role"] = matched_role
        result["role_confidence"] = "low"
        result["skill_match"] = {
            "frontend": result["frontend"],
            "backend": result["backend"],
            "database": result["database"],
            "infra": result["infra"]
        }
        result["skill_missing"] = {
            "frontend": [],
            "backend": [],
            "database": [],
            "infra": []
        }
        result["recommendations"] = "API analysis unavailable. Basic classification used."
        
        return result


# Convenience function for quick usage
def analyze_resume_with_gemini(
    resume_json: Dict, 
    job_title: str = None, 
    job_description: str = None,
    api_key: Optional[str] = None
) -> Dict:
    """
    Convenience function to analyze a resume with Gemini AI
    
    Args:
        resume_json: Structured resume data
        job_title: Target job role
        job_description: Optional job description
        api_key: Optional Gemini API key
        
    Returns:
        Analysis result dictionary
    """
    analyzer = GeminiResumeAnalyzer(api_key=api_key)
    return analyzer.analyze_resume_with_gemini(resume_json, job_title, job_description)


# Example usage
if __name__ == "__main__":
    # Example resume data
    example_resume = {
        "name": "John Doe",
        "skills": ["ReactJS", "Django", "SQL", "Docker", "Python", "JavaScript"],
        "experience": [
            {
                "title": "Full Stack Developer",
                "company": "Tech Corp",
                "duration": "2020-2023",
                "description": "Built web applications using React and Django"
            }
        ],
        "education": [
            {
                "degree": "Bachelor of Science in Computer Science",
                "institution": "University XYZ",
                "year": "2020"
            }
        ],
        "projects": [
            {
                "name": "E-commerce Platform",
                "technologies": ["React", "Node.js", "MongoDB"],
                "description": "Built a full-stack e-commerce platform"
            }
        ]
    }
    
    try:
        result = analyze_resume_with_gemini(example_resume)
        print("Analysis Result:")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error: {e}")
