"""
HR Automation - Database Manager
Handles SQLite database operations for candidate management and CSV synchronization
"""

import sqlite3
import pandas as pd
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import csv
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CandidateDatabase:
    """Manages SQLite database for candidate data with CSV synchronization"""
    
    def __init__(self, db_path: str = "hr_automation.db", csv_path: str = "connections.csv"):
        self.db_path = db_path
        self.csv_path = csv_path
        self.init_database()
        self.sync_csv_to_db()
    
    def init_database(self):
        """Initialize the database with required tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create candidates table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS candidates (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        first_name TEXT,
                        last_name TEXT,
                        full_name TEXT,
                        linkedin_url TEXT UNIQUE,
                        email TEXT,
                        company TEXT,
                        position TEXT,
                        connected_on TEXT,
                        location TEXT,
                        skills TEXT,
                        experience_summary TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create jobs table for future use
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS jobs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        company TEXT,
                        department TEXT,
                        location TEXT,
                        experience_level TEXT,
                        employment_type TEXT,
                        description TEXT,
                        skills_required TEXT,
                        skills_preferred TEXT,
                        salary_range TEXT,
                        benefits TEXT,
                        reporting_to TEXT,
                        team_size TEXT,
                        status TEXT DEFAULT 'active',
                        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create shortlists table for tracking matches
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS shortlists (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        job_id INTEGER,
                        candidate_id INTEGER,
                        match_score REAL,
                        matched_skills TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (job_id) REFERENCES jobs (id),
                        FOREIGN KEY (candidate_id) REFERENCES candidates (id)
                    )
                ''')
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def sync_csv_to_db(self):
        """Sync existing CSV data to database"""
        if not os.path.exists(self.csv_path):
            logger.warning(f"CSV file {self.csv_path} not found. Skipping sync.")
            return
        
        try:
            # Read CSV data
            df = pd.read_csv(self.csv_path)
            logger.info(f"Loading {len(df)} candidates from CSV")
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get existing LinkedIn URLs to avoid duplicates
                cursor.execute("SELECT linkedin_url FROM candidates WHERE linkedin_url IS NOT NULL")
                existing_urls = set(row[0] for row in cursor.fetchall())
                
                added_count = 0
                for _, row in df.iterrows():
                    linkedin_url = row.get('URL', '').strip()
                    
                    # Skip if LinkedIn URL already exists or is empty
                    if not linkedin_url or linkedin_url in existing_urls:
                        continue
                    
                    # Extract name components
                    full_name = row.get('First Name', '').strip() + ' ' + row.get('Last Name', '').strip()
                    full_name = full_name.strip()
                    
                    candidate_data = {
                        'first_name': row.get('First Name', '').strip(),
                        'last_name': row.get('Last Name', '').strip(),
                        'full_name': full_name,
                        'linkedin_url': linkedin_url,
                        'email': row.get('Email Address', '').strip(),
                        'company': row.get('Company', '').strip(),
                        'position': row.get('Position', '').strip(),
                        'connected_on': row.get('Connected On', '').strip()
                    }
                    
                    try:
                        cursor.execute('''
                            INSERT INTO candidates (
                                first_name, last_name, full_name, linkedin_url,
                                email, company, position, connected_on
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            candidate_data['first_name'],
                            candidate_data['last_name'],
                            candidate_data['full_name'],
                            candidate_data['linkedin_url'],
                            candidate_data['email'],
                            candidate_data['company'],
                            candidate_data['position'],
                            candidate_data['connected_on']
                        ))
                        
                        existing_urls.add(linkedin_url)
                        added_count += 1
                        
                    except sqlite3.IntegrityError:
                        # Skip duplicates
                        continue
                
                conn.commit()
                logger.info(f"Successfully synced {added_count} new candidates to database")
                
        except Exception as e:
            logger.error(f"Failed to sync CSV to database: {e}")
    
    def add_candidate(self, candidate_data: Dict[str, Any]) -> Optional[int]:
        """
        Add a new candidate to both database and CSV
        
        Args:
            candidate_data: Dictionary containing candidate information
            
        Returns:
            Candidate ID if successful, None if failed
        """
        try:
            # Validate required fields
            required_fields = ['full_name', 'linkedin_url']
            for field in required_fields:
                if not candidate_data.get(field, '').strip():
                    raise ValueError(f"Required field '{field}' is missing or empty")
            
            # Prepare data
            full_name = candidate_data['full_name'].strip()
            name_parts = full_name.split(' ', 1)
            first_name = name_parts[0] if name_parts else ''
            last_name = name_parts[1] if len(name_parts) > 1 else ''
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Check if candidate already exists
                cursor.execute(
                    "SELECT id FROM candidates WHERE linkedin_url = ?",
                    (candidate_data['linkedin_url'],)
                )
                existing = cursor.fetchone()
                if existing:
                    logger.warning(f"Candidate with LinkedIn URL {candidate_data['linkedin_url']} already exists")
                    return existing[0]
                
                # Insert new candidate
                cursor.execute('''
                    INSERT INTO candidates (
                        first_name, last_name, full_name, linkedin_url,
                        email, company, position, connected_on,
                        location, skills, experience_summary
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    first_name,
                    last_name,
                    full_name,
                    candidate_data.get('linkedin_url', ''),
                    candidate_data.get('email', ''),
                    candidate_data.get('company', ''),
                    candidate_data.get('position', ''),
                    candidate_data.get('connected_on', datetime.now().strftime('%d-%b-%y')),
                    candidate_data.get('location', ''),
                    candidate_data.get('skills', ''),
                    candidate_data.get('experience_summary', '')
                ))
                
                candidate_id = cursor.lastrowid
                conn.commit()
                
                # Also add to CSV file
                self._add_to_csv(candidate_data, first_name, last_name)
                
                logger.info(f"Successfully added candidate {full_name} with ID {candidate_id}")
                return candidate_id
                
        except Exception as e:
            logger.error(f"Failed to add candidate: {e}")
            return None
    
    def _add_to_csv(self, candidate_data: Dict[str, Any], first_name: str, last_name: str):
        """Add candidate to CSV file"""
        try:
            # Prepare CSV row
            csv_row = {
                'First Name': first_name,
                'Last Name': last_name,
                'Email Address': candidate_data.get('email', ''),
                'Company': candidate_data.get('company', ''),
                'Position': candidate_data.get('position', ''),
                'Connected On': candidate_data.get('connected_on', datetime.now().strftime('%d-%b-%y')),
                'URL': candidate_data.get('linkedin_url', '')
            }
            
            # Check if CSV exists and has headers
            csv_exists = os.path.exists(self.csv_path)
            
            if csv_exists:
                # Read existing CSV to get headers
                df = pd.read_csv(self.csv_path)
                headers = df.columns.tolist()
            else:
                headers = list(csv_row.keys())
            
            # Write to CSV
            with open(self.csv_path, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                
                # Write header if file is new
                if not csv_exists:
                    writer.writeheader()
                
                writer.writerow(csv_row)
            
            logger.info("Candidate added to CSV successfully")
            
        except Exception as e:
            logger.error(f"Failed to add candidate to CSV: {e}")
    
    def get_all_candidates(self) -> List[Dict[str, Any]]:
        """Get all candidates from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, first_name, last_name, full_name, linkedin_url,
                           email, company, position, connected_on, location,
                           skills, experience_summary, created_at, updated_at
                    FROM candidates
                    ORDER BY created_at DESC
                ''')
                
                columns = [description[0] for description in cursor.description]
                candidates = []
                
                for row in cursor.fetchall():
                    candidate = dict(zip(columns, row))
                    candidates.append(candidate)
                
                return candidates
                
        except Exception as e:
            logger.error(f"Failed to get candidates: {e}")
            return []
    
    def search_candidates(self, search_term: str) -> List[Dict[str, Any]]:
        """Search candidates by name, company, or position"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                search_pattern = f"%{search_term}%"
                cursor.execute('''
                    SELECT id, first_name, last_name, full_name, linkedin_url,
                           email, company, position, connected_on, location,
                           skills, experience_summary, created_at, updated_at
                    FROM candidates
                    WHERE full_name LIKE ? OR company LIKE ? OR position LIKE ?
                    ORDER BY full_name
                ''', (search_pattern, search_pattern, search_pattern))
                
                columns = [description[0] for description in cursor.description]
                candidates = []
                
                for row in cursor.fetchall():
                    candidate = dict(zip(columns, row))
                    candidates.append(candidate)
                
                return candidates
                
        except Exception as e:
            logger.error(f"Failed to search candidates: {e}")
            return []
    
    def get_candidate_by_id(self, candidate_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific candidate by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, first_name, last_name, full_name, linkedin_url,
                           email, company, position, connected_on, location,
                           skills, experience_summary, created_at, updated_at
                    FROM candidates
                    WHERE id = ?
                ''', (candidate_id,))
                
                row = cursor.fetchone()
                if row:
                    columns = [description[0] for description in cursor.description]
                    return dict(zip(columns, row))
                
                return None
                
        except Exception as e:
            logger.error(f"Failed to get candidate by ID: {e}")
            return None
    
    def update_candidate(self, candidate_id: int, candidate_data: Dict[str, Any]) -> bool:
        """Update an existing candidate"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Prepare update data
                update_fields = []
                update_values = []
                
                updatable_fields = [
                    'first_name', 'last_name', 'full_name', 'email', 
                    'company', 'position', 'location', 'skills', 'experience_summary'
                ]
                
                for field in updatable_fields:
                    if field in candidate_data:
                        update_fields.append(f"{field} = ?")
                        update_values.append(candidate_data[field])
                
                if not update_fields:
                    logger.warning("No valid fields to update")
                    return False
                
                # Add updated timestamp
                update_fields.append("updated_at = ?")
                update_values.append(datetime.now().isoformat())
                update_values.append(candidate_id)
                
                # Execute update
                query = f"UPDATE candidates SET {', '.join(update_fields)} WHERE id = ?"
                cursor.execute(query, update_values)
                
                if cursor.rowcount > 0:
                    conn.commit()
                    logger.info(f"Successfully updated candidate ID {candidate_id}")
                    return True
                else:
                    logger.warning(f"No candidate found with ID {candidate_id}")
                    return False
                
        except Exception as e:
            logger.error(f"Failed to update candidate: {e}")
            return False
    
    def delete_candidate(self, candidate_id: int) -> bool:
        """Delete a candidate from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM candidates WHERE id = ?", (candidate_id,))
                
                if cursor.rowcount > 0:
                    conn.commit()
                    logger.info(f"Successfully deleted candidate ID {candidate_id}")
                    return True
                else:
                    logger.warning(f"No candidate found with ID {candidate_id}")
                    return False
                
        except Exception as e:
            logger.error(f"Failed to delete candidate: {e}")
            return False
    
    def get_candidates_count(self) -> int:
        """Get total count of candidates"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM candidates")
                return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Failed to get candidate count: {e}")
            return 0
    
    def export_to_csv(self, output_path: str = None) -> str:
        """Export all candidates to CSV file"""
        try:
            if not output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f"candidates_export_{timestamp}.csv"
            
            candidates = self.get_all_candidates()
            
            if not candidates:
                logger.warning("No candidates to export")
                return ""
            
            # Convert to DataFrame and export
            df = pd.DataFrame(candidates)
            df.to_csv(output_path, index=False)
            
            logger.info(f"Exported {len(candidates)} candidates to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to export candidates: {e}")
            return ""

# Utility functions
def get_database() -> CandidateDatabase:
    """Get database instance (singleton pattern)"""
    if not hasattr(get_database, 'instance'):
        get_database.instance = CandidateDatabase()
    return get_database.instance

if __name__ == "__main__":
    # Test the database functionality
    db = CandidateDatabase()
    
    print(f"Total candidates in database: {db.get_candidates_count()}")
    
    # Test adding a candidate
    test_candidate = {
        'full_name': 'Test User',
        'linkedin_url': 'https://linkedin.com/in/testuser',
        'email': 'test@example.com',
        'company': 'Test Company',
        'position': 'Test Engineer'
    }
    
    candidate_id = db.add_candidate(test_candidate)
    if candidate_id:
        print(f"Added test candidate with ID: {candidate_id}")
        
        # Test retrieval
        retrieved = db.get_candidate_by_id(candidate_id)
        print(f"Retrieved candidate: {retrieved['full_name']}")
        
        # Clean up test data
        db.delete_candidate(candidate_id)
        print("Cleaned up test data")
    
    print("Database functionality test completed")
