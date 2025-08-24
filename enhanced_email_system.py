"""
HR Automation - Enhanced Email System
Includes manual email sending and updated configuration
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

# Import the new configuration
from hr_email_config import get_email_config, get_email_template, get_available_templates

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedEmailManager:
    """Enhanced email manager with manual sending capabilities"""
    
    def __init__(self):
        self.config = get_email_config()
        self.email_log = []
        
    def send_manual_email(self, candidate_name: str, candidate_email: str, 
                         job_title: str, template_type: str = "interview_invitation") -> bool:
        """
        Send manual email to a specific candidate
        
        Args:
            candidate_name: Name of the candidate
            candidate_email: Email address of the candidate
            job_title: Job title/position
            template_type: Email template to use
            
        Returns:
            Success status
        """
        try:
            print(f"📧 Sending manual email to {candidate_name} ({candidate_email})")
            print(f"📋 Job: {job_title}")
            print(f"📝 Template: {template_type}")
            
            # Get email template
            template = get_email_template(template_type)
            
            # Prepare template variables
            template_vars = {
                'candidate_name': candidate_name,
                'job_title': job_title,
                'company_name': self.config.COMPANY_NAME,
                'company_website': self.config.COMPANY_WEBSITE,
                'sender_name': self.config.SENDER_NAME,
                'hr_contact_name': self.config.HR_CONTACT_NAME,
                'hr_contact_email': self.config.HR_CONTACT_EMAIL,
                'hr_contact_phone': self.config.HR_CONTACT_PHONE,
                'experience_years': '3+',  # Default
                'skills': 'Technical Skills'  # Default
            }
            
            # Format email content
            subject = template['subject'].format(**template_vars)
            body = template['body'].format(**template_vars)
            
            # Send email
            success = self._send_email(candidate_email, subject, body)
            
            # Log the result
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'candidate_name': candidate_name,
                'candidate_email': candidate_email,
                'job_title': job_title,
                'template_type': template_type,
                'success': success,
                'subject': subject
            }
            self.email_log.append(log_entry)
            
            if success:
                print(f"✅ Email sent successfully to {candidate_name}")
            else:
                print(f"❌ Failed to send email to {candidate_name}")
                
            return success
            
        except Exception as e:
            logger.error(f"Error sending manual email: {e}")
            print(f"❌ Error sending email: {e}")
            return False
    
    def send_bulk_emails_to_job_candidates(self, shortlists: Dict[str, List[Dict[str, Any]]], 
                                         job_title: str, selected_candidates: List[str] = None,
                                         template_type: str = "recruitment_interest") -> Dict[str, Any]:
        """
        Send emails to multiple candidates for a specific job
        
        Args:
            shortlists: Complete shortlists data
            job_title: Job title to send emails for
            selected_candidates: List of candidate names to send emails to (optional)
            template_type: Email template to use
            
        Returns:
            Results dictionary
        """
        if job_title not in shortlists:
            return {'error': f'Job title "{job_title}" not found in shortlists'}
        
        candidates = shortlists[job_title]
        results = {
            'total_candidates': 0,
            'emails_sent': 0,
            'emails_failed': 0,
            'sent_to': [],
            'failed_to': [],
            'job_title': job_title
        }
        
        print(f"\n📧 BULK EMAIL SENDING FOR: {job_title}")
        print("="*60)
        
        for candidate_match in candidates:
            candidate = candidate_match.get('candidate', {})
            candidate_name = candidate.get('full_name', 'Unknown')
            candidate_email = candidate.get('email', '').strip()
            
            # Skip if specific candidates selected and this one is not included
            if selected_candidates and candidate_name not in selected_candidates:
                continue
            
            results['total_candidates'] += 1
            
            # Skip if no email
            if not candidate_email or candidate_email.lower() in ['', 'not available', 'n/a']:
                print(f"⚠️  No email for {candidate_name}")
                results['emails_failed'] += 1
                results['failed_to'].append({
                    'name': candidate_name,
                    'reason': 'No email address'
                })
                continue
            
            # Send email
            success = self.send_manual_email(candidate_name, candidate_email, job_title, template_type)
            
            if success:
                results['emails_sent'] += 1
                results['sent_to'].append({
                    'name': candidate_name,
                    'email': candidate_email
                })
            else:
                results['emails_failed'] += 1
                results['failed_to'].append({
                    'name': candidate_name,
                    'email': candidate_email,
                    'reason': 'SMTP error'
                })
        
        # Print summary
        print(f"\n📊 BULK EMAIL SUMMARY:")
        print(f"   Total processed: {results['total_candidates']}")
        print(f"   Emails sent: {results['emails_sent']}")
        print(f"   Emails failed: {results['emails_failed']}")
        print("="*60)
        
        return results
    
    def _send_email(self, to_email: str, subject: str, body: str) -> bool:
        """Send a single email using SMTP"""
        try:
            # Create message
            message = MIMEMultipart()
            message["From"] = self.config.SMTP_USERNAME
            message["To"] = to_email
            message["Subject"] = subject
            
            # Add body to email
            message.attach(MIMEText(body, "plain"))
            
            # Create SMTP session
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.config.SMTP_SERVER, self.config.SMTP_PORT) as server:
                server.starttls(context=context)  # Enable security
                server.login(self.config.SMTP_USERNAME, self.config.SMTP_PASSWORD)
                text = message.as_string()
                server.sendmail(self.config.SMTP_USERNAME, to_email, text)
            
            return True
            
        except Exception as e:
            logger.error(f"SMTP Error: {e}")
            return False
    
    def preview_email(self, candidate_name: str, job_title: str, 
                     template_type: str = "recruitment_interest") -> str:
        """Preview email content before sending"""
        try:
            template = get_email_template(template_type)
            
            template_vars = {
                'candidate_name': candidate_name,
                'job_title': job_title,
                'company_name': self.config.COMPANY_NAME,
                'company_website': self.config.COMPANY_WEBSITE,
                'sender_name': self.config.SENDER_NAME,
                'hr_contact_name': self.config.HR_CONTACT_NAME,
                'hr_contact_email': self.config.HR_CONTACT_EMAIL,
                'hr_contact_phone': self.config.HR_CONTACT_PHONE,
                'experience_years': '3+',
                'skills': 'Technical Skills'
            }
            
            subject = template['subject'].format(**template_vars)
            body = template['body'].format(**template_vars)
            
            preview = f"""
