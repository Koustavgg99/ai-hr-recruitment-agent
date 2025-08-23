"""
HR Automation - Candidate Shortlisting System
Processes connections.csv and matches candidates against job descriptions
"""

import csv
import json
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import logging
try:
    from database_manager import CandidateDatabase
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False
    logging.warning("Database manager not available. Running without database integration.")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Candidate:
    """Data structure for candidate information"""
    first_name: str
    last_name: str
    full_name: str
    linkedin_url: str
    email: str
    company: str
    position: str
    connected_on: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class JobDescription:
    """Data structure for job description"""
    title: str
    company: str
    description: str
    required_skills: List[str]
    preferred_skills: List[str]
    
class CandidateProcessor:
    """Processes candidate data from CSV file"""
    
    def __init__(self, csv_file_path: str):
        self.csv_file_path = csv_file_path
        self.candidates: List[Candidate] = []
        
    def load_candidates(self) -> List[Candidate]:
        """Load candidates from CSV file"""
        candidates = []
        
        try:
            with open(self.csv_file_path, 'r', encoding='utf-8', errors='ignore') as file:
                # Skip the first line if it contains headers
                lines = file.readlines()
                
                for line_num, line in enumerate(lines[1:], 2):  # Skip header line
                    try:
                        # Remove the line number prefix and split by comma
                        if '|' in line:
                            parts = line.strip().split('|', 1)
                            if len(parts) > 1:
                                data = parts[1].split(',')
                            else:
                                continue
                        else:
                            data = line.strip().split(',')
                        
                        # Skip if not enough data
                        if len(data) < 7:
                            continue
                            
                        first_name = data[0].strip()
                        last_name = data[1].strip()
                        linkedin_url = data[2].strip()
                        email = data[3].strip() if len(data) > 3 else ""
                        company = data[4].strip() if len(data) > 4 else ""
                        position = data[5].strip() if len(data) > 5 else ""
                        connected_on = data[6].strip() if len(data) > 6 else ""
                        
                        # Skip empty entries
                        if not first_name or not linkedin_url:
                            continue
                            
                        full_name = f"{first_name} {last_name}".strip()
                        
                        candidate = Candidate(
                            first_name=first_name,
                            last_name=last_name,
                            full_name=full_name,
                            linkedin_url=linkedin_url,
                            email=email,
                            company=company,
                            position=position,
                            connected_on=connected_on
                        )
                        
                        candidates.append(candidate)
                        
                    except Exception as e:
                        logger.warning(f"Error processing line {line_num}: {e}")
                        continue
                        
        except FileNotFoundError:
            logger.error(f"CSV file not found: {self.csv_file_path}")
            raise
        except Exception as e:
            logger.error(f"Error reading CSV file: {e}")
            raise
            
        self.candidates = candidates
        logger.info(f"Loaded {len(candidates)} candidates from CSV")
        return candidates

