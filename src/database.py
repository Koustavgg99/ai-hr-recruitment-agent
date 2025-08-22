import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class Candidate:
    id: int
    name: str
    email: str
    linkedin_url: str
    skills: List[str]
    experience_years: int
    location: str
    summary: str
    match_score: float
    job_id: int
    sourced_date: datetime
    last_contacted: Optional[datetime] = None
    response_status: str = "not_contacted"  # not_contacted, contacted, responded, no_response
    notes: str = ""

@dataclass
class Job:
    id: int
    title: str
    company: str
    description: str
    required_skills: List[str]
    experience_level: str
    location: str
    posted_date: datetime
    status: str = "active"  # active, paused, closed

class HRDatabase:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Jobs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                company TEXT NOT NULL,
                description TEXT NOT NULL,
                required_skills TEXT NOT NULL,  -- JSON array
                experience_level TEXT NOT NULL,
                location TEXT NOT NULL,
                posted_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'active'
            )
        ''')
        
        # Candidates table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS candidates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                linkedin_url TEXT,
                skills TEXT,  -- JSON array
                experience_years INTEGER,
                location TEXT,
                summary TEXT,
                match_score REAL,
                job_id INTEGER,
                sourced_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_contacted TIMESTAMP,
                response_status TEXT DEFAULT 'not_contacted',
                notes TEXT,
                FOREIGN KEY (job_id) REFERENCES jobs (id)
            )
        ''')
        
        # Outreach log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS outreach_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id INTEGER,
                job_id INTEGER,
                outreach_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                message_content TEXT,
                platform TEXT,  -- email, linkedin, etc.
                status TEXT,     -- sent, delivered, responded, failed
                response_content TEXT,
                FOREIGN KEY (candidate_id) REFERENCES candidates (id),
                FOREIGN KEY (job_id) REFERENCES jobs (id)
            )
        ''')
        
        # Daily reports table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_date DATE UNIQUE,
                candidates_sourced INTEGER DEFAULT 0,
                candidates_shortlisted INTEGER DEFAULT 0,
                candidates_contacted INTEGER DEFAULT 0,
                responses_received INTEGER DEFAULT 0,
                report_data TEXT  -- JSON with detailed metrics
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_job(self, title: str, company: str, description: str, 
                required_skills: List[str], experience_level: str, location: str) -> int:
        """Add a new job posting"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO jobs (title, company, description, required_skills, experience_level, location)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (title, company, description, json.dumps(required_skills), experience_level, location))
        
        job_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return job_id
    
    def add_candidate(self, candidate: Candidate) -> int:
        """Add a new candidate"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO candidates 
                (name, email, linkedin_url, skills, experience_years, location, 
                 summary, match_score, job_id, response_status, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                candidate.name, candidate.email, candidate.linkedin_url,
                json.dumps(candidate.skills), candidate.experience_years,
                candidate.location, candidate.summary, candidate.match_score,
                candidate.job_id, candidate.response_status, candidate.notes
            ))
            
            candidate_id = cursor.lastrowid
            conn.commit()
            return candidate_id
        except sqlite3.IntegrityError:
            # Email already exists, return existing candidate ID
            cursor.execute('SELECT id FROM candidates WHERE email = ?', (candidate.email,))
            result = cursor.fetchone()
            return result[0] if result else None
        finally:
            conn.close()
    
    def log_outreach(self, candidate_id: int, job_id: int, message_content: str, 
                     platform: str = "email", status: str = "sent") -> int:
        """Log an outreach attempt"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO outreach_log (candidate_id, job_id, message_content, platform, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (candidate_id, job_id, message_content, platform, status))
        
        # Update candidate's last_contacted date
        cursor.execute('''
            UPDATE candidates 
            SET last_contacted = CURRENT_TIMESTAMP, response_status = 'contacted'
            WHERE id = ?
        ''', (candidate_id,))
        
        log_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return log_id
    
    def update_candidate_response(self, candidate_id: int, status: str, response_content: str = ""):
        """Update candidate response status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE candidates SET response_status = ? WHERE id = ?
        ''', (status, candidate_id))
        
        if response_content:
            cursor.execute('''
                UPDATE outreach_log 
                SET response_content = ?, status = 'responded' 
                WHERE candidate_id = ? 
                ORDER BY outreach_date DESC LIMIT 1
            ''', (response_content, candidate_id))
        
        conn.commit()
        conn.close()
    
    def get_candidates_by_job(self, job_id: int, limit: int = None) -> List[Dict]:
        """Get all candidates for a specific job"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT * FROM candidates 
            WHERE job_id = ? 
            ORDER BY match_score DESC
        '''
        
        if limit:
            query += f' LIMIT {limit}'
        
        cursor.execute(query, (job_id,))
        columns = [description[0] for description in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        # Parse JSON fields
        for result in results:
            result['skills'] = json.loads(result['skills']) if result['skills'] else []
        
        conn.close()
        return results
    
    def get_daily_metrics(self, date: str = None) -> Dict:
        """Get daily recruitment metrics"""
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get metrics for the day
        metrics = {}
        
        # Candidates sourced today
        cursor.execute('''
            SELECT COUNT(*) FROM candidates 
            WHERE DATE(sourced_date) = ?
        ''', (date,))
        metrics['candidates_sourced'] = cursor.fetchone()[0]
        
        # Candidates shortlisted (match_score > 0.7)
        cursor.execute('''
            SELECT COUNT(*) FROM candidates 
            WHERE DATE(sourced_date) = ? AND match_score > 0.7
        ''', (date,))
        metrics['candidates_shortlisted'] = cursor.fetchone()[0]
        
        # Candidates contacted today
        cursor.execute('''
            SELECT COUNT(*) FROM outreach_log 
            WHERE DATE(outreach_date) = ?
        ''', (date,))
        metrics['candidates_contacted'] = cursor.fetchone()[0]
        
        # Responses received today
        cursor.execute('''
            SELECT COUNT(*) FROM candidates 
            WHERE response_status = 'responded' AND DATE(last_contacted) = ?
        ''', (date,))
        metrics['responses_received'] = cursor.fetchone()[0]
        
        conn.close()
        return metrics
    
    def save_daily_report(self, metrics: Dict, date: str = None):
        """Save daily report to database"""
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO daily_reports 
            (report_date, candidates_sourced, candidates_shortlisted, 
             candidates_contacted, responses_received, report_data)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            date, metrics['candidates_sourced'], metrics['candidates_shortlisted'],
            metrics['candidates_contacted'], metrics['responses_received'],
            json.dumps(metrics)
        ))
        
        conn.commit()
        conn.close()
    
    def get_jobs(self, status: str = "active") -> List[Dict]:
        """Get all jobs with specified status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM jobs WHERE status = ? ORDER BY posted_date DESC', (status,))
        columns = [description[0] for description in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        # Parse JSON fields
        for result in results:
            result['required_skills'] = json.loads(result['required_skills'])
        
        conn.close()
        return results
