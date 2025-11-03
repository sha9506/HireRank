"""
HireRank Backend API
FastAPI server for resume ranking and analysis
"""

from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional
import uvicorn
import logging
from datetime import datetime

from models.resume_processor import ResumeProcessor
from models.nlp_analyzer import NLPAnalyzer
from models.database import Database
from models.gemini_analyzer import GeminiResumeAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="HireRank API",
    description="AI-powered resume ranking and talent screening platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
resume_processor = ResumeProcessor()
nlp_analyzer = NLPAnalyzer()
database = Database()
gemini_analyzer = GeminiResumeAnalyzer()


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting HireRank API...")
    await database.connect()
    logger.info("Database connected successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down HireRank API...")
    await database.disconnect()


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "HireRank API",
        "status": "running",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    db_status = await database.check_connection()
    return {
        "status": "healthy",
        "database": "connected" if db_status else "disconnected",
        "nlp_model": "loaded"
    }


@app.post("/rank_resume")
async def rank_resume(
    resume: UploadFile = File(...),
    job_description: str = Form(...),
    job_id: Optional[str] = Form(None)
):
    """
    Main endpoint for ranking resumes (legacy endpoint for backward compatibility)
    
    Args:
        resume: Uploaded resume file (PDF or DOCX)
        job_description: Text description of the job role
        job_id: Optional job identifier for tracking
    
    Returns:
        JSON with match_score, skills_extracted, and summary
    """
    try:
        # Validate file type
        allowed_extensions = ('.pdf', '.docx', '.doc', '.jpg', '.jpeg', '.png')
        if not resume.filename.lower().endswith(allowed_extensions):
            raise HTTPException(
                status_code=400,
                detail="Invalid file format. Please upload PDF, DOCX, or image (JPG, PNG) files only."
            )
        
        logger.info(f"Processing resume: {resume.filename}")
        
        # Read file content
        file_content = await resume.read()
        
        # Validate we have file content
        if not file_content:
            raise HTTPException(
                status_code=400,
                detail="Empty file received. Please upload a valid file."
            )
        
        # Extract text from resume
        logger.info("Extracting text from resume...")
        try:
            resume_text = resume_processor.extract_text(file_content, resume.filename)
        except ValueError as ve:
            raise HTTPException(
                status_code=400,
                detail=str(ve)
            )
        except RuntimeError as re:
            raise HTTPException(
                status_code=500,
                detail=str(re)
            )
        
        if not resume_text or len(resume_text.strip()) < 50:
            raise HTTPException(
                status_code=400,
                detail="Could not extract sufficient text from resume. Please check the file."
            )
        
        # Extract candidate information
        logger.info("Extracting candidate information...")
        candidate_info = resume_processor.extract_candidate_info(resume_text)
        
        # Extract skills from resume
        logger.info("Extracting skills...")
        skills_extracted = nlp_analyzer.extract_skills(resume_text)
        
        # Calculate semantic similarity
        logger.info("Calculating match score...")
        match_score = nlp_analyzer.calculate_similarity(resume_text, job_description)
        
        # Generate AI summary
        logger.info("Generating AI summary...")
        summary = nlp_analyzer.generate_summary(
            resume_text, 
            job_description, 
            match_score
        )
        
        # Prepare result
        result = {
            "match_score": round(match_score, 2),
            "skills_extracted": skills_extracted,
            "summary": summary,
            "candidate_info": candidate_info,
            "resume_filename": resume.filename,
            "processed_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Analysis completed successfully. Match score: {match_score}%")
        return JSONResponse(content=result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing resume: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing the resume: {str(e)}"
        )


