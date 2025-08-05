#!/usr/bin/env python3
"""
School Generator Script

This script generates new school folders using the _template folder as a base.
It takes school folder name, school full name, and RMP code as input and creates
all necessary files with the appropriate imports and configurations.

Usage:
    python school_generator.py

The script will prompt you for the required information interactively.
"""

import os
import sys
import shutil
from pathlib import Path

def main():
    print("🏫 School Generator Script")
    print("=" * 50)
    print()
    
    # Get inputs interactively
    school_folder_name = get_school_folder_name()
    school_full_name = get_school_full_name()
    rmp_code = get_rmp_code()
    
    # Confirm the inputs
    print("\n📋 Summary:")
    print(f"  School Folder Name: {school_folder_name}")
    print(f"  School Full Name: {school_full_name}")
    print(f"  RMP Code: {rmp_code}")
    print()
    
    if not confirm_creation():
        print("❌ Cancelled by user.")
        return
    
    # Get the current directory (should be the schools directory)
    current_dir = Path(__file__).parent
    template_dir = current_dir / "_template"
    target_dir = current_dir / school_folder_name
    
    # Check if template exists
    if not template_dir.exists():
        print(f"❌ Error: Template directory not found at {template_dir}")
        sys.exit(1)
    
    # Check if target directory already exists
    if target_dir.exists():
        print(f"❌ Error: School directory '{school_folder_name}' already exists at {target_dir}")
        sys.exit(1)
    
    try:
        print(f"\n📁 Creating school directory: {school_folder_name}")

        # Create the new school directory
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy all files from template
        for file_path in template_dir.iterdir():
            if file_path.is_file():
                shutil.copy2(file_path, target_dir)
        
        # Update school_config.py
        update_school_config(target_dir, school_full_name, rmp_code)
        # Update main.py imports
        update_main_imports(target_dir, school_folder_name)
        # Update terms.py imports
        update_terms_imports(target_dir, school_folder_name)
        # Update courses.py imports
        update_courses_imports(target_dir, school_folder_name)
        # Update schedules.py imports
        update_schedules_imports(target_dir, school_folder_name)
        # Update departments.py imports
        update_departments_imports(target_dir, school_folder_name)
        
        print(f"\n✅ Successfully created school folder: {school_folder_name}")
        print(f"\n📝 Next steps:")
        print(f"1. Update {school_folder_name}/school_config.py with the URLs")
        print(f"2. Implement the TODO functions in the Python files")
        
    except Exception as e:
        print(f"❌ Error creating school folder: {e}")
        # Clean up if there was an error
        if target_dir.exists():
            shutil.rmtree(target_dir)
        sys.exit(1)

def get_school_folder_name():
    """Get the school folder name from user input."""
    while True:
        folder_name = input("Enter school folder name (Ex. sjcc): ").strip()
        
        if not folder_name:
            print("❌ School folder name cannot be empty. Please try again.")
            continue
        
        # Validate school folder name (should be lowercase with underscores)
        if not folder_name.replace('_', '').replace('-', '').isalnum():
            print("❌ School folder name should contain only letters, numbers, underscores, and hyphens.")
            continue
        
        return folder_name

def get_school_full_name():
    """Get the school full name from user input."""
    while True:
        full_name = input("Enter school full name (Ex. 'San Jose City College'): ").strip()
        
        if not full_name:
            print("❌ School full name cannot be empty. Please try again.")
            continue
        
        return full_name

def get_rmp_code():
    """Get the RMP code from user input."""
    while True:
        rmp_code = input("Enter RateMyProfessors school code: ").strip()
        
        if not rmp_code:
            print("❌ RMP code cannot be empty. Please try again.")
            continue
        
        # Validate that it's a number
        if not rmp_code.isdigit():
            print("❌ RMP code should be a number. Please try again.")
            continue
        
        return rmp_code

def confirm_creation():
    """Ask user to confirm the creation."""
    while True:
        response = input("Proceed with creating the school folder? (y/n): ").strip().lower()
        
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print("Please enter 'y' or 'n'.")

def update_school_config(target_dir, school_full_name, rmp_code):
    """Update school_config.py with school information."""
    config_file = target_dir / "school_config.py"
    
    with open(config_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace the placeholders
    content = content.replace('SCHOOL_NAME = ""', 
                             f'SCHOOL_NAME = "{school_full_name}"')
    content = content.replace('RMP_CODE = ""', 
                             f'RMP_CODE = "{rmp_code}"')
    
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(content)

def update_main_imports(target_dir, school_folder_name):
    """Update main.py import statements."""
    main_file = target_dir / "main.py"
    
    with open(main_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace template imports with school-specific imports
    content = content.replace('from data_fetchers.schools.template.terms import get_terms',
                             f'from data_fetchers.schools.{school_folder_name}.terms import get_terms')
    content = content.replace('from data_fetchers.schools.template.courses import get_courses_per_department',
                             f'from data_fetchers.schools.{school_folder_name}.courses import get_courses_per_department')
    content = content.replace('from data_fetchers.schools.template.schedules import get_classes_per_department',
                             f'from data_fetchers.schools.{school_folder_name}.schedules import get_classes_per_department')
    content = content.replace('from data_fetchers.schools.template.departments import get_department_data_table',
                             f'from data_fetchers.schools.{school_folder_name}.departments import get_department_data_table')
    content = content.replace('from data_fetchers.schools.template.school_config import TERMS_BASE_URL, SCHEDULES_BASE_URL, SCHOOL_NAME, RMP_CODE',
                             f'from data_fetchers.schools.{school_folder_name}.school_config import TERMS_BASE_URL, SCHEDULES_BASE_URL, SCHOOL_NAME, RMP_CODE')
    
    with open(main_file, 'w', encoding='utf-8') as f:
        f.write(content)

def update_terms_imports(target_dir, school_folder_name):
    """Update terms.py import statements."""
    terms_file = target_dir / "terms.py"
    
    with open(terms_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace the school_config import
    content = content.replace('from school_config import SCHOOL_NAME',
                             f'from data_fetchers.schools.{school_folder_name}.school_config import SCHOOL_NAME')
    
    with open(terms_file, 'w', encoding='utf-8') as f:
        f.write(content)

def update_courses_imports(target_dir, school_folder_name):
    """Update courses.py import statements."""
    courses_file = target_dir / "courses.py"
    
    with open(courses_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add any school-specific imports if needed
    # For now, just ensure the file is properly formatted
    
    with open(courses_file, 'w', encoding='utf-8') as f:
        f.write(content)

def update_schedules_imports(target_dir, school_folder_name):
    """Update schedules.py import statements."""
    schedules_file = target_dir / "schedules.py"
    
    with open(schedules_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add any school-specific imports if needed
    # For now, just ensure the file is properly formatted
    
    with open(schedules_file, 'w', encoding='utf-8') as f:
        f.write(content)

def update_departments_imports(target_dir, school_folder_name):
    """Update departments.py import statements."""
    departments_file = target_dir / "departments.py"
    
    with open(departments_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add any school-specific imports if needed
    # For now, just ensure the file is properly formatted
    
    with open(departments_file, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    main() 