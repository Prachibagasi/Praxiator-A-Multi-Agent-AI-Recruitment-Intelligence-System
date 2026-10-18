from typing import Dict, List, Any, Tuple
from utils.embeddings import EmbeddingUtil
import sys
import os

# Add parent directory to path to ensure imports work correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class MatcherAgent:
    """Agent to match job descriptions with resumes using embeddings"""
    
    def __init__(self):
        """Initialize Matcher Agent"""
        self.embedding_util = EmbeddingUtil()
    
    def calculate_match_score(self, jd_data: Dict[str, Any], cv_data: Dict[str, Any]) -> float:
        """Calculate match score between job description and resume
        
        Args:
            jd_data: Job description data
            cv_data: Resume data
            
        Returns:
            Match score (0-100)
        """
        # Get embeddings
        jd_embedding = self.embedding_util.get_jd_embedding(jd_data)
        cv_embedding = self.embedding_util.get_cv_embedding(cv_data)
        
        # Calculate similarity
        score = self.embedding_util.calculate_similarity(jd_embedding, cv_embedding)
        
        return score
    
    def match_jd_with_all_cvs(self, jd_data: Dict[str, Any], cv_data_list: List[Dict[str, Any]]) -> List[Tuple[Dict[str, Any], float]]:
        """Match a job description with all resumes
        
        Args:
            jd_data: Job description data
            cv_data_list: List of resume data
            
        Returns:
            List of tuples containing CV data and match score, sorted by score
        """
        matches = []
        
        for cv_data in cv_data_list:
            score = self.calculate_match_score(jd_data, cv_data)
            matches.append((cv_data, score))
        
        # Sort by score in descending order
        matches.sort(key=lambda x: x[1], reverse=True)
        
        return matches
    
    def match_all_jds_with_all_cvs(self, jd_data_list: List[Dict[str, Any]], cv_data_list: List[Dict[str, Any]]) -> Dict[str, List[Tuple[Dict[str, Any], float]]]:
        """Match all job descriptions with all resumes
        
        Args:
            jd_data_list: List of job description data
            cv_data_list: List of resume data
            
        Returns:
            Dictionary mapping job title to list of (CV, score) tuples
        """
        all_matches = {}
        
        for jd_data in jd_data_list:
            job_title = jd_data['title']
            print(f"Matching: {job_title}")
            
            matches = self.match_jd_with_all_cvs(jd_data, cv_data_list)
            all_matches[job_title] = matches
        
        return all_matches
    
    def get_top_matches(self, all_matches: Dict[str, List[Tuple[Dict[str, Any], float]]], threshold: float = 0.0, top_n: int = None) -> Dict[str, List[Tuple[Dict[str, Any], float]]]:
        """Get top matches for each job description
        
        Args:
            all_matches: Dictionary mapping job title to list of (CV, score) tuples
            threshold: Minimum score threshold
            top_n: Maximum number of top matches to return
            
        Returns:
            Dictionary mapping job title to filtered list of (CV, score) tuples
        """
        filtered_matches = {}
        
        for job_title, matches in all_matches.items():
            # Filter by threshold
            threshold_matches = [(cv, score) for cv, score in matches if score >= threshold]
            
            # Limit to top N
            if top_n is not None:
                threshold_matches = threshold_matches[:top_n]
            
            filtered_matches[job_title] = threshold_matches
        
        return filtered_matches 