@app.post("/analyze_resume")
async def analyze_resume(
    resume: UploadFile = File(...),
    job_title: str = Form(...),
    job_description: Optional[str] = Form(None)
):
    """
    Enhanced endpoint for analyzing resumes with job title-based matching
    
    Args:
        resume: Uploaded resume file (PDF or DOCX)
        job_title: Job title (e.g., "Data Scientist", "Software Engineer")
        job_description: Optional full job description for additional context
    
    Returns:
        JSON with candidate details, match_score, skills, and ranking info
    """
    try:
        logger.info(f"Received analyze_resume request - file: {resume.filename}, job_title: {job_title}")
        
        # Validate job title
        if not job_title or not job_title.strip():
            raise HTTPException(
                status_code=400,
                detail="Job title is required and cannot be empty."
            )
        
        # Validate file type
        allowed_extensions = ('.pdf', '.docx', '.doc', '.jpg', '.jpeg', '.png')
        if not resume.filename.lower().endswith(allowed_extensions):
            raise HTTPException(
                status_code=400,
                detail="Invalid file format. Please upload PDF, DOCX, or image (JPG, PNG) files only."
            )
        
        logger.info(f"Analyzing resume: {resume.filename} for job: {job_title}")
        
        # Read file content
        file_content = await resume.read()
        
        # Validate we have file content
        if not file_content:
            raise HTTPException(
                status_code=400,
                detail="Empty file received. Please upload a valid file."
            )
        
        # Extract text from resume
        logger.info("Extracting text from resume...")
        try:
            resume_text = resume_processor.extract_text(file_content, resume.filename)
        except ValueError as ve:
            raise HTTPException(
                status_code=400,
                detail=str(ve)
            )
        except RuntimeError as re:
            raise HTTPException(
                status_code=500,
                detail=str(re)
            )
        
        if not resume_text or len(resume_text.strip()) < 50:
            raise HTTPException(
                status_code=400,
                detail="Could not extract sufficient text from resume. Please check the file."
            )
        
        # Extract candidate name
        logger.info("Extracting candidate name...")
        candidate_name = nlp_analyzer.extract_candidate_name(resume_text)
        
        # Extract candidate information
        logger.info("Extracting candidate information...")
        candidate_info = resume_processor.extract_candidate_info(resume_text)
        
        # Get expected skills for job title
        logger.info(f"Getting skills for job title: {job_title}")
        expected_skills = nlp_analyzer.get_skills_for_job_title(job_title)
        
        # Extract skills from resume
        logger.info("Extracting skills from resume...")
        resume_skills = nlp_analyzer.extract_skills(resume_text)
        
        # Use job description if provided, otherwise use job title + expected skills
        job_context = job_description or f"{job_title}. Required skills: {', '.join(expected_skills)}"
        
        # Calculate semantic similarity
        logger.info("Calculating match score...")
        match_score = nlp_analyzer.calculate_similarity(resume_text, job_context)
        
        # Generate AI summary
        logger.info("Generating AI summary...")
        summary = nlp_analyzer.generate_summary(
            resume_text, 
            job_context, 
            match_score
        )
        
        # Calculate skills found and missing for better frontend display
        resume_skills_lower = [s.lower() for s in resume_skills]
        expected_skills_lower = [s.lower() for s in expected_skills]
        
        skills_found = [s for s in expected_skills if s.lower() in resume_skills_lower]
        skills_missing = [s for s in expected_skills if s.lower() not in resume_skills_lower]
        
        # 🧩 NEW: Role-based skill stack analysis
        logger.info("Performing role-based skill stack analysis...")
        skill_stack_analysis = nlp_analyzer.analyze_role_skills(resume_skills, job_title)
        skill_summary = nlp_analyzer.summarize_skill_match(resume_skills, job_title)
        is_role_match = nlp_analyzer.is_role_match(resume_skills, job_title)
        skill_coverage = nlp_analyzer.get_skill_coverage_percentage(resume_skills, job_title)
        
        # 🤖 NEW: Gemini AI Analysis with dynamic job role understanding
        gemini_analysis = None
        try:
            logger.info("Performing Gemini AI analysis with job context...")
            resume_json = {
                "name": candidate_name,
                "skills": resume_skills,
                "experience": candidate_info.get("experience", []),
                "education": candidate_info.get("education", []),
                "certifications": candidate_info.get("certifications", [])
            }
            # Pass job_title and job_description for intelligent analysis
            gemini_analysis = gemini_analyzer.analyze_resume_with_gemini(
                resume_json, 
                job_title=job_title,
                job_description=job_description
            )
            logger.info(f"Gemini AI analysis completed - Role: {gemini_analysis.get('matched_role')}")
        except Exception as e:
            logger.warning(f"Gemini AI analysis failed: {str(e)}")
            # Continue without Gemini analysis
        
        # Store in database
        logger.info("Storing results in database...")
        doc_id = await database.store_analysis(
            candidate_name=candidate_name,
            job_title=job_title,
            resume_filename=resume.filename,
            skills=resume_skills,
            match_score=round(match_score, 2),
            summary=summary,
            candidate_info=candidate_info,
            job_description=job_description,
            skills_found=skills_found,
            skills_missing=skills_missing,
            expected_skills=expected_skills
        )
        
        # Prepare result
        result = {
            "_id": doc_id,
            "candidate_name": candidate_name,
            "job_title": job_title,
            "match_score": round(match_score, 2),
            "skills": resume_skills,
            "skills_found": skills_found,
            "skills_missing": skills_missing,
            "expected_skills": expected_skills,
            "summary": summary,
            "candidate_info": candidate_info,
            "contact_info": {
                "email": candidate_info.get("email", "Not found"),
                "phone": candidate_info.get("phone", "Not found")
            },
            "education": candidate_info.get("education", []),
            "experience": candidate_info.get("experience", []),
            "certifications": candidate_info.get("certifications", []),
            "resume_filename": resume.filename,
            "uploaded_at": datetime.utcnow().isoformat(),
            # 🧩 NEW: Role-based skill stack data
            "skill_stack_analysis": skill_stack_analysis,
            "skill_summary": skill_summary,
            "is_role_match": is_role_match,
            "skill_coverage": skill_coverage,
            # 🤖 NEW: Gemini AI Analysis
            "gemini_analysis": gemini_analysis
        }
        
        logger.info(f"Analysis completed successfully. Match score: {match_score}%")
        return JSONResponse(content=result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing resume: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while analyzing the resume: {str(e)}"
        )


