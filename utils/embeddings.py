import numpy as np
import ollama
from typing import List, Dict, Any, Union
from sklearn.metrics.pairwise import cosine_similarity

class EmbeddingUtil:
    """Utility for creating embeddings using Ollama"""
    
    def __init__(self, model: str = "nomic-embed-text"):
        """Initialize embedding utility
        
        Args:
            model: Ollama model to use for embeddings
        """
        self.model = model
    
    def get_embedding(self, text: str) -> List[float]:
        """Get embedding for text using Ollama
        
        Args:
            text: Text to embed
            
        Returns:
            List of embedding values
        """
        try:
            # Call Ollama API to get embedding
            response = ollama.embeddings(model=self.model, prompt=text)
            
            # Extract embedding from response
            if response and 'embedding' in response:
                return response['embedding']
            else:
                raise ValueError("No embedding in Ollama response")
                
        except Exception as e:
            print(f"Error getting embedding: {str(e)}")
            # Return a zero vector as fallback
            return [0.0] * 768  # Nomic model typically uses 768-dimensional embeddings
    
    def _format_jd_text(self, jd_data: Dict[str, Any]) -> str:
        """Format JD data as text for embedding
        
        Args:
            jd_data: JD data dictionary
            
        Returns:
            Formatted text
        """
        title = jd_data.get('title', '')
        skills = jd_data.get('summary', {}).get('required_skills', [])
        if isinstance(skills, list):
            skills_text = ", ".join(skills)
        else:
            skills_text = skills
            
        education = jd_data.get('summary', {}).get('education', '')
        experience = jd_data.get('summary', {}).get('years_of_experience', '')
        certifications = jd_data.get('summary', {}).get('certifications', [])
        if isinstance(certifications, list):
            certifications_text = ", ".join(certifications)
        else:
            certifications_text = certifications
            
        responsibilities = jd_data.get('summary', {}).get('responsibilities', [])
        if isinstance(responsibilities, list):
            responsibilities_text = ". ".join(responsibilities)
        else:
            responsibilities_text = responsibilities
        
        # Combine all sections
        text = f"""
        Job Title: {title}
        Required Skills: {skills_text}
        Education: {education}
        Experience: {experience}
        Certifications: {certifications_text}
        Responsibilities: {responsibilities_text}
        """
        
        return text.strip()
    
    def _format_cv_text(self, cv_data: Dict[str, Any]) -> str:
        """Format CV data as text for embedding
        
        Args:
            cv_data: CV data dictionary
            
        Returns:
            Formatted text
        """
        name = cv_data.get('name', '')
        education = cv_data.get('education', '')
        experience = cv_data.get('work_experience', '')
        skills = cv_data.get('skills', '')
        certifications = cv_data.get('certifications', '')
        tech_stack = cv_data.get('tech_stack', '')
        
        # Combine all sections
        text = f"""
        Name: {name}
        Education: {education}
        Experience: {experience}
        Skills: {skills}
        Certifications: {certifications}
        Technologies: {tech_stack}
        """
        
        return text.strip()
    
    def get_jd_embedding(self, jd_data: Dict[str, Any]) -> List[float]:
        """Get embedding for job description data
        
        Args:
            jd_data: JD data dictionary
            
        Returns:
            Embedding for JD
        """
        text = self._format_jd_text(jd_data)
        return self.get_embedding(text)
    
    def get_cv_embedding(self, cv_data: Dict[str, Any]) -> List[float]:
        """Get embedding for CV data
        
        Args:
            cv_data: CV data dictionary
            
        Returns:
            Embedding for CV
        """
        text = self._format_cv_text(cv_data)
        return self.get_embedding(text)
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding
            embedding2: Second embedding
            
        Returns:
            Similarity score (0-1)
        """
        # Convert to numpy arrays
        emb1 = np.array(embedding1).reshape(1, -1)
        emb2 = np.array(embedding2).reshape(1, -1)
        
        # Calculate cosine similarity
        similarity = cosine_similarity(emb1, emb2)[0][0]
        
        # Return as percentage (0-100)
        return float(similarity * 100) 