=== EMAIL PREVIEW ===
To: {candidate_name}
Subject: {subject}

{body}
=== END PREVIEW ===
            """.strip()
            
            return preview
            
        except Exception as e:
            return f"Error generating preview: {e}"
    
    def get_job_candidates(self, shortlists_file: str = "shortlists.json") -> Dict[str, List[Dict[str, Any]]]:
        """Load job candidates from shortlists file"""
        try:
            with open(shortlists_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Shortlists file not found: {shortlists_file}")
            return {}
        except Exception as e:
            logger.error(f"Error loading shortlists: {e}")
            return {}
    
    def save_email_log(self, filename: str = None):
        """Save email log to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"email_log_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.email_log, f, indent=2, ensure_ascii=False)
            print(f"📄 Email log saved to: {filename}")
        except Exception as e:
            logger.error(f"Failed to save email log: {e}")

class ManualEmailInterface:
    """Command-line interface for manual email sending"""
    
    def __init__(self):
        self.email_manager = EnhancedEmailManager()
    
    def interactive_email_sending(self):
        """Interactive interface for sending emails"""
        print("\n🎯 MANUAL EMAIL SENDING INTERFACE")
        print("="*50)
        
        # Load shortlists
        shortlists = self.email_manager.get_job_candidates()
        
        if not shortlists:
            print("❌ No shortlists found. Please generate shortlists first.")
            return
        
        while True:
            print(f"\n📋 Available Options:")
            print("1. 📧 Send email to specific candidate")
            print("2. 📨 Send bulk emails to job candidates")
            print("3. 👁️  Preview email template")
            print("4. 📊 View available jobs")
            print("5. 💾 Save email log")
            print("0. ❌ Exit")
            
            choice = input("\n🤔 Choose an option (0-5): ").strip()
            
            if choice == "0":
                print("👋 Goodbye!")
                break
            elif choice == "1":
                self._send_single_email_interface(shortlists)
            elif choice == "2":
                self._send_bulk_emails_interface(shortlists)
            elif choice == "3":
                self._preview_email_interface()
            elif choice == "4":
                self._show_available_jobs(shortlists)
            elif choice == "5":
                self.email_manager.save_email_log()
            else:
                print("❌ Invalid option. Please try again.")
    
    def _send_single_email_interface(self, shortlists: Dict[str, List[Dict[str, Any]]]):
        """Interface for sending single email"""
        try:
            # Show available jobs
            self._show_available_jobs(shortlists)
            
            job_title = input("\n📋 Enter job title: ").strip()
            if job_title not in shortlists:
                print("❌ Job title not found")
                return
            
            # Show candidates for the job
            candidates = shortlists[job_title]
            print(f"\n👥 Candidates for {job_title}:")
            for i, candidate_match in enumerate(candidates, 1):
                candidate = candidate_match['candidate']
                print(f"  {i}. {candidate['full_name']} ({candidate.get('email', 'No email')})")
            
            candidate_choice = input(f"\nSelect candidate (1-{len(candidates)}): ").strip()
            try:
                candidate_idx = int(candidate_choice) - 1
                if 0 <= candidate_idx < len(candidates):
                    selected_candidate = candidates[candidate_idx]['candidate']
                    candidate_name = selected_candidate['full_name']
                    candidate_email = selected_candidate.get('email', '').strip()
                    
                    if not candidate_email:
                        print("❌ No email address for this candidate")
                        return
                    
                    # Show template options
                    templates = get_available_templates()
                    print(f"\n📝 Available templates:")
                    for i, template in enumerate(templates, 1):
                        print(f"  {i}. {template}")
                    
                    template_choice = input(f"Select template (1-{len(templates)}): ").strip()
                    template_idx = int(template_choice) - 1
                    
                    if 0 <= template_idx < len(templates):
                        template_type = templates[template_idx]
                        
                        # Confirm before sending
                        print(f"\n📧 Ready to send email:")
                        print(f"   To: {candidate_name} ({candidate_email})")
                        print(f"   Job: {job_title}")
                        print(f"   Template: {template_type}")
                        
                        confirm = input("\nConfirm sending? (y/n): ").strip().lower()
                        if confirm == 'y':
                            success = self.email_manager.send_manual_email(
                                candidate_name, candidate_email, job_title, template_type
                            )
                            if success:
                                print("✅ Email sent successfully!")
                            else:
                                print("❌ Failed to send email")
                        else:
                            print("📧 Email sending cancelled")
                    else:
                        print("❌ Invalid template selection")
                else:
                    print("❌ Invalid candidate selection")
            except ValueError:
                print("❌ Invalid input")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def _send_bulk_emails_interface(self, shortlists: Dict[str, List[Dict[str, Any]]]):
        """Interface for sending bulk emails"""
        try:
            self._show_available_jobs(shortlists)
            
            job_title = input("\n📋 Enter job title: ").strip()
            if job_title not in shortlists:
                print("❌ Job title not found")
                return
            
            # Show candidates
            candidates = shortlists[job_title]
            print(f"\n👥 Candidates for {job_title}:")
            for i, candidate_match in enumerate(candidates, 1):
                candidate = candidate_match['candidate']
                email_status = "✅" if candidate.get('email', '').strip() else "❌"
                print(f"  {i}. {candidate['full_name']} - {email_status} {candidate.get('email', 'No email')}")
            
            send_all = input(f"\nSend to all candidates with emails? (y/n): ").strip().lower()
            
            if send_all == 'y':
                # Show template options
                templates = get_available_templates()
                print(f"\n📝 Available templates:")
                for i, template in enumerate(templates, 1):
                    print(f"  {i}. {template}")
                
                template_choice = input(f"Select template (1-{len(templates)}): ").strip()
                template_idx = int(template_choice) - 1
                
                if 0 <= template_idx < len(templates):
                    template_type = templates[template_idx]
                    
                    confirm = input(f"\nConfirm bulk email sending for {job_title}? (y/n): ").strip().lower()
                    if confirm == 'y':
                        results = self.email_manager.send_bulk_emails_to_job_candidates(
                            shortlists, job_title, None, template_type
                        )
                        print(f"✅ Bulk email process completed!")
                    else:
                        print("📧 Bulk email sending cancelled")
                else:
                    print("❌ Invalid template selection")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def _preview_email_interface(self):
        """Interface for previewing emails"""
        candidate_name = input("👤 Enter candidate name: ").strip()
        job_title = input("📋 Enter job title: ").strip()
        
        templates = get_available_templates()
        print(f"\n📝 Available templates:")
        for i, template in enumerate(templates, 1):
            print(f"  {i}. {template}")
        
        try:
            template_choice = input(f"Select template (1-{len(templates)}): ").strip()
            template_idx = int(template_choice) - 1
            
            if 0 <= template_idx < len(templates):
                template_type = templates[template_idx]
                preview = self.email_manager.preview_email(candidate_name, job_title, template_type)
                print(f"\n{preview}")
            else:
                print("❌ Invalid template selection")
        except ValueError:
            print("❌ Invalid input")
    
    def _show_available_jobs(self, shortlists: Dict[str, List[Dict[str, Any]]]):
        """Show available job titles and candidate counts"""
        print(f"\n📋 Available Jobs:")
        for job_title, candidates in shortlists.items():
            email_count = sum(1 for c in candidates if c['candidate'].get('email', '').strip())
            print(f"   📊 {job_title}: {len(candidates)} candidates ({email_count} with emails)")

def main():
    """Main function for testing the enhanced email system"""
    interface = ManualEmailInterface()
    interface.interactive_email_sending()

if __name__ == "__main__":
    main()