@app.get("/analyses/{job_id}")
async def get_analyses(job_id: str, limit: int = 10):
    """Get all analyses for a specific job"""
    try:
        analyses = await database.get_analyses_by_job(job_id, limit)
        return {"job_id": job_id, "count": len(analyses), "analyses": analyses}
    except Exception as e:
        logger.error(f"Error fetching analyses: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/top_candidates/{job_id}")
async def get_top_candidates(job_id: str, limit: int = 5):
    """Get top-ranked candidates for a job"""
    try:
        top_candidates = await database.get_top_candidates(job_id, limit)
        return {
            "job_id": job_id,
            "count": len(top_candidates),
            "top_candidates": top_candidates
        }
    except Exception as e:
        logger.error(f"Error fetching top candidates: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/analysis/{analysis_id}")
async def delete_analysis(analysis_id: str):
    """Delete a specific analysis"""
    try:
        success = await database.delete_analysis(analysis_id)
        if success:
            return {"message": "Analysis deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Analysis not found")
    except Exception as e:
        logger.error(f"Error deleting analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/rankings")
async def get_rankings(job_title: Optional[str] = None, limit: int = 100):
    """
    Get leaderboard/rankings of all candidates sorted by match score
    
    Args:
        job_title: Optional filter by specific job title
        limit: Maximum number of results (default 100)
    
    Returns:
        JSON with ranked list of candidates
    """
    try:
        rankings = await database.get_rankings(job_title, limit)
        return {
            "job_title": job_title or "All Positions",
            "count": len(rankings),
            "rankings": rankings
        }
    except Exception as e:
        logger.error(f"Error fetching rankings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/history")
async def get_history(limit: int = 100):
    """
    Get chronological history of all resume analyses
    
    Args:
        limit: Maximum number of results (default 100)
    
    Returns:
        JSON with chronologically sorted analyses
    """
    try:
        history = await database.get_history(limit)
        return {
            "count": len(history),
            "history": history
        }
    except Exception as e:
        logger.error(f"Error fetching history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/top_performers")
async def get_top_performers(limit: int = 3):
    """
    Get top performing candidates across all positions
    
    Args:
        limit: Number of top performers (default 3)
    
    Returns:
        JSON with top performers
    """
    try:
        performers = await database.get_top_performers(limit)
        return {
            "count": len(performers),
            "top_performers": performers
        }
    except Exception as e:
        logger.error(f"Error fetching top performers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/remarks/{candidate_id}")
async def update_remarks(candidate_id: str, remarks: str = Form(...)):
    """
    Update HR remarks for a candidate
    
    Args:
        candidate_id: Candidate document ID
        remarks: HR remarks/comments text
    
    Returns:
        Success message
    """
    try:
        success = await database.update_remarks(candidate_id, remarks)
        if success:
            return {"message": "Remarks updated successfully", "candidate_id": candidate_id}
        else:
            raise HTTPException(status_code=404, detail="Candidate not found")
    except Exception as e:
        logger.error(f"Error updating remarks: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/candidate/{candidate_id}")
async def delete_candidate(candidate_id: str):
    """
    Delete a candidate record
    
    Args:
        candidate_id: Candidate document ID
    
    Returns:
        Success message
    """
    try:
        success = await database.delete_candidate(candidate_id)
        if success:
            return {"message": "Candidate deleted successfully", "candidate_id": candidate_id}
        else:
            raise HTTPException(status_code=404, detail="Candidate not found")
    except Exception as e:
        logger.error(f"Error deleting candidate: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/candidate/{candidate_id}")
async def get_candidate(candidate_id: str):
    """
    Get detailed information about a specific candidate
    
    Args:
        candidate_id: Candidate document ID
    
    Returns:
        Candidate details
    """
    try:
        candidate = await database.get_candidate_by_id(candidate_id)
        if candidate:
            return candidate
        else:
            raise HTTPException(status_code=404, detail="Candidate not found")
    except Exception as e:
        logger.error(f"Error fetching candidate: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/statistics")
async def get_statistics(job_title: Optional[str] = None):
    """
    Get statistics for all analyses or filtered by job title
    
    Args:
        job_title: Optional job title filter
    
    Returns:
        Statistics including count, average score, etc.
    """
    try:
        stats = await database.get_statistics(job_title)
        return stats
    except Exception as e:
        logger.error(f"Error fetching statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
