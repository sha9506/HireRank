"""
MongoDB database connection and operations module
"""

import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from bson.objectid import ObjectId

logger = logging.getLogger(__name__)


class Database:
    """Handles MongoDB operations for HireRank"""
    
    def __init__(self):
        """Initialize database connection parameters"""
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None
        self.resumes_collection = None
        self.rankings_collection = None
        
        # Get MongoDB connection details from environment variables
        self.mongo_uri = os.getenv(
            "MONGODB_URI",
            "mongodb://localhost:27017/"
        )
        self.db_name = os.getenv("MONGODB_DATABASE", "hirerank")
    
    async def connect(self):
        """Establish connection to MongoDB"""
        try:
            logger.info(f"Connecting to MongoDB at {self.mongo_uri}")
            self.client = AsyncIOMotorClient(self.mongo_uri)
            self.db = self.client[self.db_name]
            self.resumes_collection = self.db["resumes"]
            self.rankings_collection = self.db["rankings"]
            
            # Create indexes for better query performance
            await self.resumes_collection.create_index([("candidate_name", 1)])
            await self.resumes_collection.create_index([("uploaded_at", -1)])
            await self.rankings_collection.create_index([("job_title", 1)])
            await self.rankings_collection.create_index([("match_score", -1)])
            await self.rankings_collection.create_index([("uploaded_at", -1)])
            
            logger.info("MongoDB connected successfully")
        except Exception as e:
            logger.error(f"Error connecting to MongoDB: {e}")
            raise
    
    async def disconnect(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")
    
    async def check_connection(self) -> bool:
        """Check if database connection is active"""
        try:
            if self.client:
                await self.client.admin.command('ping')
                return True
        except Exception as e:
            logger.error(f"Database connection check failed: {e}")
        return False
    
    async def store_analysis(
        self,
        candidate_name: str,
        job_title: str,
        resume_filename: str,
        skills: List[str],
        match_score: float,
        summary: str,
        candidate_info: Dict[str, Any],
        job_description: Optional[str] = None
    ) -> str:
        """
        Store resume analysis results in rankings collection
        
        Args:
            candidate_name: Extracted candidate name
            job_title: Job title being applied for
            resume_filename: Name of the resume file
            skills: List of extracted skills
            match_score: Calculated match score
            summary: AI-generated summary
            candidate_info: Dictionary containing candidate information
            job_description: Optional full job description
        
        Returns:
            Document ID of stored analysis
        """
        try:
            document = {
                "candidate_name": candidate_name,
                "job_title": job_title,
                "resume_filename": resume_filename,
                "skills": skills,
                "match_score": match_score,
                "summary": summary,
                "candidate_info": candidate_info,
                "job_description": job_description or "",
                "remarks": "",
                "uploaded_at": datetime.utcnow()
            }
            
            result = await self.rankings_collection.insert_one(document)
            logger.info(f"Analysis stored with ID: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error storing analysis: {e}")
            raise
    
    async def get_analyses_by_job(self, job_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve all analyses for a specific job (legacy method for backward compatibility)
        
        Args:
            job_id: Job identifier
            limit: Maximum number of results to return
        
        Returns:
            List of analysis documents
        """
        try:
            cursor = self.rankings_collection.find(
                {"job_title": job_id}
            ).sort("uploaded_at", -1).limit(limit)
            
            analyses = []
            async for doc in cursor:
                doc["_id"] = str(doc["_id"])
                analyses.append(doc)
            
            return analyses
            
        except Exception as e:
            logger.error(f"Error fetching analyses: {e}")
            raise
    
    async def get_rankings(self, job_title: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get ranked candidates sorted by match score
        
        Args:
            job_title: Optional filter by job title
            limit: Maximum number of results to return
        
        Returns:
            List of ranked candidate documents
        """
        try:
            filter_query = {"job_title": job_title} if job_title else {}
            cursor = self.rankings_collection.find(filter_query).sort("match_score", -1).limit(limit)
            
            rankings = []
            async for doc in cursor:
                doc["_id"] = str(doc["_id"])
                rankings.append(doc)
            
            return rankings
            
        except Exception as e:
            logger.error(f"Error fetching rankings: {e}")
            raise
    
    async def get_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get chronological history of all resume analyses
        
        Args:
            limit: Maximum number of results to return
        
        Returns:
            List of analysis documents sorted by date
        """
        try:
            cursor = self.rankings_collection.find({}).sort("uploaded_at", -1).limit(limit)
            
            history = []
            async for doc in cursor:
                doc["_id"] = str(doc["_id"])
                history.append(doc)
            
            return history
            
        except Exception as e:
            logger.error(f"Error fetching history: {e}")
            raise
    
    async def get_top_candidates(self, job_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get top-ranked candidates for a job (legacy method)
        
        Args:
            job_id: Job identifier
            limit: Number of top candidates to return
        
        Returns:
            List of top candidate documents
        """
        try:
            cursor = self.rankings_collection.find(
                {"job_title": job_id}
            ).sort("match_score", -1).limit(limit)
            
            candidates = []
            async for doc in cursor:
                doc["_id"] = str(doc["_id"])
                candidates.append(doc)
            
            return candidates
            
        except Exception as e:
            logger.error(f"Error fetching top candidates: {e}")
            raise
    
    async def get_top_performers(self, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Get overall top performers across all positions
        
        Args:
            limit: Number of top performers to return (default 3)
        
        Returns:
            List of top performer documents
        """
        try:
            cursor = self.rankings_collection.find({}).sort("match_score", -1).limit(limit)
            
            performers = []
            async for doc in cursor:
                doc["_id"] = str(doc["_id"])
                performers.append(doc)
            
            return performers
            
        except Exception as e:
            logger.error(f"Error fetching top performers: {e}")
            raise
    
    async def update_feedback(self, analysis_id: str, feedback: str) -> bool:
        """
        Update feedback notes for an analysis (legacy method)
        
        Args:
            analysis_id: Analysis document ID
            feedback: Feedback text
        
        Returns:
            True if update successful
        """
        try:
            result = await self.rankings_collection.update_one(
                {"_id": ObjectId(analysis_id)},
                {"$set": {"remarks": feedback}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating feedback: {e}")
            return False
    
    async def update_remarks(self, candidate_id: str, remarks: str) -> bool:
        """
        Update HR remarks for a candidate
        
        Args:
            candidate_id: Candidate document ID
            remarks: HR remarks text
        
        Returns:
            True if update successful
        """
        try:
            result = await self.rankings_collection.update_one(
                {"_id": ObjectId(candidate_id)},
                {"$set": {"remarks": remarks, "updated_at": datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating remarks: {e}")
            return False
    
    async def delete_analysis(self, analysis_id: str) -> bool:
        """
        Delete an analysis document
        
        Args:
            analysis_id: Analysis document ID
        
        Returns:
            True if deletion successful
        """
        try:
            result = await self.rankings_collection.delete_one(
                {"_id": ObjectId(analysis_id)}
            )
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting analysis: {e}")
            return False
    
    async def delete_candidate(self, candidate_id: str) -> bool:
        """
        Delete a candidate record
        
        Args:
            candidate_id: Candidate document ID
        
        Returns:
            True if deletion successful
        """
        try:
            result = await self.rankings_collection.delete_one(
                {"_id": ObjectId(candidate_id)}
            )
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting candidate: {e}")
            return False
    
    async def get_statistics(self, job_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get statistics for analyses
        
        Args:
            job_id: Optional job ID to filter statistics (maps to job_title)
        
        Returns:
            Dictionary containing statistics
        """
        try:
            match_filter = {"job_title": job_id} if job_id else {}
            
            total_count = await self.rankings_collection.count_documents(match_filter)
            
            pipeline = [
                {"$match": match_filter},
                {
                    "$group": {
                        "_id": None,
                        "avg_score": {"$avg": "$match_score"},
                        "max_score": {"$max": "$match_score"},
                        "min_score": {"$min": "$match_score"}
                    }
                }
            ]
            
            cursor = self.rankings_collection.aggregate(pipeline)
            stats = await cursor.to_list(length=1)
            
            result = {
                "total_analyses": total_count,
                "average_score": round(stats[0]["avg_score"], 2) if stats else 0,
                "highest_score": stats[0]["max_score"] if stats else 0,
                "lowest_score": stats[0]["min_score"] if stats else 0
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            raise
    
    async def get_candidate_by_id(self, candidate_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a single candidate by ID
        
        Args:
            candidate_id: Candidate document ID
        
        Returns:
            Candidate document or None if not found
        """
        try:
            doc = await self.rankings_collection.find_one({"_id": ObjectId(candidate_id)})
            if doc:
                doc["_id"] = str(doc["_id"])
            return doc
        except Exception as e:
            logger.error(f"Error fetching candidate: {e}")
            return None

