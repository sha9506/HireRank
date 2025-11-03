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
    # JOB_TITLE_SKILLS = {
    #     'data scientist': ['python', 'machine learning', 'statistics', 'pandas', 'sql', 'tensorflow', 'pytorch', 'scikit-learn', 'numpy', 'data visualization', 'r', 'deep learning'],
    #     'software engineer': ['python', 'java', 'javascript', 'git', 'algorithms', 'data structures', 'oop', 'api design', 'testing', 'debugging', 'agile'],
    #     'full stack developer': ['react', 'node.js', 'javascript', 'html', 'css', 'mongodb', 'sql', 'rest api', 'git', 'docker', 'aws'],
    #     'frontend developer': ['react', 'vue', 'angular', 'javascript', 'typescript', 'html', 'css', 'sass', 'webpack', 'responsive design', 'ui/ux'],
    #     'backend developer': ['python', 'java', 'node.js', 'sql', 'mongodb', 'rest api', 'microservices', 'docker', 'kubernetes', 'redis', 'rabbitmq'],
    #     'devops engineer': ['docker', 'kubernetes', 'jenkins', 'ci/cd', 'aws', 'azure', 'terraform', 'ansible', 'linux', 'bash', 'git'],
    #     'machine learning engineer': ['python', 'tensorflow', 'pytorch', 'machine learning', 'deep learning', 'nlp', 'computer vision', 'mlops', 'docker', 'aws', 'sql'],
    #     'data engineer': ['python', 'sql', 'spark', 'hadoop', 'kafka', 'airflow', 'etl', 'data warehousing', 'aws', 'snowflake', 'mongodb'],
    #     'cloud engineer': ['aws', 'azure', 'gcp', 'terraform', 'kubernetes', 'docker', 'serverless', 'lambda', 'networking', 'security'],
    #     'mobile developer': ['react native', 'flutter', 'swift', 'kotlin', 'ios', 'android', 'mobile ui', 'rest api', 'firebase', 'git'],
    #     'qa engineer': ['selenium', 'pytest', 'jest', 'api testing', 'automation', 'manual testing', 'test cases', 'bug tracking', 'jira', 'agile'],
    #     'product manager': ['product strategy', 'roadmap', 'agile', 'scrum', 'stakeholder management', 'data analysis', 'user research', 'jira', 'sql'],
    #     'ui/ux designer': ['figma', 'sketch', 'adobe xd', 'user research', 'wireframing', 'prototyping', 'design systems', 'responsive design', 'usability testing'],
    #     'business analyst': ['sql', 'excel', 'data analysis', 'tableau', 'power bi', 'requirements gathering', 'documentation', 'agile', 'jira'],
    #     'cybersecurity analyst': ['penetration testing', 'network security', 'siem', 'firewall', 'vulnerability assessment', 'python', 'linux', 'compliance', 'incident response'],
    #     'network engineer': ['cisco', 'routing', 'switching', 'tcp/ip', 'vpn', 'firewall', 'network troubleshooting', 'lan/wan', 'bgp', 'ospf'],
    #     'project manager': ['project management', 'agile', 'scrum', 'risk management', 'budgeting', 'stakeholder communication', 'pmp', 'jira', 'ms project'],
    #     'systems administrator': ['linux', 'windows server', 'active directory', 'bash', 'powershell', 'vmware', 'backup', 'monitoring', 'troubleshooting'],
    # }
    
    JOB_TITLE_SKILLS = {
    # --- Core Software Roles ---
    'software engineer': [
        'python', 'java', 'c++', 'c#', 'javascript', 'typescript',
        'git', 'github', 'bitbucket', 'gitlab', 'rest api', 'graphql',
        'data structures', 'algorithms', 'oop', 'design patterns',
        'unit testing', 'integration testing', 'ci/cd', 'jenkins',
        'docker', 'kubernetes', 'agile', 'scrum', 'debugging', 'system design'
    ],
    'sde': [],  # alias for software engineer (auto-map in your code)

    'full stack developer': [
        'react', 'next.js', 'angular', 'vue', 'node.js', 'express',
        'html', 'css', 'javascript', 'typescript', 'tailwind', 'bootstrap',
        'mongodb', 'mysql', 'postgresql', 'firebase', 'rest api', 'graphql',
        'docker', 'aws', 'nginx', 'ci/cd', 'microservices'
    ],
    'frontend developer': [
        'react', 'next.js', 'vue', 'angular', 'svelte', 'typescript',
        'html', 'css', 'sass', 'less', 'webpack', 'vite', 'redux',
        'responsive design', 'ui/ux', 'accessibility', 'figma'
    ],
    'backend developer': [
        'python', 'java', 'go', 'node.js', 'express', 'django', 'flask', 'fastapi',
        'sql', 'mongodb', 'postgresql', 'redis', 'elasticsearch', 'rest api', 'graphql',
        'microservices', 'docker', 'kubernetes', 'aws', 'gcp', 'azure', 'rabbitmq', 'kafka'
    ],

    # --- Data & AI ---
    'data scientist': [
        'python', 'r', 'sql', 'pandas', 'numpy', 'matplotlib', 'seaborn',
        'scikit-learn', 'tensorflow', 'pytorch', 'keras', 'statistics',
        'data visualization', 'feature engineering', 'ml algorithms', 'nlp',
        'deep learning', 'data preprocessing', 'jupyter', 'azure ml', 'aws sagemaker'
    ],
    'machine learning engineer': [
        'python', 'tensorflow', 'pytorch', 'scikit-learn', 'mlops', 'docker', 'kubernetes',
        'mlflow', 'airflow', 'aws', 'gcp', 'feature store', 'deep learning', 'computer vision',
        'nlp', 'huggingface', 'transformers', 'model optimization', 'api deployment', 'fastapi'
    ],
    'data engineer': [
        'python', 'java', 'scala', 'spark', 'pyspark', 'hadoop', 'hive',
        'airflow', 'kafka', 'flink', 'etl', 'data pipelines', 'data warehousing',
        'snowflake', 'redshift', 'bigquery', 'aws glue', 'azure data factory',
        'lakehouse', 'databricks', 'delta lake', 'postgresql', 'mongodb'
    ],
    'data analyst': [
        'sql', 'excel', 'power bi', 'tableau', 'looker', 'python',
        'pandas', 'statistics', 'data visualization', 'data cleaning',
        'reporting', 'dashboarding', 'storytelling'
    ],

    # --- DevOps & Infra ---
    'devops engineer': [
        'linux', 'bash', 'shell scripting', 'docker', 'kubernetes',
        'jenkins', 'gitlab ci', 'aws', 'azure', 'gcp', 'terraform', 'ansible',
        'prometheus', 'grafana', 'elk stack', 'ci/cd', 'monitoring', 'helm', 'nginx'
    ],
    'cloud engineer': [
        'aws', 'azure', 'gcp', 'terraform', 'cloudformation', 'docker', 'kubernetes',
        'lambda', 'serverless', 'cloudwatch', 'networking', 'load balancing',
        'security', 'iam', 's3', 'ec2', 'vpc', 'dns', 'cdn'
    ],
    'site reliability engineer': [
        'linux', 'kubernetes', 'prometheus', 'grafana', 'monitoring',
        'incident response', 'sre', 'devops', 'ansible', 'terraform', 'aws', 'gcp', 'python'
    ],

    # --- Security & Networks ---
    'cybersecurity analyst': [
        'network security', 'penetration testing', 'siem', 'splunk', 'firewall',
        'vulnerability assessment', 'incident response', 'forensics', 'python',
        'wireshark', 'nmap', 'burp suite', 'owasp', 'compliance', 'iso 27001'
    ],
    'network engineer': [
        'cisco', 'routing', 'switching', 'tcp/ip', 'vpn', 'firewall',
        'network troubleshooting', 'lan', 'wan', 'ospf', 'bgp', 'load balancer', 'network monitoring'
    ],

    # --- Management & Product ---
    'product manager': [
        'product strategy', 'roadmap', 'agile', 'scrum', 'user research',
        'data analysis', 'stakeholder management', 'a/b testing', 'sql', 'jira', 'analytics', 'kpi tracking'
    ],
    'project manager': [
        'project management', 'agile', 'scrum', 'kanban', 'risk management',
        'budgeting', 'stakeholder communication', 'pmp', 'jira', 'ms project', 'team leadership'
    ],
    'business analyst': [
        'requirements gathering', 'sql', 'excel', 'tableau', 'power bi',
        'data modeling', 'documentation', 'agile', 'jira', 'process improvement'
    ],

    # --- Design & Mobile ---
    'ui/ux designer': [
        'figma', 'sketch', 'adobe xd', 'photoshop', 'illustrator',
        'wireframing', 'prototyping', 'design systems', 'responsive design',
        'usability testing', 'user research', 'interaction design', 'accessibility'
    ],
    'mobile developer': [
        'react native', 'flutter', 'swift', 'kotlin', 'ios', 'android',
        'firebase', 'mobile ui', 'push notifications', 'api integration',
        'xcode', 'android studio'
    ],

    # --- Systems & Admin ---
    'systems administrator': [
        'linux', 'windows server', 'active directory', 'bash', 'powershell',
        'vmware', 'backup', 'networking', 'monitoring', 'troubleshooting', 'security'
    ]
}

    # Layered skill stacks for role-based analysis
    # Each role maps to technology layers with specific tools/frameworks
    JOB_TITLE_STACKS = {
        'full stack developer': {
            'frontend': ['react', 'angular', 'vue', 'next.js', 'svelte', 'typescript', 'html', 'css', 'tailwind', 'bootstrap'],
            'backend': ['django', 'flask', 'fastapi', 'node.js', 'express', 'spring boot', 'nest.js', 'go', 'rust'],
            'database': ['sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'firebase', 'dynamodb'],
            'infrastructure': ['docker', 'kubernetes', 'aws', 'azure', 'gcp', 'git', 'nginx', 'ci/cd']
        },
        'frontend developer': {
            'frameworks': ['react', 'angular', 'vue', 'next.js', 'svelte', 'gatsby'],
            'languages': ['javascript', 'typescript', 'html', 'css', 'sass', 'less'],
            'tools': ['webpack', 'vite', 'babel', 'npm', 'yarn', 'pnpm'],
            'ui_libraries': ['tailwind', 'bootstrap', 'material-ui', 'chakra-ui', 'styled-components'],
            'state_management': ['redux', 'zustand', 'mobx', 'context api', 'recoil']
        },
        'backend developer': {
            'languages': ['python', 'java', 'node.js', 'go', 'rust', 'c#', 'php'],
            'frameworks': ['django', 'flask', 'fastapi', 'express', 'spring boot', 'nest.js', '.net'],
            'database': ['postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch', 'cassandra'],
            'api': ['rest api', 'graphql', 'grpc', 'websockets'],
            'infrastructure': ['docker', 'kubernetes', 'aws', 'azure', 'microservices', 'kafka', 'rabbitmq']
        },
        'data scientist': {
            'languages': ['python', 'r', 'sql', 'julia'],
            'ml_libraries': ['scikit-learn', 'tensorflow', 'pytorch', 'keras', 'xgboost', 'lightgbm'],
            'data_processing': ['pandas', 'numpy', 'scipy', 'polars', 'dask'],
            'visualization': ['matplotlib', 'seaborn', 'plotly', 'tableau', 'power bi'],
            'cloud': ['aws', 'azure', 'gcp', 'databricks', 'sagemaker']
        },
        'machine learning engineer': {
            'ml_frameworks': ['tensorflow', 'pytorch', 'scikit-learn', 'keras', 'huggingface'],
            'mlops': ['mlflow', 'kubeflow', 'airflow', 'prefect', 'dagster'],
            'deployment': ['docker', 'kubernetes', 'fastapi', 'flask', 'aws', 'gcp'],
            'monitoring': ['prometheus', 'grafana', 'wandb', 'tensorboard'],
            'specialized': ['nlp', 'computer vision', 'deep learning', 'transformers', 'onnx']
        },
        'data engineer': {
            'languages': ['python', 'java', 'scala', 'sql'],
            'processing': ['spark', 'pyspark', 'flink', 'hadoop', 'hive'],
            'orchestration': ['airflow', 'prefect', 'dagster', 'luigi'],
            'storage': ['snowflake', 'redshift', 'bigquery', 'databricks', 'delta lake'],
            'streaming': ['kafka', 'kinesis', 'pub/sub', 'rabbitmq'],
            'cloud': ['aws', 'azure', 'gcp', 'terraform']
        },
        'devops engineer': {
            'containerization': ['docker', 'kubernetes', 'helm', 'podman'],
            'ci_cd': ['jenkins', 'github actions', 'gitlab ci', 'circleci', 'travis ci'],
            'iac': ['terraform', 'ansible', 'cloudformation', 'pulumi'],
            'cloud': ['aws', 'azure', 'gcp', 'digitalocean'],
            'monitoring': ['prometheus', 'grafana', 'elk stack', 'datadog', 'new relic'],
            'scripting': ['bash', 'python', 'powershell', 'groovy']
        },
        'cloud engineer': {
            'cloud_platforms': ['aws', 'azure', 'gcp', 'alibaba cloud'],
            'iac': ['terraform', 'cloudformation', 'pulumi', 'ansible'],
            'containerization': ['docker', 'kubernetes', 'ecs', 'aks', 'gke'],
            'networking': ['vpc', 'load balancing', 'cdn', 'dns', 'firewall'],
            'serverless': ['lambda', 'azure functions', 'cloud functions', 'fargate']
        },
        'mobile developer': {
            'cross_platform': ['react native', 'flutter', 'ionic', 'xamarin'],
            'native_ios': ['swift', 'objective-c', 'xcode', 'swiftui'],
            'native_android': ['kotlin', 'java', 'android studio', 'jetpack compose'],
            'backend': ['firebase', 'aws amplify', 'supabase', 'rest api'],
            'tools': ['git', 'fastlane', 'app center', 'testflight']
        },
        'qa engineer': {
            'automation': ['selenium', 'cypress', 'playwright', 'puppeteer', 'appium'],
            'frameworks': ['pytest', 'jest', 'junit', 'testng', 'mocha'],
            'api_testing': ['postman', 'rest assured', 'karate', 'insomnia'],
            'performance': ['jmeter', 'gatling', 'locust', 'k6'],
            'tools': ['jira', 'testrail', 'git', 'ci/cd', 'docker']
        }
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
    
    def analyze_role_skills(self, skills: List[str], role: str) -> Dict[str, Dict[str, List[str]]]:
        """
        Analyze candidate skills against role-specific technology stacks.
        Returns matched and missing skills for each technology layer.
        
        Args:
            skills: List of candidate skills (case-insensitive)
            role: Job role/title (e.g., "Full Stack Developer")
        
        Returns:
            Dictionary with matched and missing skills per layer:
            {
                "frontend": {"matched": ["react"], "missing": ["angular", "vue"]},
                "backend": {"matched": ["django"], "missing": ["flask", "node.js"]},
                ...
            }
        
        Example:
            >>> analyzer = NLPAnalyzer()
            >>> result = analyzer.analyze_role_skills(["react", "django", "sql"], "full stack developer")
            >>> print(result["frontend"]["matched"])
            ['react']
        """
        role_lower = role.lower().strip()
        
        # Get the role's technology stack
        role_stack = None
        if role_lower in self.JOB_TITLE_STACKS:
            role_stack = self.JOB_TITLE_STACKS[role_lower]
        else:
            # Try partial match
            for key in self.JOB_TITLE_STACKS.keys():
                if key in role_lower or role_lower in key:
                    role_stack = self.JOB_TITLE_STACKS[key]
                    break
        
        # If no stack found, return empty result
        if not role_stack:
            logger.warning(f"No technology stack found for role: {role}")
            return {}
        
        # Normalize candidate skills to lowercase
        candidate_skills_lower = [s.lower().strip() for s in skills]
        
        # Analyze each technology layer
        result = {}
        for layer, layer_skills in role_stack.items():
            matched = []
            missing = []
            
            for skill in layer_skills:
                skill_lower = skill.lower().strip()
                # Check if candidate has this skill
                if skill_lower in candidate_skills_lower:
                    matched.append(skill)
                else:
                    missing.append(skill)
            
            result[layer] = {
                "matched": matched,
                "missing": missing
            }
        
        return result
    
    def summarize_skill_match(self, skills: List[str], role: str) -> Dict[str, Dict[str, str]]:
        """
        Simplified skill match summary for frontend display.
        Groups matched and missing skills by layer, formatted as comma-separated strings.
        
        Args:
            skills: List of candidate skills
            role: Job role/title
        
        Returns:
            Dictionary with "Skill Match" and "Skill Missing" sections:
            {
                "Skill Match": {
                    "frontend": "react, next.js",
                    "backend": "django",
                    "database": "sql"
                },
                "Skill Missing": {
                    "frontend": "angular, vue",
                    "backend": "flask, node.js",
                    "database": "mysql, mongodb, postgresql"
                }
            }
        
        Example:
            >>> analyzer = NLPAnalyzer()
            >>> summary = analyzer.summarize_skill_match(["react", "django", "sql"], "full stack developer")
            >>> print(summary["Skill Match"]["frontend"])
            'react'
        """
        # Get detailed analysis
        analysis = self.analyze_role_skills(skills, role)
        
        if not analysis:
            return {
                "Skill Match": {},
                "Skill Missing": {}
            }
        
        skill_match = {}
        skill_missing = {}
        
        # Format each layer's skills as comma-separated strings
        for layer, layer_data in analysis.items():
            matched_skills = layer_data.get("matched", [])
            missing_skills = layer_data.get("missing", [])
            
            # Only include layers with at least one skill
            if matched_skills:
                skill_match[layer] = ", ".join(matched_skills)
            else:
                skill_match[layer] = "-"
            
            if missing_skills:
                skill_missing[layer] = ", ".join(missing_skills)
            else:
                skill_missing[layer] = "-"
        
        return {
            "Skill Match": skill_match,
            "Skill Missing": skill_missing
        }
    
    def is_role_match(self, skills: List[str], role: str) -> bool:
        """
        Check if candidate is a good match for the role.
        Returns True if candidate has at least one skill from every major technology layer.
        
        Args:
            skills: List of candidate skills
            role: Job role/title
        
        Returns:
            True if candidate has skills in all major layers, False otherwise
        
        Example:
            >>> analyzer = NLPAnalyzer()
            >>> analyzer.is_role_match(["react", "django", "sql"], "full stack developer")
            True
            >>> analyzer.is_role_match(["react", "sql"], "full stack developer")
            False  # Missing backend
        """
        analysis = self.analyze_role_skills(skills, role)
        
        if not analysis:
            return False
        
        # Check if candidate has at least one skill in each layer
        for layer, layer_data in analysis.items():
            matched_skills = layer_data.get("matched", [])
            if not matched_skills:  # No skills matched in this layer
                return False
        
        return True
    
    def get_skill_coverage_percentage(self, skills: List[str], role: str) -> Dict[str, float]:
        """
        Calculate percentage of skills covered for each technology layer.
        
        Args:
            skills: List of candidate skills
            role: Job role/title
        
        Returns:
            Dictionary mapping each layer to its coverage percentage:
            {
                "frontend": 25.0,  # 1 out of 4 skills
                "backend": 50.0,   # 2 out of 4 skills
                ...
            }
        """
        analysis = self.analyze_role_skills(skills, role)
        
        if not analysis:
            return {}
        
        coverage = {}
        for layer, layer_data in analysis.items():
            matched = len(layer_data.get("matched", []))
            total = matched + len(layer_data.get("missing", []))
            
            if total > 0:
                coverage[layer] = round((matched / total) * 100, 1)
            else:
                coverage[layer] = 0.0
        
        return coverage

