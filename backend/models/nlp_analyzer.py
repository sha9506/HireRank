"""
NLP Analysis module for semantic similarity and skill extraction
Uses HuggingFace Transformers for sentence embeddings and summarization
"""

import logging
from typing import List, Dict, Optional
import re
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    from transformers import pipeline
    import torch
except ImportError as e:
    logging.error(f"Required ML libraries not installed: {e}")
    SentenceTransformer = None
    pipeline = None

logger = logging.getLogger(__name__)


class NLPAnalyzer:
    """Handles NLP tasks for resume analysis"""
    
    # Job title to skills mapping
    JOB_TITLE_SKILLS = {
        'data scientist': ['python', 'machine learning', 'statistics', 'pandas', 'sql', 'tensorflow', 'pytorch', 'scikit-learn', 'numpy', 'data visualization', 'r', 'deep learning'],
        'software engineer': ['python', 'java', 'javascript', 'git', 'algorithms', 'data structures', 'oop', 'api design', 'testing', 'debugging', 'agile'],
        'full stack developer': ['react', 'node.js', 'javascript', 'html', 'css', 'mongodb', 'sql', 'rest api', 'git', 'docker', 'aws'],
        'frontend developer': ['react', 'vue', 'angular', 'javascript', 'typescript', 'html', 'css', 'sass', 'webpack', 'responsive design', 'ui/ux'],
        'backend developer': ['python', 'java', 'node.js', 'sql', 'mongodb', 'rest api', 'microservices', 'docker', 'kubernetes', 'redis', 'rabbitmq'],
        'devops engineer': ['docker', 'kubernetes', 'jenkins', 'ci/cd', 'aws', 'azure', 'terraform', 'ansible', 'linux', 'bash', 'git'],
        'machine learning engineer': ['python', 'tensorflow', 'pytorch', 'machine learning', 'deep learning', 'nlp', 'computer vision', 'mlops', 'docker', 'aws', 'sql'],
        'data engineer': ['python', 'sql', 'spark', 'hadoop', 'kafka', 'airflow', 'etl', 'data warehousing', 'aws', 'snowflake', 'mongodb'],
        'cloud engineer': ['aws', 'azure', 'gcp', 'terraform', 'kubernetes', 'docker', 'serverless', 'lambda', 'networking', 'security'],
        'mobile developer': ['react native', 'flutter', 'swift', 'kotlin', 'ios', 'android', 'mobile ui', 'rest api', 'firebase', 'git'],
        'qa engineer': ['selenium', 'pytest', 'jest', 'api testing', 'automation', 'manual testing', 'test cases', 'bug tracking', 'jira', 'agile'],
        'product manager': ['product strategy', 'roadmap', 'agile', 'scrum', 'stakeholder management', 'data analysis', 'user research', 'jira', 'sql'],
        'ui/ux designer': ['figma', 'sketch', 'adobe xd', 'user research', 'wireframing', 'prototyping', 'design systems', 'responsive design', 'usability testing'],
        'business analyst': ['sql', 'excel', 'data analysis', 'tableau', 'power bi', 'requirements gathering', 'documentation', 'agile', 'jira'],
        'cybersecurity analyst': ['penetration testing', 'network security', 'siem', 'firewall', 'vulnerability assessment', 'python', 'linux', 'compliance', 'incident response'],
        'network engineer': ['cisco', 'routing', 'switching', 'tcp/ip', 'vpn', 'firewall', 'network troubleshooting', 'lan/wan', 'bgp', 'ospf'],
        'project manager': ['project management', 'agile', 'scrum', 'risk management', 'budgeting', 'stakeholder communication', 'pmp', 'jira', 'ms project'],
        'systems administrator': ['linux', 'windows server', 'active directory', 'bash', 'powershell', 'vmware', 'backup', 'monitoring', 'troubleshooting'],
    }
    
    # Common technical and soft skills database
    SKILL_KEYWORDS = {
        'programming': [
            'python', 'java', 'javascript', 'typescript', 'c\\+\\+', 'c#', 'ruby',
            'go', 'rust', 'scala', 'kotlin', 'swift', 'php', 'r', 'matlab'
        ],
        'web': [
            'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask',
            'fastapi', 'spring', 'asp.net', 'html', 'css', 'sass', 'webpack'
        ],
        'data': [
            'sql', 'mongodb', 'postgresql', 'mysql', 'redis', 'elasticsearch',
            'spark', 'hadoop', 'kafka', 'airflow', 'tableau', 'power bi'
        ],
        'ml_ai': [
            'machine learning', 'deep learning', 'neural networks', 'tensorflow',
            'pytorch', 'keras', 'scikit-learn', 'nlp', 'computer vision', 'bert',
            'transformers', 'gan', 'reinforcement learning'
        ],
        'cloud': [
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform',
            'jenkins', 'ci/cd', 'github actions', 'gitlab', 'serverless'
        ],
        'soft_skills': [
            'leadership', 'communication', 'teamwork', 'problem solving',
            'analytical', 'critical thinking', 'agile', 'scrum', 'project management'
        ]
    }
    
    def __init__(self):
        """Initialize NLP models"""
        self.similarity_model = None
        self.summarizer = None
        
        if SentenceTransformer:
            try:
                logger.info("Loading sentence transformer model...")
                self.similarity_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
                logger.info("Sentence transformer loaded successfully")
            except Exception as e:
                logger.error(f"Error loading sentence transformer: {e}")
        
        if pipeline:
            try:
                logger.info("Loading summarization model...")
                # Use a smaller model for faster inference
                self.summarizer = pipeline(
                    "summarization",
                    model="facebook/bart-large-cnn",
                    device=0 if torch.cuda.is_available() else -1
                )
                logger.info("Summarization model loaded successfully")
            except Exception as e:
                logger.warning(f"Could not load summarization model: {e}")
                self.summarizer = None
    
    def extract_skills(self, resume_text: str) -> List[str]:
        """
        Extract skills from resume text using keyword matching
        
        Args:
            resume_text: Text extracted from resume
        
        Returns:
            List of identified skills
        """
        resume_lower = resume_text.lower()
        found_skills = []
        
        for category, skills in self.SKILL_KEYWORDS.items():
            for skill in skills:
                # Use word boundary regex for accurate matching
                pattern = r'\b' + skill.replace('+', '\\+').replace('.', '\\.') + r'\b'
                if re.search(pattern, resume_lower, re.IGNORECASE):
                    # Format skill nicely
                    formatted_skill = skill.replace('\\+', '+').replace('\\.', '.').title()
                    if formatted_skill not in found_skills:
                        found_skills.append(formatted_skill)
        
        return sorted(found_skills)
    
    def calculate_similarity(self, resume_text: str, job_description: str) -> float:
        """
        Calculate semantic similarity between resume and job description
        
        Args:
            resume_text: Text extracted from resume
            job_description: Job description text
        
        Returns:
            Similarity score (0-100)
        """
        if not self.similarity_model:
            logger.warning("Similarity model not loaded. Using fallback method.")
            return self._fallback_similarity(resume_text, job_description)
        
        try:
            # Encode texts to embeddings
            resume_embedding = self.similarity_model.encode(resume_text, convert_to_tensor=True)
            job_embedding = self.similarity_model.encode(job_description, convert_to_tensor=True)
            
            # Calculate cosine similarity
            from torch.nn.functional import cosine_similarity
            similarity = cosine_similarity(
                resume_embedding.unsqueeze(0),
                job_embedding.unsqueeze(0)
            ).item()
            
            # Convert to 0-100 scale
            # Cosine similarity is between -1 and 1, but typically 0.2-0.9 for text
            # We'll scale and adjust to give meaningful scores
            score = max(0, min(100, (similarity * 100)))
            
            # Apply some boost logic based on keyword overlap
            keyword_boost = self._calculate_keyword_overlap(resume_text, job_description)
            final_score = min(100, score * 0.7 + keyword_boost * 0.3)
            
            return final_score
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return self._fallback_similarity(resume_text, job_description)
    
    def _fallback_similarity(self, resume_text: str, job_description: str) -> float:
        """
        Fallback similarity calculation using keyword overlap
        """
        return self._calculate_keyword_overlap(resume_text, job_description)
    
    def _calculate_keyword_overlap(self, resume_text: str, job_description: str) -> float:
        """
        Calculate keyword overlap between resume and job description
        """
        # Extract meaningful words (remove common words)
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                     'of', 'with', 'is', 'are', 'was', 'were', 'been', 'be', 'have', 'has',
                     'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could', 'may',
                     'might', 'must', 'can', 'this', 'that', 'these', 'those'}
        
        def extract_keywords(text):
            words = re.findall(r'\b[a-z]{3,}\b', text.lower())
            return set(w for w in words if w not in stopwords)
        
        resume_keywords = extract_keywords(resume_text)
        job_keywords = extract_keywords(job_description)
        
        if not job_keywords:
            return 0.0
        
        overlap = len(resume_keywords & job_keywords)
        score = (overlap / len(job_keywords)) * 100
        
        return min(100, score)
    
    def generate_summary(self, resume_text: str, job_description: str, match_score: float) -> str:
        """
        Generate AI-powered summary explaining why candidate fits the role
        
        Args:
            resume_text: Text extracted from resume
            job_description: Job description text
            match_score: Calculated match score
        
        Returns:
            Summary text
        """
        if self.summarizer and match_score > 50:
            try:
                # Create a combined text for context
                combined_text = f"Job Requirements: {job_description[:500]}... Candidate Profile: {resume_text[:500]}..."
                
                # Generate summary
                if len(combined_text) > 100:
                    summary_result = self.summarizer(
                        combined_text,
                        max_length=80,
                        min_length=30,
                        do_sample=False
                    )
                    
                    if summary_result and len(summary_result) > 0:
                        base_summary = summary_result[0]['summary_text']
                        return self._enhance_summary(base_summary, match_score)
            except Exception as e:
                logger.warning(f"Error generating AI summary: {e}")
        
        # Fallback to template-based summary
        return self._generate_template_summary(resume_text, job_description, match_score)
    
    def _enhance_summary(self, base_summary: str, match_score: float) -> str:
        """Enhance AI-generated summary with match score context"""
        if match_score >= 80:
            prefix = "Excellent match: "
        elif match_score >= 60:
            prefix = "Good match: "
        elif match_score >= 40:
            prefix = "Moderate match: "
        else:
            prefix = "Partial match: "
        
        return prefix + base_summary
    
    def _generate_template_summary(self, resume_text: str, job_description: str, match_score: float) -> str:
        """Generate template-based summary when AI model is unavailable"""
        skills = self.extract_skills(resume_text)
        
        if match_score >= 80:
            return f"Highly qualified candidate with {len(skills)} relevant skills including {', '.join(skills[:3])}. Strong alignment with job requirements."
        elif match_score >= 60:
            return f"Well-suited candidate with {len(skills)} matching skills such as {', '.join(skills[:3])}. Good potential for the role."
        elif match_score >= 40:
            return f"Candidate shows {len(skills)} relevant competencies including {', '.join(skills[:2])}. May require additional evaluation."
        else:
            if skills:
                return f"Candidate has some transferable skills ({', '.join(skills[:2])}), but limited direct match with requirements."
            else:
                return "Limited overlap with job requirements based on keyword analysis. Consider manual review."
    
    def get_skills_for_job_title(self, job_title: str) -> List[str]:
        """
        Get relevant skills for a given job title
        
        Args:
            job_title: Job title string
        
        Returns:
            List of relevant skills for the job
        """
        job_title_lower = job_title.lower().strip()
        
        # Direct match
        if job_title_lower in self.JOB_TITLE_SKILLS:
            return self.JOB_TITLE_SKILLS[job_title_lower]
        
        # Partial match
        for key, skills in self.JOB_TITLE_SKILLS.items():
            if key in job_title_lower or job_title_lower in key:
                return skills
        
        # Default: extract from job title text
        logger.warning(f"No predefined skills for job title: {job_title}. Extracting from text.")
        return self.extract_skills(job_title)
    
    def extract_candidate_name(self, resume_text: str) -> str:
        """
        Extract candidate name from resume text using multiple strategies
        
        Args:
            resume_text: Text extracted from resume
        
        Returns:
            Candidate name or "Unknown"
        """
        lines = resume_text.split('\n')
        
        # Strategy 1: First few lines with capitalized words (2-4 words)
        for line in lines[:15]:
            line = line.strip()
            # Remove common prefixes
            line = re.sub(r'^(resume|curriculum vitae|cv)\s*[-:]*\s*', '', line, flags=re.IGNORECASE)
            
            if len(line) > 2 and len(line) < 50:
                words = line.split()
                # Check for name pattern: 2-4 capitalized words
                if 2 <= len(words) <= 4:
                    if all(word[0].isupper() for word in words if word and word[0].isalpha()):
                        # Exclude lines with common keywords
                        exclude_keywords = ['phone', 'email', 'address', 'linkedin', 'github', 'portfolio', 
                                           'objective', 'summary', 'education', 'experience', 'skills']
                        if not any(keyword in line.lower() for keyword in exclude_keywords):
                            return line
        
        # Strategy 2: Look for "Name:" or similar patterns
        name_patterns = [
            r'name\s*:\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
            r'candidate\s*:\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
            r'applicant\s*:\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, resume_text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        # Strategy 3: First line with only letters and spaces (likely a name)
        for line in lines[:10]:
            line = line.strip()
            if 5 <= len(line) <= 40 and re.match(r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+$', line):
                return line
        
        return "Unknown"

