#!/usr/bin/env python3
"""
Moodle to GitHub Classroom Roster Sync
CSC3301 Programming Language Paradigms

This script fetches enrolled students from Moodle and exports them
to a CSV format compatible with GitHub Classroom roster import.

Usage:
    python moodle_to_github_roster.py --moodle-token TOKEN --course-id ID
    python moodle_to_github_roster.py --config config.json

Environment variables (alternative to command line):
    MOODLE_TOKEN: Moodle API token
    MOODLE_URL: Moodle instance URL (default: https://moodle.unza.zm)
    GITHUB_TOKEN: GitHub token (for direct roster update)
"""

import argparse
import csv
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
from urllib.parse import urlencode

try:
    import requests
except ImportError:
    print("Error: 'requests' library required. Install with: pip install requests")
    sys.exit(1)


# Default configuration
DEFAULT_MOODLE_URL = "https://moodle.unza.zm"
DEFAULT_OUTPUT_FILE = "github_classroom_roster.csv"


class MoodleAPI:
    """Moodle REST API client."""
    
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.endpoint = f"{self.base_url}/webservice/rest/server.php"
    
    def call(self, function: str, **params) -> dict:
        """
        Call a Moodle web service function.
        
        Args:
            function: Moodle web service function name
            **params: Function parameters
            
        Returns:
            JSON response as dictionary
        """
        data = {
            'wstoken': self.token,
            'wsfunction': function,
            'moodlewsrestformat': 'json',
            **params
        }
        
        try:
            response = requests.post(self.endpoint, data=data, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            # Check for Moodle error response
            if isinstance(result, dict) and 'exception' in result:
                raise Exception(f"Moodle API Error: {result.get('message', 'Unknown error')}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {e}")
    
    def get_courses(self) -> list:
        """Get list of courses the token has access to."""
        return self.call('core_course_get_courses')
    
    def search_courses(self, search_term: str) -> list:
        """Search for courses by name."""
        result = self.call('core_course_search_courses', criterianame='search', criteriavalue=search_term)
        return result.get('courses', [])
    
    def get_enrolled_users(self, course_id: int) -> list:
        """
        Get all enrolled users for a course.
        
        Args:
            course_id: Moodle course ID
            
        Returns:
            List of user dictionaries
        """
        return self.call('core_enrol_get_enrolled_users', courseid=course_id)
    
    def get_course_by_shortname(self, shortname: str) -> Optional[dict]:
        """Find a course by its shortname."""
        courses = self.call('core_course_get_courses_by_field', field='shortname', value=shortname)
        if courses.get('courses'):
            return courses['courses'][0]
        return None


class GitHubClassroomAPI:
    """GitHub Classroom API client."""
    
    def __init__(self, token: str):
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
    
    def get_classrooms(self) -> list:
        """Get list of classrooms."""
        # Note: GitHub Classroom API has limited public documentation
        # This uses the available endpoints
        response = requests.get(
            f"{self.base_url}/classrooms",
            headers=self.headers,
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        return []
    
    def get_classroom_roster(self, classroom_id: int) -> list:
        """Get roster for a classroom."""
        response = requests.get(
            f"{self.base_url}/classrooms/{classroom_id}/roster",
            headers=self.headers,
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        return []


def extract_student_id(email: str, username: str, custom_fields: dict) -> str:
    """
    Extract student ID from various sources.
    
    Priority:
    1. Custom profile field 'studentid' or 'idnumber'
    2. Username if it looks like a student ID
    3. Email prefix
    """
    # Check custom fields
    if custom_fields:
        for field in ['studentid', 'idnumber', 'student_id']:
            if field in custom_fields and custom_fields[field]:
                return custom_fields[field]
    
    # Check if username looks like a student ID (numeric or alphanumeric pattern)
    if username and re.match(r'^[0-9]{6,10}$', username):
        return username
    
    # Fall back to email prefix
    if email:
        return email.split('@')[0]
    
    return username or 'unknown'


def normalize_name(firstname: str, lastname: str) -> str:
    """Normalize student name."""
    parts = []
    if firstname:
        parts.append(firstname.strip())
    if lastname:
        parts.append(lastname.strip())
    return ' '.join(parts) or 'Unknown'


def filter_students(users: list, exclude_roles: list = None) -> list:
    """
    Filter users to only include students.
    
    Args:
        users: List of Moodle user dictionaries
        exclude_roles: Role shortnames to exclude (default: ['teacher', 'editingteacher', 'manager'])
    """
    if exclude_roles is None:
        exclude_roles = ['teacher', 'editingteacher', 'manager', 'coursecreator', 'admin']
    
    students = []
    for user in users:
        # Check roles
        roles = user.get('roles', [])
        role_shortnames = [r.get('shortname', '') for r in roles]
        
        # Skip if user has an excluded role
        if any(role in exclude_roles for role in role_shortnames):
            continue
        
        # Skip if user is suspended
        if user.get('suspended', False):
            continue
        
        students.append(user)
    
    return students


def process_custom_fields(user: dict) -> dict:
    """Extract custom profile fields from user data."""
    custom = {}
    for field in user.get('customfields', []):
        shortname = field.get('shortname', field.get('name', '')).lower()
        value = field.get('value', '')
        if shortname and value:
            custom[shortname] = value
    return custom


def fetch_moodle_students(moodle: MoodleAPI, course_id: int = None, course_shortname: str = None) -> list:
    """
    Fetch students from Moodle course.
    
    Args:
        moodle: MoodleAPI instance
        course_id: Numeric course ID
        course_shortname: Course shortname (e.g., 'CSC3301')
        
    Returns:
        List of student dictionaries with normalized data
    """
    # Resolve course ID if shortname provided
    if course_shortname and not course_id:
        print(f"Looking up course by shortname: {course_shortname}")
        course = moodle.get_course_by_shortname(course_shortname)
        if course:
            course_id = course['id']
            print(f"Found course: {course.get('fullname', 'Unknown')} (ID: {course_id})")
        else:
            raise Exception(f"Course not found with shortname: {course_shortname}")
    
    if not course_id:
        raise Exception("Either course_id or course_shortname must be provided")
    
    # Fetch enrolled users
    print(f"Fetching enrolled users for course ID: {course_id}")
    users = moodle.get_enrolled_users(course_id)
    print(f"Found {len(users)} enrolled users")
    
    # Filter to students only
    students = filter_students(users)
    print(f"Filtered to {len(students)} students (excluding teachers/managers)")
    
    # Process and normalize student data
    processed = []
    for user in students:
        custom_fields = process_custom_fields(user)
        
        student = {
            'moodle_id': user.get('id'),
            'username': user.get('username', ''),
            'email': user.get('email', ''),
            'firstname': user.get('firstname', ''),
            'lastname': user.get('lastname', ''),
            'fullname': normalize_name(user.get('firstname'), user.get('lastname')),
            'student_id': extract_student_id(
                user.get('email', ''),
                user.get('username', ''),
                custom_fields
            ),
            'idnumber': user.get('idnumber', ''),
            'custom_fields': custom_fields
        }
        processed.append(student)
    
    return processed


def export_to_csv(students: list, output_file: str, identifier_field: str = 'email') -> str:
    """
    Export students to GitHub Classroom roster CSV format.
    
    GitHub Classroom expects columns:
    - identifier: unique identifier (email or student ID)
    - github_username: GitHub username (optional, students can link later)
    - name: display name
    
    Args:
        students: List of student dictionaries
        output_file: Output CSV file path
        identifier_field: Field to use as identifier ('email', 'student_id', 'username')
        
    Returns:
        Path to created CSV file
    """
    output_path = Path(output_file)
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # GitHub Classroom expected headers
        writer.writerow(['identifier', 'github_username', 'name'])
        
        for student in students:
            # Determine identifier based on preference
            if identifier_field == 'email':
                identifier = student['email']
            elif identifier_field == 'student_id':
                identifier = student['student_id']
            elif identifier_field == 'username':
                identifier = student['username']
            else:
                identifier = student['email'] or student['student_id']
            
            # GitHub username left empty - students will link their accounts
            github_username = ''
            
            # Full name
            name = student['fullname']
            
            writer.writerow([identifier, github_username, name])
    
    print(f"Exported {len(students)} students to: {output_path}")
    return str(output_path)


def export_full_details(students: list, output_file: str) -> str:
    """
    Export full student details to CSV for reference.
    """
    output_path = Path(output_file)
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'moodle_id', 'username', 'email', 'firstname', 'lastname',
            'fullname', 'student_id', 'idnumber'
        ])
        
        for student in students:
            writer.writerow([
                student['moodle_id'],
                student['username'],
                student['email'],
                student['firstname'],
                student['lastname'],
                student['fullname'],
                student['student_id'],
                student['idnumber']
            ])
    
    print(f"Exported full details to: {output_path}")
    return str(output_path)


def load_config(config_file: str) -> dict:
    """Load configuration from JSON file."""
    with open(config_file) as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(
        description='Sync Moodle course roster to GitHub Classroom format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Using command line arguments
  python moodle_to_github_roster.py --moodle-token TOKEN --course-id 123
  
  # Using course shortname
  python moodle_to_github_roster.py --moodle-token TOKEN --course-shortname CSC3301
  
  # Using config file
  python moodle_to_github_roster.py --config config.json
  
  # Using environment variables
  export MOODLE_TOKEN=your_token
  python moodle_to_github_roster.py --course-shortname CSC3301
        """
    )
    
    parser.add_argument('--config', '-c', help='Path to JSON config file')
    parser.add_argument('--moodle-url', default=DEFAULT_MOODLE_URL,
                        help=f'Moodle instance URL (default: {DEFAULT_MOODLE_URL})')
    parser.add_argument('--moodle-token', help='Moodle API token (or set MOODLE_TOKEN env var)')
    parser.add_argument('--course-id', type=int, help='Moodle course ID')
    parser.add_argument('--course-shortname', help='Moodle course shortname (e.g., CSC3301)')
    parser.add_argument('--output', '-o', default=DEFAULT_OUTPUT_FILE,
                        help=f'Output CSV file (default: {DEFAULT_OUTPUT_FILE})')
    parser.add_argument('--identifier', choices=['email', 'student_id', 'username'],
                        default='email', help='Field to use as identifier (default: email)')
    parser.add_argument('--full-export', action='store_true',
                        help='Also export full student details to separate CSV')
    parser.add_argument('--list-courses', action='store_true',
                        help='List available courses and exit')
    parser.add_argument('--search-course', help='Search for courses by name')
    parser.add_argument('--dry-run', action='store_true',
                        help='Fetch data but do not write files')
    
    args = parser.parse_args()
    
    # Load config file if provided
    config = {}
    if args.config:
        config = load_config(args.config)
    
    # Resolve configuration (command line > config file > env vars)
    moodle_url = args.moodle_url or config.get('moodle_url') or os.environ.get('MOODLE_URL', DEFAULT_MOODLE_URL)
    moodle_token = args.moodle_token or config.get('moodle_token') or os.environ.get('MOODLE_TOKEN')
    course_id = args.course_id or config.get('course_id')
    course_shortname = args.course_shortname or config.get('course_shortname')
    
    # Validate required parameters
    if not moodle_token:
        print("Error: Moodle token required. Use --moodle-token, config file, or MOODLE_TOKEN env var")
        sys.exit(1)
    
    # Initialize Moodle API
    print(f"Connecting to Moodle: {moodle_url}")
    moodle = MoodleAPI(moodle_url, moodle_token)
    
    # Handle special commands
    if args.list_courses:
        print("\nAvailable courses:")
        courses = moodle.get_courses()
        for course in courses:
            print(f"  ID: {course['id']:5} | {course.get('shortname', 'N/A'):15} | {course.get('fullname', 'Unknown')}")
        return
    
    if args.search_course:
        print(f"\nSearching for courses matching: {args.search_course}")
        courses = moodle.search_courses(args.search_course)
        for course in courses:
            print(f"  ID: {course['id']:5} | {course.get('shortname', 'N/A'):15} | {course.get('fullname', 'Unknown')}")
        return
    
    # Validate course specification
    if not course_id and not course_shortname:
        print("Error: Either --course-id or --course-shortname must be provided")
        sys.exit(1)
    
    # Fetch students
    try:
        students = fetch_moodle_students(moodle, course_id, course_shortname)
    except Exception as e:
        print(f"Error fetching students: {e}")
        sys.exit(1)
    
    if not students:
        print("No students found in course")
        sys.exit(0)
    
    # Display summary
    print(f"\n{'='*50}")
    print(f"Found {len(students)} students")
    print(f"{'='*50}")
    print(f"{'Name':<30} {'Email':<35} {'Student ID'}")
    print(f"{'-'*30} {'-'*35} {'-'*15}")
    for s in students[:10]:  # Show first 10
        print(f"{s['fullname'][:30]:<30} {s['email'][:35]:<35} {s['student_id']}")
    if len(students) > 10:
        print(f"... and {len(students) - 10} more")
    print()
    
    # Export files
    if not args.dry_run:
        # Main roster file for GitHub Classroom
        export_to_csv(students, args.output, args.identifier)
        
        # Optional full export
        if args.full_export:
            full_output = args.output.replace('.csv', '_full.csv')
            export_full_details(students, full_output)
        
        print(f"\n✅ Export complete!")
        print(f"   Import {args.output} into GitHub Classroom:")
        print(f"   1. Go to https://classroom.github.com")
        print(f"   2. Select your classroom (CSC3301-2026)")
        print(f"   3. Go to 'Students' tab")
        print(f"   4. Click 'Import roster' and upload the CSV")
    else:
        print("\n[Dry run - no files written]")


if __name__ == "__main__":
    main()
