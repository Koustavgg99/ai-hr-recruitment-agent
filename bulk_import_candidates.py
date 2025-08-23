#!/usr/bin/env python3
"""
Bulk Import Script for HR Automation System
Imports all candidates from connections.csv to the SQLite database
"""

import pandas as pd
import sqlite3
import logging
from datetime import datetime
from pathlib import Path
import sys
import os

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database_manager import CandidateDatabase, get_database

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def bulk_import_candidates():
    """Import all candidates from CSV to database"""
    
    csv_path = "connections.csv"
    
    # Check if CSV file exists
    if not os.path.exists(csv_path):
        logger.error(f"CSV file {csv_path} not found!")
        return False
    
    try:
        # Read CSV file
        df = pd.read_csv(csv_path)
        logger.info(f"Found {len(df)} total rows in CSV file")
        
        # Initialize database
        db = get_database()
        
        # Get current candidate count
        initial_count = db.get_candidates_count()
        logger.info(f"Database currently has {initial_count} candidates")
        
        # Process each row
        added_count = 0
        skipped_count = 0
        error_count = 0
        
        for index, row in df.iterrows():
            try:
                # Skip rows with empty essential data
                first_name = str(row.get('First Name', '')).strip()
                last_name = str(row.get('Last Name', '')).strip()
                linkedin_url = str(row.get('URL', '')).strip()
                
                # Skip empty rows
                if not first_name and not last_name and not linkedin_url:
                    skipped_count += 1
                    continue
                
                if not linkedin_url or linkedin_url == 'nan':
                    logger.warning(f"Row {index + 2}: Missing LinkedIn URL for {first_name} {last_name}")
                    skipped_count += 1
                    continue
                
                # Handle NaN values
                def clean_value(val):
                    if pd.isna(val) or str(val).lower() == 'nan':
                        return ''
                    return str(val).strip()
                
                # Prepare candidate data
                full_name = f"{first_name} {last_name}".strip()
                
                candidate_data = {
                    'full_name': full_name,
                    'linkedin_url': linkedin_url,
                    'email': clean_value(row.get('Email Address', '')),
                    'company': clean_value(row.get('Company', '')),
                    'position': clean_value(row.get('Position', '')),
                    'connected_on': clean_value(row.get('Connected On', '')),
                    'location': '',  # Not in original CSV
                    'skills': '',    # Not in original CSV
                    'experience_summary': ''  # Not in original CSV
                }
                
                # Try to add candidate
                candidate_id = db.add_candidate(candidate_data)
                
                if candidate_id:
                    added_count += 1
                    if added_count % 50 == 0:  # Progress update every 50 candidates
                        logger.info(f"Progress: Added {added_count} candidates...")
                else:
                    skipped_count += 1  # Likely duplicate
                    
            except Exception as e:
                error_count += 1
                logger.error(f"Row {index + 2}: Error processing {first_name} {last_name}: {e}")
                continue
        
        # Final statistics
        final_count = db.get_candidates_count()
        logger.info("\n" + "="*60)
        logger.info("BULK IMPORT COMPLETED")
        logger.info("="*60)
        logger.info(f"Total rows processed: {len(df)}")
        logger.info(f"Successfully added: {added_count}")
        logger.info(f"Skipped (duplicates/empty): {skipped_count}")
        logger.info(f"Errors: {error_count}")
        logger.info(f"Database count before: {initial_count}")
        logger.info(f"Database count after: {final_count}")
        logger.info(f"Net increase: {final_count - initial_count}")
        logger.info("="*60)
        
        return True
        
    except Exception as e:
        logger.error(f"Bulk import failed: {e}")
        return False

def verify_import():
    """Verify the import by showing some statistics"""
    try:
        db = get_database()
        
        # Get total count
        total_count = db.get_candidates_count()
        
        # Get some sample candidates
        candidates = db.get_all_candidates()
        
        print(f"\n📊 DATABASE VERIFICATION")
        print(f"Total candidates in database: {total_count}")
        
        if candidates:
            print(f"\n🔍 Sample of recent candidates:")
            for i, candidate in enumerate(candidates[:5]):
                print(f"  {i+1}. {candidate['full_name']} - {candidate['company']} ({candidate['position']})")
        
        # Show company distribution
        with sqlite3.connect("hr_automation.db") as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT company, COUNT(*) as count 
                FROM candidates 
                WHERE company != '' AND company IS NOT NULL
                GROUP BY company 
                ORDER BY count DESC 
                LIMIT 10
            """)
            
            companies = cursor.fetchall()
            if companies:
                print(f"\n🏢 Top companies:")
                for company, count in companies:
                    print(f"  • {company}: {count} candidates")
        
        return True
        
    except Exception as e:
        logger.error(f"Verification failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting bulk import of candidates from CSV to database...")
    print("This will add all candidates from connections.csv to the HR automation database.")
    print("-" * 60)
    
    # Run bulk import
    success = bulk_import_candidates()
    
    if success:
        print("\n✅ Import completed successfully!")
        
        # Verify the import
        print("\n🔍 Verifying import...")
        verify_import()
        
        print("\n🎉 All candidates have been successfully imported!")
        print("You can now use the Streamlit app to manage all your candidates.")
        
    else:
        print("\n❌ Import failed. Please check the logs above for details.")
        sys.exit(1)