class JobDescriptionProcessor:
    """Processes job descriptions for matching"""
    
    def __init__(self, job_descriptions_path: str):
        self.job_descriptions_path = job_descriptions_path
        self.job_descriptions: List[JobDescription] = []
        
    def load_job_descriptions(self) -> List[JobDescription]:
        """Load job descriptions from JSON file"""
        try:
            with open(self.job_descriptions_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                
            job_descriptions = []
            for job_data in data.get('job_descriptions', []):
                # Extract skills from description
                description = job_data['description']
                required_skills, preferred_skills = self._extract_skills(description)
                
                job_desc = JobDescription(
                    title=job_data['title'],
                    company=job_data['company'],
                    description=description,
                    required_skills=required_skills,
                    preferred_skills=preferred_skills
                )
                job_descriptions.append(job_desc)
                
            self.job_descriptions = job_descriptions
            logger.info(f"Loaded {len(job_descriptions)} job descriptions")
            return job_descriptions
            
        except FileNotFoundError:
            logger.error(f"Job descriptions file not found: {self.job_descriptions_path}")
            raise
        except Exception as e:
            logger.error(f"Error loading job descriptions: {e}")
            raise
    
    def _extract_skills(self, description: str) -> tuple[List[str], List[str]]:
        """Extract required and preferred skills from job description"""
        # Convert to lowercase for processing
        desc_lower = description.lower()
        
        # Common technical skills patterns
        technical_skills = [
            'python', 'java', 'javascript', 'react', 'angular', 'vue', 'node.js', 'django',
            'flask', 'spring', 'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'terraform',
            'jenkins', 'git', 'sql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
            'machine learning', 'ai', 'data science', 'tensorflow', 'pytorch', 'scikit-learn',
            'html', 'css', 'typescript', 'go', 'rust', 'c++', 'c#', '.net', 'php',
            'devops', 'ci/cd', 'microservices', 'restful api', 'graphql', 'agile', 'scrum'
        ]
        
        required_skills = []
        preferred_skills = []
        
        # Find skills in required section
        required_section = re.search(r'required.*?:(.*?)(?:preferred|bonus|location|salary|$)', desc_lower, re.DOTALL | re.IGNORECASE)
        if required_section:
            required_text = required_section.group(1)
            for skill in technical_skills:
                if skill in required_text:
                    required_skills.append(skill)
        
        # Find skills in preferred/bonus section
        preferred_section = re.search(r'(?:preferred|bonus).*?:(.*?)(?:location|salary|$)', desc_lower, re.DOTALL | re.IGNORECASE)
        if preferred_section:
            preferred_text = preferred_section.group(1)
            for skill in technical_skills:
                if skill in preferred_text and skill not in required_skills:
                    preferred_skills.append(skill)
        
        # If no specific sections found, extract from entire description
        if not required_skills and not preferred_skills:
            for skill in technical_skills:
                if skill in desc_lower:
                    required_skills.append(skill)
        
        return required_skills, preferred_skills

class CandidateMatcher:
    """Matches candidates against job descriptions"""
    
    def __init__(self):
        self.match_threshold = 0.3  # Minimum match score to be considered
        
    def match_candidate_to_job(self, candidate: Candidate, job_description: JobDescription) -> Dict[str, Any]:
        """Match a single candidate against a job description"""
        score = 0.0
        matched_skills = []
        
        # Create candidate skill profile from position and company
        candidate_profile = f"{candidate.position} {candidate.company}".lower()
        
        # Check for skill matches
        all_job_skills = job_description.required_skills + job_description.preferred_skills
        
        for skill in all_job_skills:
            if skill.lower() in candidate_profile:
                if skill in job_description.required_skills:
                    score += 1.0  # Higher weight for required skills
                else:
                    score += 0.5  # Lower weight for preferred skills
                matched_skills.append(skill)
        
        # Normalize score based on total possible points
        max_score = len(job_description.required_skills) + (len(job_description.preferred_skills) * 0.5)
        normalized_score = score / max_score if max_score > 0 else 0
        
        # Job title similarity bonus
        if self._check_title_similarity(candidate.position, job_description.title):
            normalized_score += 0.2
        
        # Cap score at 1.0
        normalized_score = min(normalized_score, 1.0)
        
        return {
            'candidate': candidate,
            'job_description': job_description,
            'score': normalized_score,
            'matched_skills': matched_skills,
            'is_match': normalized_score >= self.match_threshold
        }
    
    def _check_title_similarity(self, candidate_title: str, job_title: str) -> bool:
        """Check if candidate title is similar to job title"""
        candidate_words = set(candidate_title.lower().split())
        job_words = set(job_title.lower().split())
        
        # Remove common words
        common_words = {'the', 'and', 'or', 'of', 'in', 'at', 'to', 'for', 'with', 'by'}
        candidate_words -= common_words
        job_words -= common_words
        
        # Check for overlap
        overlap = len(candidate_words.intersection(job_words))
        return overlap >= 1
    
    def get_matches_for_job(self, candidates: List[Candidate], job_description: JobDescription, 
                          top_n: int = 10) -> List[Dict[str, Any]]:
        """Get top N candidate matches for a specific job"""
        matches = []
        
        for candidate in candidates:
            match_result = self.match_candidate_to_job(candidate, job_description)
            if match_result['is_match']:
                matches.append(match_result)
        
        # Sort by score (descending)
        matches.sort(key=lambda x: x['score'], reverse=True)
        
        return matches[:top_n]

class CandidateShortlister:
    """Main class for candidate shortlisting - compatible with Streamlit app"""
    
    def __init__(self, csv_file_path: str):
        self.csv_file_path = csv_file_path
        self.candidate_processor = CandidateProcessor(csv_file_path)
        self.matcher = CandidateMatcher()
        self.candidates = []
        
        # Initialize database if available
        self.database = None
        if DATABASE_AVAILABLE:
            try:
                self.database = CandidateDatabase(csv_path=csv_file_path)
                logger.info("Database integration enabled")
            except Exception as e:
                logger.warning(f"Database initialization failed: {e}")
                self.database = None
        
    def load_candidates(self):
        """Load candidates from CSV"""
        self.candidates = self.candidate_processor.load_candidates()
        return self.candidates
    
    def extract_skills_from_job(self, job_data: Dict[str, Any]) -> List[str]:
        """Extract skills from job description data"""
        skills = []
        
        # Check for skills in various fields
        skill_fields = ['skills_required', 'required_skills', 'skills', 'technologies']
        for field in skill_fields:
            if field in job_data and job_data[field]:
                if isinstance(job_data[field], list):
                    skills.extend(job_data[field])
                elif isinstance(job_data[field], str):
                    # Split by common delimiters
                    skills.extend([s.strip() for s in job_data[field].replace(',', ' ').replace(';', ' ').split()])
        
        # Extract from description if no specific skills field
        if not skills and 'description' in job_data:
            description = job_data['description'].lower()
            common_skills = [
                'python', 'java', 'javascript', 'react', 'angular', 'vue', 'node.js', 'django',
                'flask', 'spring', 'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'terraform',
                'jenkins', 'git', 'sql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
                'machine learning', 'ai', 'data science', 'tensorflow', 'pytorch', 'scikit-learn',
                'html', 'css', 'typescript', 'go', 'rust', 'c++', 'c#', '.net', 'php',
                'devops', 'ci/cd', 'microservices', 'restful api', 'graphql', 'agile', 'scrum'
            ]
            
            for skill in common_skills:
                if skill in description:
                    skills.append(skill)
        
        return list(set(skills))  # Remove duplicates
    
    def find_matches_for_job(self, job_data: Dict[str, Any], min_score: float = 0.1, max_candidates: int = 20) -> List[Dict[str, Any]]:
        """Find candidate matches for a specific job"""
        if not self.candidates:
            self.load_candidates()
        
        job_title = job_data.get('title', 'Unknown Job')
        job_skills = self.extract_skills_from_job(job_data)
        
        matches = []
        
        for candidate in self.candidates:
            score = self.calculate_match_score(candidate, job_skills, job_title)
            
            if score >= min_score:
                matched_skills = self.get_matched_skills(candidate, job_skills)
                
                match_result = {
                    'candidate': candidate.to_dict(),
                    'score': score,
                    'matched_skills': matched_skills,
                    'job_title': job_title
                }
                matches.append(match_result)
        
        # Sort by score (descending) and limit results
        matches.sort(key=lambda x: x['score'], reverse=True)
        return matches[:max_candidates]
    
    def calculate_match_score(self, candidate: Candidate, job_skills: List[str], job_title: str) -> float:
        """Calculate match score between candidate and job"""
        score = 0.0
        
        # Create candidate profile text
        candidate_text = f"{candidate.position} {candidate.company}".lower()
        
        # Skill matching
        if job_skills:
            matched_skills = 0
            for skill in job_skills:
                if skill.lower() in candidate_text:
                    matched_skills += 1
            
            skill_score = matched_skills / len(job_skills) if job_skills else 0
            score += skill_score * 0.7  # 70% weight for skills
        
        # Title similarity
        title_similarity = self.calculate_title_similarity(candidate.position, job_title)
        score += title_similarity * 0.3  # 30% weight for title similarity
        
        return min(score, 1.0)  # Cap at 1.0
    
    def calculate_title_similarity(self, candidate_title: str, job_title: str) -> float:
        """Calculate similarity between candidate title and job title"""
        candidate_words = set(candidate_title.lower().split())
        job_words = set(job_title.lower().split())
        
        # Remove common words
        common_words = {'the', 'and', 'or', 'of', 'in', 'at', 'to', 'for', 'with', 'by', 'a', 'an'}
        candidate_words -= common_words
        job_words -= common_words
        
        if not job_words:
            return 0.0
        
        # Calculate Jaccard similarity
        intersection = len(candidate_words.intersection(job_words))
        union = len(candidate_words.union(job_words))
        
        return intersection / union if union > 0 else 0.0
    
    def get_matched_skills(self, candidate: Candidate, job_skills: List[str]) -> List[str]:
        """Get list of skills that match between candidate and job"""
        candidate_text = f"{candidate.position} {candidate.company}".lower()
        matched = []
        
        for skill in job_skills:
            if skill.lower() in candidate_text:
                matched.append(skill)
        
        return matched

class ShortlistGenerator:
    """Generates shortlists of candidates for jobs"""
    
    def __init__(self, csv_file_path: str, job_descriptions_path: str):
        self.candidate_processor = CandidateProcessor(csv_file_path)
        self.job_processor = JobDescriptionProcessor(job_descriptions_path)
        self.matcher = CandidateMatcher()
        
    def generate_shortlists(self) -> Dict[str, List[Dict[str, Any]]]:
        """Generate shortlists for all job descriptions"""
        # Load data
        candidates = self.candidate_processor.load_candidates()
        job_descriptions = self.job_processor.load_job_descriptions()
        
        shortlists = {}
        
        for job_desc in job_descriptions:
            matches = self.matcher.get_matches_for_job(candidates, job_desc)
            shortlists[job_desc.title] = matches
            
            logger.info(f"Generated shortlist for '{job_desc.title}': {len(matches)} candidates")
        
        return shortlists
    
    def save_shortlists_to_json(self, shortlists: Dict[str, List[Dict[str, Any]]], 
                               output_path: str = "shortlists.json"):
        """Save shortlists to JSON file"""
        # Convert to serializable format
        serializable_shortlists = {}
        
        for job_title, matches in shortlists.items():
            serializable_matches = []
            for match in matches:
                serializable_match = {
                    'candidate': match['candidate'].to_dict(),
                    'job_title': job_title,
                    'score': match['score'],
                    'matched_skills': match['matched_skills'],
                    'is_match': match['is_match']
                }
                serializable_matches.append(serializable_match)
            
            serializable_shortlists[job_title] = serializable_matches
        
        try:
            with open(output_path, 'w', encoding='utf-8') as file:
                json.dump(serializable_shortlists, file, indent=2, ensure_ascii=False)
            
            logger.info(f"Shortlists saved to {output_path}")
            
        except Exception as e:
            logger.error(f"Error saving shortlists: {e}")
            raise

def main():
    """Main function for testing the shortlisting system"""
    # File paths
    csv_file = "connections.csv"
    job_descriptions_file = "templates/sample_job_descriptions.json"
    
    try:
        # Initialize shortlist generator
        generator = ShortlistGenerator(csv_file, job_descriptions_file)
        
        # Generate shortlists
        print("Generating candidate shortlists...")
        shortlists = generator.generate_shortlists()
        
        # Display results
        print(f"\n=== SHORTLIST RESULTS ===")
        for job_title, matches in shortlists.items():
            print(f"\nJob: {job_title}")
            print(f"Candidates found: {len(matches)}")
            
            for i, match in enumerate(matches[:5], 1):  # Show top 5
                candidate = match['candidate']
                score = match['score']
                skills = ', '.join(match['matched_skills'])
                
                # Convert candidate object to dict if needed
                if hasattr(candidate, 'to_dict'):
                    candidate_dict = candidate.to_dict()
                else:
                    candidate_dict = candidate
                
                print(f"  {i}. {candidate_dict['full_name']} - Score: {score:.2f}")
                print(f"     Position: {candidate_dict['position']} at {candidate_dict['company']}")
                print(f"     Skills: {skills}")
                print(f"     LinkedIn: {candidate_dict['linkedin_url']}")
                print(f"     Email: {candidate_dict['email']}")
                print()
        
        # Save to JSON
        generator.save_shortlists_to_json(shortlists)
        print("Shortlists saved to shortlists.json")
        
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        raise

if __name__ == "__main__":
    main()
