"""
Resume text extraction and processing module
Supports PDF, DOCX, and image formats (JPG, PNG)
"""

import io
import re
import os
import platform
from typing import Dict, Any
import logging

try:
    from pdfminer.high_level import extract_text as extract_pdf_text
    from pdfminer.pdfparser import PDFSyntaxError
except ImportError:
    extract_pdf_text = None

try:
    import docx2txt
except ImportError:
    docx2txt = None

try:
    from PIL import Image
    import pytesseract
    
    # Configure Tesseract path for Windows
    if platform.system() == 'Windows':
        # Common installation paths for Tesseract on Windows
        possible_paths = [
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
            r'C:\Users\{}\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'.format(os.getenv('USERNAME', ''))
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                break
except ImportError:
    Image = None
    pytesseract = None

logger = logging.getLogger(__name__)


class ResumeProcessor:
    """Handles resume text extraction and candidate information parsing"""
    
    def __init__(self):
        """Initialize the resume processor"""
        if not extract_pdf_text:
            logger.warning("pdfminer.six not installed. PDF extraction will not work.")
        if not docx2txt:
            logger.warning("docx2txt not installed. DOCX extraction will not work.")
        if not Image or not pytesseract:
            logger.warning("PIL/pytesseract not installed. Image OCR will not work.")
    
    def extract_text(self, file_content: bytes, filename: str) -> str:
        """
        Extract text from PDF, DOCX, or image file
        
        Args:
            file_content: Binary content of the file
            filename: Name of the file
        
        Returns:
            Extracted text as string
        """
        try:
            if filename.endswith('.pdf'):
                return self._extract_from_pdf(file_content)
            elif filename.endswith(('.docx', '.doc')):
                return self._extract_from_docx(file_content)
            elif filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                return self._extract_from_image(file_content)
            else:
                raise ValueError(f"Unsupported file format: {filename}")
        except Exception as e:
            logger.error(f"Error extracting text from {filename}: {str(e)}")
            raise
    
    def _extract_from_pdf(self, file_content: bytes) -> str:
        """Extract text from PDF file"""
        if not extract_pdf_text:
            raise RuntimeError("PDF extraction not available. Install pdfminer.six")
        
        try:
            # Use BytesIO to treat bytes as file-like object
            pdf_file = io.BytesIO(file_content)
            text = extract_pdf_text(pdf_file)
            return text.strip()
        except PDFSyntaxError as e:
            logger.error(f"PDF syntax error: {str(e)}")
            raise ValueError("Invalid or corrupted PDF file")
        except Exception as e:
            logger.error(f"Error extracting PDF: {str(e)}")
            raise
    
    def _extract_from_docx(self, file_content: bytes) -> str:
        """Extract text from DOCX file"""
        if not docx2txt:
            raise RuntimeError("DOCX extraction not available. Install docx2txt")
        
        try:
            # Use BytesIO to treat bytes as file-like object
            docx_file = io.BytesIO(file_content)
            text = docx2txt.process(docx_file)
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting DOCX: {str(e)}")
            raise
    
    def _extract_from_image(self, file_content: bytes) -> str:
        """Extract text from image file using OCR"""
        if not Image or not pytesseract:
            raise RuntimeError(
                "Image OCR not available. Please install Pillow and pytesseract: "
                "pip install Pillow pytesseract"
            )
        
        try:
            # Open image from bytes
            image_file = io.BytesIO(file_content)
            image = Image.open(image_file)
            
            # Perform OCR
            text = pytesseract.image_to_string(image)
            return text.strip()
        except pytesseract.TesseractNotFoundError:
            error_msg = (
                "Tesseract OCR is not installed or not in PATH. "
                "Please install Tesseract OCR:\n"
                "Windows: winget install --id UB-Mannheim.TesseractOCR\n"
                "Or download from: https://github.com/UB-Mannheim/tesseract/wiki"
            )
            logger.error(error_msg)
            raise ValueError(
                "Image files are not supported at this time. Please upload a PDF or DOCX file instead. "
                "(Tesseract OCR not installed)"
            )
        except Exception as e:
            logger.error(f"Error extracting text from image: {str(e)}")
            raise ValueError(f"Failed to extract text from image: {str(e)}")
    
    def extract_candidate_info(self, resume_text: str) -> Dict[str, Any]:
        """
        Extract candidate information from resume text
        
        Args:
            resume_text: Extracted resume text
        
        Returns:
            Dictionary containing candidate information
        """
        info = {
            "name": self._extract_name(resume_text),
            "email": self._extract_email(resume_text),
            "phone": self._extract_phone(resume_text),
            "education": self._extract_education_detailed(resume_text),
            "experience_years": self._estimate_experience(resume_text),
            "experience": self._extract_experience_detailed(resume_text),
            "certifications": self._extract_certifications(resume_text),
            "skills": self._extract_skills_basic(resume_text)
        }
        return info
    
    def _extract_email(self, text: str) -> str:
        """Extract email address from text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(email_pattern, text)
        return matches[0] if matches else "Not found"
    
    def _extract_phone(self, text: str) -> str:
        """Extract phone number from text"""
        # Pattern for various phone formats
        phone_patterns = [
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # 123-456-7890 or 1234567890
            r'\b\(\d{3}\)\s*\d{3}[-.]?\d{4}\b',  # (123) 456-7890
            r'\b\+\d{1,3}[-.]?\d{3,4}[-.]?\d{3,4}[-.]?\d{4}\b'  # +1-123-456-7890
        ]
        
        for pattern in phone_patterns:
            matches = re.findall(pattern, text)
            if matches:
                return matches[0]
        return "Not found"
    
    def _extract_name(self, text: str) -> str:
        """
        Extract candidate name (usually first non-empty line or line with capitalized words)
        """
        lines = text.split('\n')
        
        # Strategy 1: Look for name in first 15 lines
        for line in lines[:15]:
            line = line.strip()
            # Remove common prefixes
            line = re.sub(r'^(resume|curriculum vitae|cv|name)\s*[-:]*\s*', '', line, flags=re.IGNORECASE)
            
            if 5 <= len(line) <= 50:
                words = line.split()
                # Check for 2-4 capitalized words (typical name format)
                if 2 <= len(words) <= 4:
                    # Exclude common keywords that aren't names
                    exclude_keywords = ['phone', 'email', 'address', 'linkedin', 'github', 
                                       'portfolio', 'objective', 'summary', 'experience', 
                                       'education', 'skills', 'contact', 'mobile']
                    
                    if not any(keyword in line.lower() for keyword in exclude_keywords):
                        # Check if words start with capital letters
                        if all(word[0].isupper() for word in words if word and word[0].isalpha()):
                            return line
        
        # Strategy 2: Look for "Name:" pattern
        name_match = re.search(r'(?:name|candidate)\s*:\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})', text, re.IGNORECASE)
        if name_match:
            return name_match.group(1).strip()
        
        return "Not found"
    
    def _extract_education(self, text: str) -> str:
        """Extract education information"""
        education_keywords = [
            'bachelor', 'master', 'phd', 'doctorate', 'mba', 'b.tech', 
            'm.tech', 'b.sc', 'm.sc', 'diploma', 'degree'
        ]
        
        text_lower = text.lower()
        found_education = []
        
        for keyword in education_keywords:
            if keyword in text_lower:
                # Find the line containing the keyword
                for line in text.split('\n'):
                    if keyword in line.lower() and len(line.strip()) > 5:
                        found_education.append(line.strip())
                        break
        
        return '; '.join(found_education[:3]) if found_education else "Not specified"
    
    def _estimate_experience(self, text: str) -> str:
        """Estimate years of experience from resume"""
        # Look for patterns like "5 years", "5+ years", "5-7 years"
        experience_patterns = [
            r'(\d+)\+?\s*years?\s+(?:of\s+)?experience',
            r'experience\s+(?:of\s+)?(\d+)\+?\s*years?',
            r'(\d+)\s*-\s*(\d+)\s*years?'
        ]
        
        text_lower = text.lower()
        
        for pattern in experience_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                if isinstance(matches[0], tuple):
                    return f"{matches[0][0]}-{matches[0][1]} years"
                else:
                    return f"{matches[0]} years"
        
        # Alternative: Count years mentioned (rough estimate)
        year_pattern = r'\b(19|20)\d{2}\b'
        years = re.findall(year_pattern, text)
        if len(years) >= 2:
            years_int = sorted([int(y) for y in years])
            experience = years_int[-1] - years_int[0]
            if 0 < experience < 50:
                return f"~{experience} years"
        
        return "Not specified"
    
    def _extract_education_detailed(self, text: str) -> list:
        """Extract detailed education information with improved multi-pattern parsing"""
        education_list = []
        seen_entries = set()
        
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Step 1: Find education section boundaries
        edu_start, edu_end = self._find_section_boundaries(lines, 
            start_patterns=[r'^education', r'^academic', r'^qualification'],
            end_patterns=[r'^experience', r'^employment', r'^work', r'^skills', r'^projects?', r'^certifications?'])
        
        # Search in education section if found, otherwise search entire document
        search_lines = lines[edu_start:edu_end] if edu_start >= 0 else lines
        
        # Step 2: Define comprehensive degree patterns with multiple variations
        degree_patterns = {
            'bachelor': [
                r'(?:Bachelor|B\.?\s*Tech|B\.?\s*E\.?|B\.?\s*Sc?\.?|B\.?\s*A\.?|B\.?\s*Com\.?)\s*(?:\(|\s+in\s+|\s+of\s+|\s*-\s*)?\s*([A-Za-z\s&,\(\)]+?)(?:\)|,|\s*\d{4}|\||$|from|at|\n)',
                r'(Bachelor\s+(?:of\s+)?(?:Science|Arts|Engineering|Technology|Commerce|Business))\s*(?:in\s+)?([A-Za-z\s&,]+?)(?:,|\s*\d{4}|\||$|from)',
            ],
            'master': [
                r'(?:Master|M\.?\s*Tech|M\.?\s*E\.?|M\.?\s*Sc?\.?|M\.?\s*A\.?|MBA|M\.?\s*Com\.?)\s*(?:\(|\s+in\s+|\s+of\s+|\s*-\s*)?\s*([A-Za-z\s&,\(\)]+?)(?:\)|,|\s*\d{4}|\||$|from|at|\n)',
                r'(Master\s+(?:of\s+)?(?:Science|Arts|Engineering|Technology|Business|Commerce))\s*(?:in\s+)?([A-Za-z\s&,]+?)(?:,|\s*\d{4}|\||$|from)',
            ],
            'phd': [
                r'(?:Ph\.?\s*D\.?|Doctorate|Doctor\s+of\s+Philosophy)\s*(?:in\s+)?([A-Za-z\s&,]+?)(?:,|\s*\d{4}|\||$|from)',
            ],
            'diploma': [
                r'((?:Post\s+Graduate\s+)?Diploma)\s*(?:in\s+)?([A-Za-z\s&,]+?)(?:,|\s*\d{4}|\||$|from)',
            ]
        }
        
        # Step 3: Parse each line for degree information
        i = 0
        while i < len(search_lines):
            line = search_lines[i]
            if len(line) < 5:
                i += 1
                continue
            
            # Try all degree patterns
            for degree_type, patterns in degree_patterns.items():
                for pattern in patterns:
                    match = re.search(pattern, line, re.IGNORECASE)
                    if match:
                        # Extract degree and field
                        if len(match.groups()) >= 2 and match.group(2):
                            degree_base = match.group(1).strip()
                            field = match.group(2).strip()
                        elif len(match.groups()) >= 1:
                            degree_base = match.group(0).split('in')[0].strip() if 'in' in match.group(0).lower() else match.group(0).strip()
                            field_match = re.search(r'\bin\s+([A-Za-z\s&,]+)', match.group(0), re.IGNORECASE)
                            field = field_match.group(1).strip() if field_match else match.group(1).strip()
                        else:
                            continue
                        
                        # Clean and format
                        field = re.sub(r'\s+', ' ', field).strip()
                        field = re.sub(r'[,\|\-]+$', '', field).strip()
                        
                        # Remove trailing junk
                        field = re.split(r'\s+(?:from|at|\d{4})', field)[0].strip()
                        
                        if len(field) > 60:
                            field = field[:60].rsplit(' ', 1)[0]
                        
                        # Build full degree name
                        if field and len(field) > 2 and field.lower() not in ['', 'in', 'from', 'at']:
                            full_degree = f"{degree_base} in {field}"
                        else:
                            full_degree = degree_base
                        
                        # Look for institution and dates in surrounding lines
                        institution, years = self._extract_institution_and_years(search_lines, i, window=4)
                        
                        # Create entry
                        edu_entry = {
                            "degree": full_degree,
                            "institution": institution,
                            "year": years,
                            "description": ""
                        }
                        
                        # Add if unique
                        entry_key = f"{full_degree.lower()}|{institution.lower()}"
                        if entry_key not in seen_entries and len(full_degree) > 3:
                            seen_entries.add(entry_key)
                            education_list.append(edu_entry)
                            break
            
            i += 1
        
        # Step 4: Fallback - look for education keywords if nothing found
        if not education_list:
            education_list = self._fallback_education_extraction(lines)
        
        # Return up to 5 entries
        return education_list[:5]
    
    def _find_section_boundaries(self, lines: list, start_patterns: list, end_patterns: list) -> tuple:
        """Find start and end indices of a section"""
        start_idx = -1
        end_idx = len(lines)
        
        for i, line in enumerate(lines):
            line_lower = line.lower().strip()
            
            # Check for section start
            if start_idx == -1:
                for pattern in start_patterns:
                    if re.match(pattern, line_lower):
                        start_idx = i + 1  # Start from next line
                        break
            
            # Check for section end
            elif start_idx >= 0:
                for pattern in end_patterns:
                    if re.match(pattern, line_lower):
                        end_idx = i
                        return start_idx, end_idx
        
        return start_idx, end_idx
    
    def _extract_institution_and_years(self, lines: list, current_idx: int, window: int = 4) -> tuple:
        """Extract institution name and year range from surrounding lines"""
        institution = "Not specified"
        years = "Not specified"
        years_found = []
        
        # Search in a window around current line
        start = max(0, current_idx - 1)
        end = min(len(lines), current_idx + window)
        
        for i in range(start, end):
            line = lines[i].strip()
            
            # Extract institution
            if institution == "Not specified":
                # Look for institution keywords
                inst_patterns = [
                    r'([A-Z][A-Za-z\s,\.&\'-]{3,}(?:University|College|Institute|School|Academy|Polytechnic)[A-Za-z\s,\.&\'-]*)',
                    r'((?:Indian\s+Institute|National\s+Institute|Massachusetts\s+Institute)[A-Za-z\s,\.&\'-]*)',
                    r'([A-Z][A-Z]+(?:\s+[A-Z][A-Z]+)*\s*(?:University|College|Institute))',  # Acronyms
                ]
                
                for pattern in inst_patterns:
                    match = re.search(pattern, line, re.IGNORECASE)
                    if match:
                        inst = match.group(1).strip()
                        inst = re.sub(r'\s+', ' ', inst)
                        # Clean up any trailing dates or separators
                        inst = re.sub(r'[,\|\-]\s*\d{4}.*$', '', inst).strip()
                        if len(inst) > 5 and len(inst) < 100:
                            institution = inst
                            break
            
            # Extract years
            year_matches = re.findall(r'\b(19[5-9]\d|20[0-2]\d)\b', line)
            years_found.extend(year_matches)
        
        # Process years
        if years_found:
            unique_years = sorted(set(years_found), key=int)
            if len(unique_years) == 1:
                years = unique_years[0]
            elif len(unique_years) >= 2:
                # Use first and last year as range
                years = f"{unique_years[0]} - {unique_years[-1]}"
        
        return institution, years
    
    def _fallback_education_extraction(self, lines: list) -> list:
        """Fallback method to extract education when pattern matching fails"""
        education_list = []
        education_keywords = [
            'bachelor', 'b.tech', 'b.e', 'b.sc', 'b.a', 'b.com', 'btech', 'bsc',
            'master', 'm.tech', 'm.e', 'm.sc', 'm.a', 'mba', 'm.com', 'mtech', 'msc',
            'phd', 'ph.d', 'doctorate', 'doctoral',
            'diploma', 'post graduate', 'graduate degree'
        ]
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Skip section headers
            if line_lower in ['education', 'academic', 'qualification', 'educational background', 'academics']:
                continue
            
            # Check if line contains education keyword
            if any(keyword in line_lower for keyword in education_keywords):
                if len(line) > 10 and len(line) < 150:
                    # Extract years if present
                    years = re.findall(r'\b(19[5-9]\d|20[0-2]\d)\b', line)
                    year_str = " - ".join(sorted(set(years))) if years else "Not specified"
                    
                    # Try to separate degree from institution
                    parts = re.split(r'\s*(?:from|at|-)\s*', line, maxsplit=1)
                    degree = parts[0].strip()
                    institution = parts[1].strip() if len(parts) > 1 else "Not specified"
                    
                    education_list.append({
                        "degree": degree[:100],
                        "institution": institution[:80] if institution != "Not specified" else "Not specified",
                        "year": year_str,
                        "description": ""
                    })
                    
                    if len(education_list) >= 3:
                        break
        
        return education_list
    
    def _extract_experience_detailed(self, text: str) -> list:
        """Extract detailed work experience with improved multi-format parsing"""
        experience_list = []
        seen_entries = set()
        
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Find experience section boundaries
        exp_start, exp_end = self._find_section_boundaries(lines,
            start_patterns=[r'^(?:work\s+)?experience', r'^employment', r'^professional\s+experience', r'^work\s+history', r'^career'],
            end_patterns=[r'^education', r'^skills', r'^certifications?', r'^projects?', r'^awards?', r'^training', r'^languages?', r'^interests?'])
        
        # Search in experience section if found, otherwise search from beginning
        search_lines = lines[exp_start:exp_end] if exp_start >= 0 else lines[:max(len(lines)//2, 50)]
        
        # Enhanced job title indicators and patterns
        job_keywords = [
            'engineer', 'developer', 'programmer', 'architect', 'designer',
            'manager', 'director', 'lead', 'head', 'chief',
            'analyst', 'scientist', 'researcher', 'specialist',
            'consultant', 'advisor', 'coordinator', 'administrator',
            'associate', 'assistant', 'executive', 'officer',
            'supervisor', 'technician', 'intern', 'trainee'
        ]
        
        # Comprehensive date patterns
        date_patterns = [
            r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}\s*[-–—]+\s*(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4})',
            r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}\s*[-–—]+\s*(?:Present|Current|Now|Ongoing))',
            r'(\d{1,2}/\d{4}\s*[-–—]+\s*\d{1,2}/\d{4})',
            r'(\d{1,2}/\d{4}\s*[-–—]+\s*(?:Present|Current|Now))',
            r'(\d{4}\s*[-–—]+\s*\d{4})',
            r'(\d{4}\s*[-–—]+\s*(?:Present|Current|Now|Ongoing))',
        ]
        
        # Parse experiences
        i = 0
        current_position = None
        
        while i < len(search_lines):
            line = search_lines[i]
            
            if len(line) < 5:
                i += 1
                continue
            
            line_lower = line.lower()
            
            # Skip obvious section headers
            if line_lower in ['experience', 'work experience', 'employment', 'professional experience', 'work history']:
                i += 1
                continue
            
            # Check for job title indicators
            is_likely_title = any(keyword in line_lower for keyword in job_keywords)
            
            # Check for date pattern
            date_match = None
            for pattern in date_patterns:
                date_match = re.search(pattern, line, re.IGNORECASE)
                if date_match:
                    break
            
            # Identify job title line
            if is_likely_title or date_match:
                # Save previous position
                if current_position and current_position.get('title'):
                    entry_key = f"{current_position['title']}|{current_position['company']}"
                    if entry_key not in seen_entries and len(current_position['title']) > 3:
                        seen_entries.add(entry_key)
                        experience_list.append(current_position)
                
                # Extract job title
                title = line
                duration = date_match.group(1) if date_match else ""
                
                # Remove date from title if present
                if duration:
                    title = title.replace(duration, '').strip()
                
                # Clean up title
                title = re.sub(r'\s+', ' ', title).strip()
                title = re.sub(r'[,\|\-]+$', '', title).strip()
                
                # Extract company and additional info from following lines
                company, duration, desc_lines = self._extract_job_details(search_lines, i + 1, duration, job_keywords)
                
                current_position = {
                    "title": title[:100],
                    "company": company,
                    "duration": duration,
                    "description": " ".join(desc_lines)[:300] if desc_lines else ""
                }
            
            i += 1
        
        # Add last position
        if current_position and current_position.get('title'):
            entry_key = f"{current_position['title']}|{current_position['company']}"
            if entry_key not in seen_entries and len(current_position['title']) > 3:
                experience_list.append(current_position)
        
        # Fallback: If no structured experience found, try to estimate
        if not experience_list:
            exp_years = self._estimate_experience(text)
            if exp_years != "Not specified":
                experience_list.append({
                    "title": "Experience mentioned in resume",
                    "company": "Various",
                    "duration": exp_years,
                    "description": "See resume for details"
                })
        
        return experience_list[:5]  # Return max 5 experiences
    
    def _extract_job_details(self, lines: list, start_idx: int, initial_duration: str, job_keywords: list) -> tuple:
        """Extract company, duration, and description from lines following a job title"""
        company = "Not specified"
        duration = initial_duration
        description_lines = []
        
        # Date patterns for duration search
        date_patterns = [
            r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}\s*[-–—]+\s*(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4})',
            r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}\s*[-–—]+\s*(?:Present|Current|Now|Ongoing))',
            r'(\d{4}\s*[-–—]+\s*\d{4})',
            r'(\d{4}\s*[-–—]+\s*(?:Present|Current|Now|Ongoing))',
        ]
        
        for j in range(start_idx, min(start_idx + 8, len(lines))):
            line = lines[j].strip()
            line_lower = line.lower()
            
            if not line or len(line) < 3:
                continue
            
            # Check if this is a new job title (stop collecting details)
            is_new_job = any(keyword in line_lower for keyword in job_keywords)
            if is_new_job and j > start_idx + 2 and len(line) > 15:
                # Likely a new position
                if re.match(r'^(senior|junior|lead|principal|staff|associate|assistant)', line_lower):
                    break
            
            # Extract company name
            if company == "Not specified":
                # Company indicators
                company_indicators = ['inc', 'llc', 'ltd', 'corp', 'company', 'corporation', 'technologies', 'solutions', 'systems', 'services']
                has_company_indicator = any(ind in line_lower for ind in company_indicators)
                
                # Check if line starts with capital letter and doesn't have job keywords
                if (re.match(r'^[A-Z]', line) or has_company_indicator) and not is_new_job:
                    # Clean up the company name
                    company_line = re.sub(r'\s*[-–—]\s*.*$', '', line).strip()  # Remove trailing info
                    if 3 < len(company_line) < 80:
                        company = company_line
                        continue
            
            # Extract duration if not found
            if not duration:
                for pattern in date_patterns:
                    match = re.search(pattern, line, re.IGNORECASE)
                    if match:
                        duration = match.group(1)
                        break
                if duration:
                    continue
            
            # Collect description (after company and duration are found)
            if company != "Not specified" or duration:
                # Valid description line criteria
                if len(line) > 15 and not re.match(r'^[\W\d]+$', line):
                    # Skip lines that look like section headers
                    if not re.match(r'^(education|skills|certifications?|projects?|awards?)', line_lower):
                        description_lines.append(line)
                        if len(description_lines) >= 3:
                            break
        
        # Set default duration if still not found
        if not duration:
            duration = "Not specified"
        
        return company, duration, description_lines
    
    def _extract_certifications(self, text: str) -> list:
        """Extract certifications from resume with improved parsing"""
        certifications = []
        seen_certs = set()
        
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Find certification section
        cert_start, cert_end = self._find_section_boundaries(lines,
            start_patterns=[r'^certifications?', r'^licenses?', r'^credentials?', r'^professional\s+certifications?'],
            end_patterns=[r'^education', r'^experience', r'^skills', r'^projects?', r'^awards?', r'^interests?'])
        
        # Comprehensive certification patterns
        cert_patterns = [
            # Cloud certifications
            r'(AWS\s+Certified\s+[A-Za-z\s\-]+(?:Associate|Professional|Specialty)?)',
            r'(Microsoft\s+Certified:\s*[A-Za-z\s\-]+)',
            r'(Google\s+Cloud\s+(?:Certified\s+)?[A-Za-z\s\-]+)',
            r'(Azure\s+(?:Certified\s+)?[A-Za-z\s\-]+)',
            # Professional certifications
            r'(PMP|PMI|PRINCE2)',
            r'(CISSP|CISM|CEH|OSCP|Security\+)',
            r'(CCNA|CCNP|CCIE)',
            r'(CKA|CKAD|CKS)',  # Kubernetes
            r'(CompTIA\s+\w+)',
            # Programming/Framework certifications
            r'(Oracle\s+Certified\s+[A-Za-z\s\-]+)',
            r'(Red\s+Hat\s+Certified\s+[A-Za-z\s\-]+)',
            r'(Salesforce\s+Certified\s+[A-Za-z\s\-]+)',
            # Scrum/Agile
            r'(Certified\s+Scrum\s+(?:Master|Product\s+Owner|Developer))',
            r'(SAFe\s+(?:Agilist|Practitioner))',
            # General certification pattern
            r'((?:Certified|Certificate)\s+[A-Za-z\s\-]{5,50})',
        ]
        
        # Search in certification section if found, otherwise entire document
        search_lines = lines[cert_start:cert_end] if cert_start >= 0 else lines
        
        for line in search_lines:
            line_lower = line.lower()
            
            # Skip section headers
            if line_lower in ['certifications', 'certification', 'licenses', 'credentials', 'professional certifications']:
                continue
            
            # Try all patterns
            for pattern in cert_patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    cert_name = match.group(1).strip()
                    
                    # Clean up
                    cert_name = re.sub(r'\s+', ' ', cert_name)
                    cert_name = re.sub(r'[,\|\-]+$', '', cert_name).strip()
                    
                    # Extract year if present in the line
                    year_match = re.search(r'\b(19[89]\d|20[0-2]\d)\b', line)
                    year = year_match.group(0) if year_match else None
                    
                    # Extract issuer from line if possible
                    issuer = "Not specified"
                    issuer_match = re.search(r'(?:by|from|issued\s+by)\s+([A-Z][A-Za-z\s&,\.]{3,40})', line, re.IGNORECASE)
                    if issuer_match:
                        issuer = issuer_match.group(1).strip()
                    
                    # Add if unique and valid
                    if cert_name and len(cert_name) > 3:
                        cert_key = cert_name.lower()
                        if cert_key not in seen_certs:
                            seen_certs.add(cert_key)
                            certifications.append({
                                "name": cert_name[:100],
                                "issuer": issuer[:50],
                                "year": year
                            })
        
        # Fallback: Look for lines with "certification" or "certified" anywhere
        if not certifications:
            for line in lines:
                if re.search(r'\bcertifi(?:ed|cate)\b', line, re.IGNORECASE) and len(line) > 10:
                    # Skip section headers
                    if line.lower().strip() in ['certifications', 'certification', 'licenses']:
                        continue
                    
                    year_match = re.search(r'\b(19[89]\d|20[0-2]\d)\b', line)
                    year = year_match.group(0) if year_match else None
                    
                    cert_key = line.lower()
                    if cert_key not in seen_certs:
                        seen_certs.add(cert_key)
                        certifications.append({
                            "name": line[:100],
                            "issuer": "Not specified",
                            "year": year
                        })
                        
                        if len(certifications) >= 5:
                            break
        
        return certifications[:10]  # Return max 10 certifications
    
    def _extract_skills_basic(self, text: str) -> list:
        """Extract basic technical skills"""
        skills = []
        
        # Common technical skills
        common_skills = [
            'python', 'java', 'javascript', 'typescript', 'c\\+\\+', 'c#', 'sql', 'html', 'css',
            'react', 'angular', 'vue', 'node.js', 'django', 'flask', 'spring', 'docker', 'kubernetes',
            'aws', 'azure', 'gcp', 'git', 'jenkins', 'mongodb', 'postgresql', 'mysql', 'redis',
            'machine learning', 'deep learning', 'tensorflow', 'pytorch', 'pandas', 'numpy',
            'agile', 'scrum', 'rest api', 'microservices', 'ci/cd', 'linux', 'bash'
        ]
        
        text_lower = text.lower()
        
        for skill in common_skills:
            pattern = r'\b' + skill.replace('+', '\\+').replace('.', '\\.') + r'\b'
            if re.search(pattern, text_lower, re.IGNORECASE):
                formatted_skill = skill.replace('\\+', '+').replace('\\.', '.').title()
                if formatted_skill not in skills:
                    skills.append(formatted_skill)
        
        return skills
