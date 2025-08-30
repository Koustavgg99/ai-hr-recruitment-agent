"""
Team Member Management Module
============================

This module provides functionality to manage team members and their LinkedIn profiles
for the AI HR Recruitment Agent system.

Features:
- Load team members from JSON file
- Update LinkedIn profiles
- Search team members by various criteria
- Generate team member reports
"""

import json
import os
from typing import List, Dict, Optional, Union
from datetime import datetime


class TeamManager:
    """Manages team members and their LinkedIn profiles."""
    
    def __init__(self, team_file_path: str = "team_members.json"):
        """
        Initialize the Team Manager.
        
        Args:
            team_file_path (str): Path to the team members JSON file
        """
        self.team_file_path = team_file_path
        self.team_members = []
        self.load_team_members()
    
    def load_team_members(self) -> None:
        """Load team members from the JSON file."""
        try:
            if os.path.exists(self.team_file_path):
                with open(self.team_file_path, 'r', encoding='utf-8') as file:
                    self.team_members = json.load(file)
                print(f"Loaded {len(self.team_members)} team members from {self.team_file_path}")
            else:
                print(f"Team file {self.team_file_path} not found. Starting with empty team.")
                self.team_members = []
        except json.JSONDecodeError as e:
            print(f"Error reading team file: {e}")
            self.team_members = []
        except Exception as e:
            print(f"Error loading team members: {e}")
            self.team_members = []
    
    def save_team_members(self) -> None:
        """Save team members to the JSON file."""
        try:
            with open(self.team_file_path, 'w', encoding='utf-8') as file:
                json.dump(self.team_members, file, indent=2, ensure_ascii=False)
            print(f"Saved {len(self.team_members)} team members to {self.team_file_path}")
        except Exception as e:
            print(f"Error saving team members: {e}")
    
    def get_all_team_members(self) -> List[Dict]:
        """
        Get all team members.
        
        Returns:
            List[Dict]: List of all team members
        """
        return self.team_members
    
    def get_team_member_by_id(self, member_id: int) -> Optional[Dict]:
        """
        Get a team member by their ID.
        
        Args:
            member_id (int): The member's ID
            
        Returns:
            Optional[Dict]: Team member data or None if not found
        """
        for member in self.team_members:
            if member.get('id') == member_id:
                return member
        return None
    
    def get_team_member_by_name(self, name: str) -> Optional[Dict]:
        """
        Get a team member by their full name.
        
        Args:
            name (str): The member's full name
            
        Returns:
            Optional[Dict]: Team member data or None if not found
        """
        for member in self.team_members:
            if member.get('full_name', '').lower() == name.lower():
                return member
        return None
    
    def update_linkedin_url(self, identifier: Union[int, str], linkedin_url: str) -> bool:
        """
        Update a team member's LinkedIn URL.
        
        Args:
            identifier (Union[int, str]): Member ID (int) or full name (str)
            linkedin_url (str): The LinkedIn profile URL
            
        Returns:
            bool: True if updated successfully, False otherwise
        """
        # Find the team member
        member = None
        if isinstance(identifier, int):
            member = self.get_team_member_by_id(identifier)
        elif isinstance(identifier, str):
            member = self.get_team_member_by_name(identifier)
        
        if member:
            member['linkedin_url'] = linkedin_url
            member['updated_at'] = datetime.now().isoformat()
            self.save_team_members()
            print(f"Updated LinkedIn URL for {member['full_name']}")
            return True
        else:
            print(f"Team member not found: {identifier}")
            return False
    
    def get_members_without_linkedin(self) -> List[Dict]:
        """
        Get team members who don't have LinkedIn URLs.
        
        Returns:
            List[Dict]: List of team members without LinkedIn URLs
        """
        return [member for member in self.team_members 
                if not member.get('linkedin_url') or member.get('linkedin_url') is None]
    
    def get_members_with_linkedin(self) -> List[Dict]:
        """
        Get team members who have LinkedIn URLs.
        
        Returns:
            List[Dict]: List of team members with LinkedIn URLs
        """
        return [member for member in self.team_members 
                if member.get('linkedin_url') and member.get('linkedin_url') is not None]
    
    def generate_team_report(self) -> Dict:
        """
        Generate a comprehensive team report.
        
        Returns:
            Dict: Team statistics and information
        """
        total_members = len(self.team_members)
        members_with_linkedin = len(self.get_members_with_linkedin())
        members_without_linkedin = len(self.get_members_without_linkedin())
        
        active_members = len([m for m in self.team_members if m.get('status') == 'Active'])
        
        report = {
            'total_members': total_members,
            'active_members': active_members,
            'members_with_linkedin': members_with_linkedin,
            'members_without_linkedin': members_without_linkedin,
            'linkedin_completion_rate': f"{(members_with_linkedin/total_members*100):.1f}%" if total_members > 0 else "0%",
            'team_members': self.team_members
        }
        
        return report
    
    def search_members(self, query: str, field: str = 'all') -> List[Dict]:
        """
        Search team members by various criteria.
        
        Args:
            query (str): Search query
            field (str): Field to search in ('all', 'name', 'role', 'skills', 'department')
            
        Returns:
            List[Dict]: List of matching team members
        """
        query = query.lower()
        results = []
        
        for member in self.team_members:
            if field == 'all':
                # Search in multiple fields
                searchable_text = f"{member.get('full_name', '')} {member.get('role', '')} {member.get('skills', '')} {member.get('department', '')}".lower()
                if query in searchable_text:
                    results.append(member)
            elif field == 'name' and query in member.get('full_name', '').lower():
                results.append(member)
            elif field == 'role' and query in member.get('role', '').lower():
                results.append(member)
            elif field == 'skills' and query in member.get('skills', '').lower():
                results.append(member)
            elif field == 'department' and query in member.get('department', '').lower():
                results.append(member)
        
        return results
    
    def display_team_members(self, members: List[Dict] = None) -> None:
        """
        Display team members in a formatted way.
        
        Args:
            members (List[Dict], optional): Specific members to display. If None, displays all.
        """
        if members is None:
            members = self.team_members
        
        if not members:
            print("No team members to display.")
            return
        
        print("\n" + "="*80)
        print("TEAM MEMBERS")
        print("="*80)
        
        for i, member in enumerate(members, 1):
            print(f"\n{i}. {member.get('full_name', 'Unknown')}")
            print(f"   ID: {member.get('id', 'N/A')}")
            print(f"   Role: {member.get('role', 'N/A')}")
            print(f"   Department: {member.get('department', 'N/A')}")
            print(f"   Email: {member.get('email', 'N/A')}")
            print(f"   Phone: {member.get('phone', 'N/A')}")
            print(f"   Status: {member.get('status', 'N/A')}")
            print(f"   Skills: {member.get('skills', 'N/A')}")
            
            linkedin_url = member.get('linkedin_url')
            if linkedin_url:
                print(f"   LinkedIn: {linkedin_url}")
            else:
                print("   LinkedIn: Not added yet")
            
            print(f"   Notes: {member.get('notes', 'N/A')}")
        
        print("\n" + "="*80)


def main():
    """
    Main function to demonstrate the TeamManager functionality.
    """
    # Initialize team manager
    team_manager = TeamManager()
    
    # Display all team members
    print("Current Team Members:")
    team_manager.display_team_members()
    
    # Generate and display team report
    report = team_manager.generate_team_report()
    print(f"\nTEAM REPORT")
    print(f"===========")
    print(f"Total Members: {report['total_members']}")
    print(f"Active Members: {report['active_members']}")
    print(f"Members with LinkedIn: {report['members_with_linkedin']}")
    print(f"Members without LinkedIn: {report['members_without_linkedin']}")
    print(f"LinkedIn Completion Rate: {report['linkedin_completion_rate']}")
    
    # Show members without LinkedIn
    members_without_linkedin = team_manager.get_members_without_linkedin()
    if members_without_linkedin:
        print(f"\nMembers without LinkedIn profiles:")
        for member in members_without_linkedin:
            print(f"  - {member['full_name']} (ID: {member['id']})")


if __name__ == "__main__":
    main()
