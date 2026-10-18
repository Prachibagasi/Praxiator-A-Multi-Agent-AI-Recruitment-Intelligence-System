import os
import re
import fitz  # PyMuPDF
from typing import Dict, List, Any, Optional

class CVExtractorAgent:
    """Agent to extract structured data from PDF resumes"""
    
    def __init__(self, resumes_dir: str = "resumes"):
        """Initialize CV Extractor Agent
        
        Args:
            resumes_dir: Directory containing resume PDFs
        """
        self.resumes_dir = resumes_dir
    
    def get_resume_files(self) -> List[str]:
        """Get list of PDF files in the resumes directory
        
        Returns:
            List of PDF filenames
        """
        resume_files = []
        try:
            for file in os.listdir(self.resumes_dir):
                if file.lower().endswith('.pdf'):
                    resume_files.append(file)
        except Exception as e:
            print(f"Error listing resume files: {str(e)}")
        
        return resume_files
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text content from PDF
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text from the PDF
        """
        text = ""
        try:
            doc = fitz.open(pdf_path)
            for page in doc:
                text += page.get_text()
            doc.close()
        except Exception as e:
            print(f"Error extracting text from PDF {pdf_path}: {str(e)}")
        
        return text
    
    def parse_resume(self, resume_text: str) -> Dict[str, Any]:
        """Parse resume text into structured data
        
        Args:
            resume_text: Text content of the resume
            
        Returns:
            Dictionary with structured data extracted from resume
        """
        # Extract name (usually at the beginning of the resume)
        name_match = re.search(r'^([A-Z][a-z]+(?: [A-Z][a-z]+)+)', resume_text)
        name = name_match.group(1) if name_match else "Unknown"
        
        # Extract email
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', resume_text)
        email = email_match.group(0) if email_match else ""
        
        # Extract phone number
        phone_pattern = r'(?:\+\d{1,3}[-.\s]?)?(?:\d{3}[-.\s]?)?\d{3}[-.\s]?\d{4}'
        phone_match = re.search(phone_pattern, resume_text)
        phone = phone_match.group(0) if phone_match else ""
        
        # Extract education
        education_section = self._extract_section(resume_text, 
            ['education', 'academic background', 'academic qualification'], 
            ['experience', 'skills', 'projects'])
        
        # Extract work experience
        experience_section = self._extract_section(resume_text, 
            ['experience', 'work history', 'professional experience', 'employment'], 
            ['education', 'skills', 'projects', 'certification'])
        
        # Extract skills
        skills_section = self._extract_section(resume_text, 
            ['skills', 'technical skills', 'core competencies'], 
            ['experience', 'education', 'projects', 'certification'])
        
        # Parse individual skills
        skills = self._extract_skills(skills_section)
        
        # Extract certifications
        cert_section = self._extract_section(resume_text, 
            ['certifications', 'certificates', 'professional certifications'], 
            ['experience', 'education', 'skills', 'projects'])
        
        # Parse individual certifications
        certifications = self._extract_certifications(cert_section)
        
        # Extract tech stack
        tech_stack = self._extract_tech_stack(resume_text)
        
        return {
            'name': name,
            'email': email,
            'phone': phone,
            'education': education_section,
            'work_experience': experience_section,
            'skills': ", ".join(skills) if skills else "",
            'certifications': ", ".join(certifications) if certifications else "",
            'tech_stack': ", ".join(tech_stack) if tech_stack else "",
            'raw_text': resume_text
        }
    
    def _extract_section(self, text: str, section_headers: List[str], next_section_headers: List[str]) -> str:
        """Extract text for a specific section from resume
        
        Args:
            text: Full resume text
            section_headers: Possible headers for the target section
            next_section_headers: Possible headers for the next sections
            
        Returns:
            Extracted section text
        """
        # Create regex patterns
        section_pattern = '|'.join([rf'(?:{header})' for header in section_headers])
        next_section_pattern = '|'.join([rf'(?:{header})' for header in next_section_headers])
        
        # Try to find section with various formatting
        for pattern in [
            rf'(?i)({section_pattern})[:\s]*\n+(.*?)(?:\n+(?:{next_section_pattern})[:\s]*|$)',
            rf'(?i)({section_pattern})[:\s]*(.*?)(?:(?:{next_section_pattern})[:\s]*|$)'
        ]:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                return match.group(2).strip()
        
        return ""
    
    def _extract_skills(self, skills_section: str) -> List[str]:
        """Extract individual skills from skills section
        
        Args:
            skills_section: Text from the skills section
            
        Returns:
            List of skills
        """
        if not skills_section:
            return []
        
        # Try different patterns to extract skills
        # Look for lists (comma-separated, bullet points, etc.)
        skills = []
        
        # Try comma-separated list
        if ',' in skills_section:
            skills = [s.strip() for s in skills_section.split(',') if s.strip()]
        
        # Try bullet points or line-by-line
        if not skills:
            bullet_skills = re.findall(r'(?:•|\*|\-|\d+\.)\s*([^•\*\-\n]+)', skills_section)
            if bullet_skills:
                skills = [s.strip() for s in bullet_skills if s.strip()]
        
        # Try line by line if still no skills found
        if not skills:
            line_skills = [line.strip() for line in skills_section.split('\n') if line.strip()]
            skills = line_skills
        
        return skills
    
    def _extract_certifications(self, cert_section: str) -> List[str]:
        """Extract individual certifications from certification section
        
        Args:
            cert_section: Text from the certifications section
            
        Returns:
            List of certifications
        """
        if not cert_section:
            return []
        
        # Similar approach as skills extraction
        certs = []
        
        # Try comma-separated list
        if ',' in cert_section:
            certs = [c.strip() for c in cert_section.split(',') if c.strip()]
        
        # Try bullet points
        if not certs:
            bullet_certs = re.findall(r'(?:•|\*|\-|\d+\.)\s*([^•\*\-\n]+)', cert_section)
            if bullet_certs:
                certs = [c.strip() for c in bullet_certs if c.strip()]
        
        # Try line by line if still no certs found
        if not certs:
            line_certs = [line.strip() for line in cert_section.split('\n') if line.strip()]
            certs = line_certs
            
        return certs
    
    def _extract_tech_stack(self, text: str) -> List[str]:
        """Extract tech stack from resume text
        
        Args:
            text: Full resume text
            
        Returns:
            List of technologies
        """
        # Common programming languages and technologies
        tech_keywords = [
            # Programming languages
            'Python', 'Java', 'JavaScript', 'C\\+\\+', 'C#', 'Ruby', 'PHP', 'Go', 'Swift', 'Kotlin',
            'TypeScript', 'Scala', 'Rust', 'Perl', 'R', 'MATLAB',
            
            # Web technologies
            'HTML', 'CSS', 'React', 'Angular', 'Vue', 'Node\\.js', 'Express', 'Django', 'Flask',
            'Spring', 'Laravel', 'Ruby on Rails', 'jQuery', 'Bootstrap', 'Tailwind',
            
            # Databases
            'SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'Oracle', 'SQLite', 'Redis', 'Cassandra',
            'DynamoDB', 'Elasticsearch', 'Firebase',
            
            # Cloud platforms
            'AWS', 'Azure', 'GCP', 'Google Cloud', 'Heroku', 'Netlify', 'Vercel',
            
            # DevOps
            'Docker', 'Kubernetes', 'Jenkins', 'Git', 'GitHub', 'GitLab', 'Terraform', 'Ansible',
            'CI/CD', 'Continuous Integration', 'Continuous Deployment',
            
            # AI/ML
            'TensorFlow', 'PyTorch', 'Keras', 'scikit-learn', 'Pandas', 'NumPy', 'SciPy',
            'Machine Learning', 'Deep Learning', 'NLP', 'Computer Vision'
        ]
        
        tech_pattern = '|'.join([rf'\b{tech}\b' for tech in tech_keywords])
        tech_matches = re.findall(tech_pattern, text, re.IGNORECASE)
        
        # Deduplicate and normalize
        tech_stack = list(set([match.strip() for match in tech_matches]))
        
        return tech_stack
    
    def process_resume(self, filename: str) -> Dict[str, Any]:
        """Process a single resume file
        
        Args:
            filename: Name of the resume PDF file
            
        Returns:
            Dictionary with structured data extracted from the resume
        """
        pdf_path = os.path.join(self.resumes_dir, filename)
        
        try:
            print(f"Processing resume: {filename}")
            text = self.extract_text_from_pdf(pdf_path)
            parsed_data = self.parse_resume(text)
            parsed_data['filename'] = filename
            return parsed_data
        except Exception as e:
            print(f"Error processing resume {filename}: {str(e)}")
            return {
                'filename': filename,
                'name': 'Error',
                'email': '',
                'phone': '',
                'education': '',
                'work_experience': '',
                'skills': '',
                'certifications': '',
                'tech_stack': '',
                'raw_text': ''
            }
    
    def process_all_resumes(self) -> List[Dict[str, Any]]:
        """Process all resume files in the directory
        
        Returns:
            List of dictionaries with parsed resume data
        """
        resume_files = self.get_resume_files()
        parsed_resumes = []
        
        for filename in resume_files:
            parsed_resume = self.process_resume(filename)
            parsed_resumes.append(parsed_resume)
        
        return parsed_resumes 