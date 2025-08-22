import os
import json
import re
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import google.generativeai as genai
import ollama
from dataclasses import dataclass, asdict
import requests
from database import HRDatabase, Candidate, Job

class AIService:
    """Wrapper for AI services (Gemini and Ollama)"""
    
    def __init__(self, google_api_key: str, ollama_host: str = "http://localhost:11434", 
                 ollama_model: str = "llama3.1:8b"):
        # Configure Gemini
        genai.configure(api_key=google_api_key)
        self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Configure Ollama
        self.ollama_host = ollama_host
        self.ollama_model = ollama_model
        self.ollama_client = ollama.Client(host=ollama_host)
    
    def analyze_job_description(self, job_description: str) -> Dict:
        """Use Gemini to extract structured data from job description"""
        prompt = f"""
        Analyze the following job description and extract structured information in JSON format:
        
        Job Description:
        {job_description}
        
        Please extract and return a JSON object with the following fields:
        - title: Job title
        - company: Company name (if mentioned)
        - required_skills: Array of required technical skills
        - preferred_skills: Array of preferred/nice-to-have skills
        - experience_level: Entry/Mid/Senior/Executive
        - location: Job location (if mentioned)
        - salary_range: Salary information (if mentioned)
        - key_responsibilities: Array of main responsibilities
        - qualifications: Array of required qualifications
        
        Return only valid JSON without any markdown formatting.
        """
        
        try:
            response = self.gemini_model.generate_content(prompt)
            # Clean the response to extract JSON
            content = response.text.strip()
            if content.startswith('```json'):
                content = content[7:-3]
            elif content.startswith('```'):
                content = content[3:-3]
            
            return json.loads(content)
        except Exception as e:
            print(f"Error analyzing job description with Gemini: {e}")
            return self._fallback_jd_analysis(job_description)
    
    def _fallback_jd_analysis(self, job_description: str) -> Dict:
        """Fallback method for JD analysis using regex patterns"""
        # Simple keyword extraction as fallback
        skills_keywords = ['python', 'java', 'javascript', 'react', 'node.js', 'sql', 'aws', 'docker', 'kubernetes']
        found_skills = [skill for skill in skills_keywords if skill.lower() in job_description.lower()]
        
        return {
            "title": "Software Developer",  # Default
            "company": "Not specified",
            "required_skills": found_skills,
            "preferred_skills": [],
            "experience_level": "Mid",
            "location": "Remote",
            "salary_range": "Not specified",
            "key_responsibilities": ["Software development"],
            "qualifications": ["Bachelor's degree"]
        }
    
    def generate_outreach_email(self, candidate: Dict, job: Dict) -> str:
        """Use Ollama to generate personalized outreach email"""
        prompt = f"""
        Generate a professional, personalized recruitment email for the following candidate and job:
        
        Candidate:
        - Name: {candidate['name']}
        - Skills: {', '.join(candidate['skills'])}
        - Experience: {candidate['experience_years']} years
        - Location: {candidate['location']}
        - Summary: {candidate['summary']}
        
        Job:
        - Title: {job['title']}
        - Company: {job['company']}
        - Location: {job['location']}
        - Required Skills: {', '.join(job['required_skills'])}
        
        Requirements:
        1. Keep it concise (under 200 words)
        2. Mention specific skills that match
        3. Be professional but friendly
        4. Include a clear call-to-action
        5. Don't be overly salesy
        6. Personalize based on candidate's background
        
        Return only the email content without subject line.
        """
        
        try:
            response = self.ollama_client.chat(
                model=self.ollama_model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response['message']['content'].strip()
        except Exception as e:
            print(f"Error generating email with Ollama: {e}")
            return self._fallback_email_template(candidate, job)
    
    def _fallback_email_template(self, candidate: Dict, job: Dict) -> str:
        """Fallback email template"""
        return f"""Hi {candidate['name']},

I hope this message finds you well. I came across your profile and was impressed by your background in {', '.join(candidate['skills'][:3])}.

We have an exciting opportunity for a {job['title']} position at {job['company']} that I believe could be a great fit for your {candidate['experience_years']} years of experience.

The role involves working with technologies you're familiar with, including {', '.join(set(candidate['skills']) & set(job['required_skills']))}.

Would you be interested in learning more about this opportunity? I'd love to schedule a brief call to discuss how your expertise could contribute to our team.

Best regards,
HR Recruitment Team"""

    def rank_candidate_match(self, candidate: Dict, job: Dict) -> float:
        """Use AI to calculate candidate-job match score"""
        prompt = f"""
        Calculate a match score (0.0 to 1.0) between this candidate and job requirement:
        
        Candidate:
        - Skills: {candidate.get('skills', [])}
        - Experience: {candidate.get('experience_years', 0)} years
        - Location: {candidate.get('location', 'Unknown')}
        
        Job Requirements:
        - Required Skills: {job.get('required_skills', [])}
        - Experience Level: {job.get('experience_level', 'Mid')}
        - Location: {job.get('location', 'Remote')}
        
        Consider:
        - Skill overlap (weight: 50%)
        - Experience level match (weight: 30%)
        - Location compatibility (weight: 20%)
        
        Return only a number between 0.0 and 1.0 (e.g., 0.85)
        """
        
        try:
            response = self.ollama_client.chat(
                model=self.ollama_model,
                messages=[{"role": "user", "content": prompt}]
            )
            score_text = response['message']['content'].strip()
            return float(re.findall(r'0\.\d+|1\.0', score_text)[0])
        except:
            # Fallback calculation
            return self._calculate_match_score_fallback(candidate, job)
    
    def _calculate_match_score_fallback(self, candidate: Dict, job: Dict) -> float:
        """Fallback match score calculation"""
        score = 0.0
        
        # Skill match (50% weight)
        candidate_skills = set(s.lower() for s in candidate.get('skills', []))
        required_skills = set(s.lower() for s in job.get('required_skills', []))
        
        if required_skills:
            skill_overlap = len(candidate_skills & required_skills) / len(required_skills)
            score += skill_overlap * 0.5
        
        # Experience match (30% weight)
        exp_years = candidate.get('experience_years', 0)
        exp_level = job.get('experience_level', 'Mid').lower()
        
        if exp_level == 'entry' and exp_years <= 2:
            score += 0.3
        elif exp_level == 'mid' and 2 <= exp_years <= 7:
            score += 0.3
        elif exp_level == 'senior' and exp_years >= 5:
            score += 0.3
        elif exp_level == 'executive' and exp_years >= 10:
            score += 0.3
        else:
            score += 0.1  # Partial match
        
        # Location match (20% weight)
        candidate_location = candidate.get('location', '').lower()
        job_location = job.get('location', '').lower()
        
        if 'remote' in job_location or 'remote' in candidate_location:
            score += 0.2
        elif candidate_location in job_location or job_location in candidate_location:
            score += 0.2
        else:
            score += 0.05  # Different locations but still possible
        
        return min(score, 1.0)

class MockLinkedInAPI:
    """Mock LinkedIn API for demonstration purposes"""
    
    def __init__(self):
        # Sample candidate data for demonstration
        self.mock_candidates = [
            {
                "name": "John Smith",
                "email": "john.smith@email.com",
                "linkedin_url": "https://linkedin.com/in/johnsmith",
                "skills": ["Python", "Django", "PostgreSQL", "AWS", "Docker"],
                "experience_years": 5,
                "location": "San Francisco, CA",
                "summary": "Full-stack developer with 5 years experience building scalable web applications."
            },
            {
                "name": "Sarah Johnson",
                "email": "sarah.johnson@email.com",
                "linkedin_url": "https://linkedin.com/in/sarahjohnson",
                "skills": ["React", "Node.js", "TypeScript", "MongoDB", "GraphQL"],
                "experience_years": 3,
                "location": "New York, NY",
                "summary": "Frontend specialist passionate about creating intuitive user experiences."
            },
            {
                "name": "Mike Chen",
                "email": "mike.chen@email.com",
                "linkedin_url": "https://linkedin.com/in/mikechen",
                "skills": ["Java", "Spring", "Kubernetes", "Microservices", "Jenkins"],
                "experience_years": 8,
                "location": "Seattle, WA",
                "summary": "Senior backend engineer with expertise in distributed systems and DevOps."
            },
            {
                "name": "Emily Davis",
                "email": "emily.davis@email.com",
                "linkedin_url": "https://linkedin.com/in/emilydavis",
                "skills": ["Python", "Machine Learning", "TensorFlow", "AWS", "Pandas"],
                "experience_years": 4,
                "location": "Austin, TX",
                "summary": "Data scientist with strong background in ML model development and deployment."
            },
            {
                "name": "Alex Rodriguez",
                "email": "alex.rodriguez@email.com",
                "linkedin_url": "https://linkedin.com/in/alexrodriguez",
                "skills": ["JavaScript", "Vue.js", "PHP", "MySQL", "Laravel"],
                "experience_years": 6,
                "location": "Remote",
                "summary": "Full-stack developer specializing in modern web technologies and API development."
            },
             {
                "name": "Subham Biswas",
                "email": "subhambiswas330@gmail.com",
                "linkedin_url": "https://www.linkedin.com/in/subham-biswas-768b47255",
                "skills": ["JavaScript", "Vue.js", "PHP", "MySQL", "Laravel","C++","AI","ML", "Python"],
                "experience_years": 6,
                "location": "India",
                "summary": "I'm Subham Biswas, a B.Tech Computer Science student at Techno India University. Passionate about Data Structures,Data-Base Algorithms, and Web Development, I enjoy problem-solving challenges."
            }
        ]
    
    def search_candidates(self, skills: List[str], location: str = "", experience_min: int = 0) -> List[Dict]:
        """Mock candidate search based on skills and criteria"""
        matches = []
        
        for candidate in self.mock_candidates:
            # Check skill overlap with flexible matching
            candidate_skills_lower = [s.lower() for s in candidate['skills']]
            required_skills_lower = [s.lower() for s in skills]
            
            skill_matches = 0
            for req_skill in required_skills_lower:
                for cand_skill in candidate_skills_lower:
                    # Flexible matching: check if any part of the skill matches
                    req_parts = req_skill.replace(' ', '').replace('-', '').replace('_', '')
                    cand_parts = cand_skill.replace(' ', '').replace('-', '').replace('_', '')
                    
                    if req_parts in cand_parts or cand_parts in req_parts:
                        skill_matches += 1
                        break
                    
                    # Special case matching
                    if ('microservice' in req_parts and 'microservice' in cand_parts) or \
                       ('postgresql' in req_parts and 'postgres' in cand_parts) or \
                       ('javascript' in req_parts and 'js' in cand_parts):
                        skill_matches += 1
                        break
            
            # Check experience
            if candidate['experience_years'] >= experience_min:
                # Check location (if specified)
                if not location or location.lower() == 'remote' or \
                   location.lower() in candidate['location'].lower() or \
                   candidate['location'].lower() == 'remote':
                    if skill_matches > 0:  # At least one skill match
                        matches.append(candidate.copy())
        
        return matches

class HRRecruitmentAgent:
    """Main HR Recruitment Agent class"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.db = HRDatabase(config['database_path'])
        self.ai_service = AIService(
            config['google_api_key'],
            config.get('ollama_host', 'http://localhost:11434'),
            config.get('ollama_model', 'llama3.1:8b')
        )
        self.linkedin_api = MockLinkedInAPI()  # Replace with real API when available
    
    def process_job_description(self, job_description: str, company: str = "TechCorp") -> int:
        """Process JD and extract requirements using Gemini"""
        print("🔍 Analyzing job description...")
        
        # Use Gemini to analyze the JD
        jd_analysis = self.ai_service.analyze_job_description(job_description)
        
        # Save job to database
        company_name = company or jd_analysis.get('company') or 'TechCorp'
        title = jd_analysis.get('title') or 'Software Developer'
        required_skills = jd_analysis.get('required_skills') or []
        experience_level = jd_analysis.get('experience_level') or 'Mid'
        location = jd_analysis.get('location') or 'Remote'
        
        job_id = self.db.add_job(
            title=title,
            company=company_name,
            description=job_description,
            required_skills=required_skills,
            experience_level=experience_level,
            location=location
        )
        
        print(f"✅ Job analyzed and saved (ID: {job_id})")
        print(f"📋 Required skills: {', '.join(jd_analysis.get('required_skills', []))}")
        print(f"🎯 Experience level: {jd_analysis.get('experience_level', 'Mid')}")
        
        return job_id
    
    def source_candidates(self, job_id: int, max_candidates: int = 20) -> List[Dict]:
        """Source candidates for a specific job"""
        print("🔎 Sourcing candidates...")
        
        # Get job details
        jobs = self.db.get_jobs()
        job = next((j for j in jobs if j['id'] == job_id), None)
        
        if not job:
            raise ValueError(f"Job with ID {job_id} not found")
        
        # Search for candidates
        candidates = self.linkedin_api.search_candidates(
            skills=job['required_skills'],
            location=job['location'],
            experience_min=self._get_min_experience(job['experience_level'])
        )
        
        # Rank candidates
        ranked_candidates = []
        for candidate_data in candidates[:max_candidates]:
            match_score = self.ai_service.rank_candidate_match(candidate_data, job)
            
            candidate = Candidate(
                id=0,  # Will be set by database
                name=candidate_data['name'],
                email=candidate_data['email'],
                linkedin_url=candidate_data['linkedin_url'],
                skills=candidate_data['skills'],
                experience_years=candidate_data['experience_years'],
                location=candidate_data['location'],
                summary=candidate_data['summary'],
                match_score=match_score,
                job_id=job_id,
                sourced_date=datetime.now()
            )
            
            # Add to database
            candidate_id = self.db.add_candidate(candidate)
            if candidate_id:
                candidate.id = candidate_id
                ranked_candidates.append(asdict(candidate))
        
        # Sort by match score
        ranked_candidates.sort(key=lambda x: x['match_score'], reverse=True)
        
        print(f"✅ Sourced {len(ranked_candidates)} candidates")
        return ranked_candidates
    
    def _get_min_experience(self, experience_level: str) -> int:
        """Convert experience level to minimum years"""
        mapping = {
            'entry': 0,
            'mid': 2,
            'senior': 5,
            'executive': 10
        }
        return mapping.get(experience_level.lower(), 0)
    
    def generate_outreach_campaigns(self, job_id: int, min_match_score: float = 0.6, 
                                   max_outreach: int = 10) -> List[Dict]:
        """Generate outreach emails for top candidates"""
        print("📧 Generating outreach campaigns...")
        
        # Get job details
        jobs = self.db.get_jobs()
        job = next((j for j in jobs if j['id'] == job_id), None)
        
        # Get top candidates
        candidates = self.db.get_candidates_by_job(job_id)
        shortlisted = [c for c in candidates if c['match_score'] >= min_match_score][:max_outreach]
        
        outreach_campaigns = []
        
        for candidate in shortlisted:
            if candidate['response_status'] == 'not_contacted':
                # Generate personalized email
                email_content = self.ai_service.generate_outreach_email(candidate, job)
                
                # Log outreach
                outreach_id = self.db.log_outreach(
                    candidate['id'], job_id, email_content, "email", "generated"
                )
                
                outreach_campaigns.append({
                    "candidate_id": candidate['id'],
                    "candidate_name": candidate['name'],
                    "candidate_email": candidate['email'],
                    "match_score": candidate['match_score'],
                    "email_content": email_content,
                    "outreach_id": outreach_id
                })
        
        print(f"✅ Generated {len(outreach_campaigns)} outreach emails")
        return outreach_campaigns
    
    def send_outreach_emails(self, outreach_campaigns: List[Dict]) -> Dict:
        """Simulate sending outreach emails (in real implementation, integrate with email service)"""
        print("📤 Sending outreach emails...")
        
        sent_count = 0
        failed_count = 0
        
        for campaign in outreach_campaigns:
            try:
                # Simulate email sending (replace with actual SMTP in production)
                print(f"  📧 Sending to {campaign['candidate_name']} ({campaign['candidate_email']})")
                
                # Update database status
                self.db.log_outreach(
                    campaign['candidate_id'], 
                    campaign.get('job_id', 1),
                    campaign['email_content'],
                    "email",
                    "sent"
                )
                
                sent_count += 1
                
            except Exception as e:
                print(f"  ❌ Failed to send to {campaign['candidate_email']}: {e}")
                failed_count += 1
        
        result = {
            "sent": sent_count,
            "failed": failed_count,
            "total": len(outreach_campaigns)
        }
        
        print(f"✅ Email campaign completed: {sent_count} sent, {failed_count} failed")
        return result
    
    def generate_daily_report(self, date: str = None) -> Dict:
        """Generate comprehensive daily recruitment report"""
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        print(f"📊 Generating daily report for {date}...")
        
        # Get basic metrics
        metrics = self.db.get_daily_metrics(date)
        
        # Add detailed breakdown
        detailed_report = {
            "date": date,
            "summary": metrics,
            "job_breakdown": [],
            "top_candidates": [],
            "outreach_performance": {
                "total_sent": metrics['candidates_contacted'],
                "response_rate": 0,
                "pending_responses": 0
            }
        }
        
        # Get job-specific metrics
        jobs = self.db.get_jobs()
        for job in jobs:
            candidates = self.db.get_candidates_by_job(job['id'])
            job_metrics = {
                "job_id": job['id'],
                "job_title": job['title'],
                "candidates_sourced": len(candidates),
                "avg_match_score": sum(c['match_score'] for c in candidates) / len(candidates) if candidates else 0,
                "top_candidate": candidates[0]['name'] if candidates else "None"
            }
            detailed_report["job_breakdown"].append(job_metrics)
        
        # Save report
        self.db.save_daily_report(detailed_report, date)
        
        print("✅ Daily report generated")
        return detailed_report
    
    def get_pipeline_status(self) -> Dict:
        """Get current recruitment pipeline status"""
        jobs = self.db.get_jobs()
        
        pipeline = {
            "active_jobs": len(jobs),
            "total_candidates": 0,
            "contacted_candidates": 0,
            "responded_candidates": 0,
            "jobs_detail": []
        }
        
        for job in jobs:
            candidates = self.db.get_candidates_by_job(job['id'])
            contacted = len([c for c in candidates if c['response_status'] in ['contacted', 'responded']])
            responded = len([c for c in candidates if c['response_status'] == 'responded'])
            
            pipeline["total_candidates"] += len(candidates)
            pipeline["contacted_candidates"] += contacted
            pipeline["responded_candidates"] += responded
            
            pipeline["jobs_detail"].append({
                "job_id": job['id'],
                "title": job['title'],
                "candidates": len(candidates),
                "contacted": contacted,
                "responded": responded,
                "response_rate": f"{(responded/contacted*100):.1f}%" if contacted > 0 else "0%"
            })
        
        return pipeline
