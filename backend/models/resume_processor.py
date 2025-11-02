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
            "education": self._extract_education(resume_text),
            "experience_years": self._estimate_experience(resume_text)
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
        for line in lines[:10]:  # Check first 10 lines
            line = line.strip()
            if len(line) > 2 and len(line) < 50:
                # Check if line has mostly capital letters (likely a name)
                words = line.split()
                if len(words) >= 2 and len(words) <= 4:
                    if all(word[0].isupper() for word in words if word):
                        return line
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
