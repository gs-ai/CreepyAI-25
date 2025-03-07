#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Debug and manually apply AI-suggested code changes
"""

import os
import sys
import re
import difflib
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def parse_report_file(report_file):
    """Parse the report file to extract file paths and recommendations."""
    try:
        with open(report_file, 'r', errors='ignore') as f:
            content = f.read()
        
        # Split by file recommendation sections
        sections = re.split(r'=== Recommendations for (.*?) ===', content)
        
        file_recommendations = {}
        for i in range(1, len(sections), 2):
            if i+1 < len(sections):
                file_path = sections[i].strip()
                recommendations = sections[i+1].strip()
                file_recommendations[file_path] = recommendations
        
        return file_recommendations
    
    except Exception as e:
        logging.error(f"Error parsing report file: {e}")
        return {}

def extract_code_changes(recommendations):
    """Extract code changes from recommendations."""
    changes = []
    if "CODE CHANGES:" in recommendations:
        parts = recommendations.split("CODE CHANGES:")
        for part in parts[1:]:
            changes.append(part.split("ISSUE:")[0] if "ISSUE:" in part else part)
    return changes

def display_code_blocks(change_text):
    """Display code blocks from change text."""
    code_blocks = re.findall(r'```(?:python)?\n(.*?)\n```', change_text, re.DOTALL)
    print(f"Found {len(code_blocks)} code blocks:")
    for i, block in enumerate(code_blocks):
        print(f"\n--- Code Block {i+1} ---")
        print(block.strip())
    
    return code_blocks

def apply_manual_change(file_path, original_content, code_blocks):
    """Apply manual changes based on user input."""
    if len(code_blocks) < 1:
        print("No code blocks found to apply.")
        return original_content, False

    print("\nOptions:")
    print("1. Replace specific text")
    print("2. Replace lines")
    print("3. Insert at position")
    print("4. Use a diff-like approach")
    
    choice = input("Choose option (1-4): ").strip()
    
    modified_content = original_content
    
    if choice == "1":
        # Text replacement
        search_text = input("Enter text to replace: ").strip()
        replace_idx = int(input(f"Enter code block number to use as replacement (1-{len(code_blocks)}): ")) - 1
        
        if 0 <= replace_idx < len(code_blocks):
            replacement = code_blocks[replace_idx].strip()
            modified_content = original_content.replace(search_text, replacement)
            return modified_content, True
    
    elif choice == "2":
        # Line replacement
        start_line = int(input("Enter start line number: ")) - 1  # Convert to 0-indexed
        end_line = int(input("Enter end line number: "))
        replace_idx = int(input(f"Enter code block number to use as replacement (1-{len(code_blocks)}): ")) - 1
        
        if 0 <= replace_idx < len(code_blocks) and 0 <= start_line < end_line:
            lines = original_content.splitlines()
            replacement_lines = code_blocks[replace_idx].strip().splitlines()
            
            if start_line >= 0 and end_line <= len(lines):
                new_lines = lines[:start_line] + replacement_lines + lines[end_line:]
                modified_content = "\n".join(new_lines)
                return modified_content, True
    
    elif choice == "3":
        # Insert at position
        position = int(input("Enter line number to insert after: "))
        insert_idx = int(input(f"Enter code block number to insert (1-{len(code_blocks)}): ")) - 1
        
        if 0 <= insert_idx < len(code_blocks):
            lines = original_content.splitlines()
            insertion = code_blocks[insert_idx].strip()
            
            if 0 <= position <= len(lines):
                new_lines = lines[:position] + [insertion] + lines[position:]
                modified_content = "\n".join(new_lines)
                return modified_content, True
    
    elif choice == "4":
        # Diff-like approach
        if len(code_blocks) >= 2:
            old_code = code_blocks[0].strip()
            new_code = code_blocks[1].strip()
            
            print("\nAttempting diff replacement...")
            
            # Find best match for the old code in the file
            matcher = difflib.SequenceMatcher(None, original_content, old_code)
            match = matcher.find_longest_match(0, len(original_content), 0, len(old_code))
            
            if match.size > len(old_code) * 0.7:  # If we found at least 70% match
                before_match = original_content[:match.a]
                after_match = original_content[match.a + match.size:]
                modified_content = before_match + new_code + after_match
                
                print(f"Found match of size {match.size} at position {match.a}")
                print("Preview of the change:")
                print("-" * 40)
                preview_start = max(0, match.a - 100)
                preview_end = min(len(original_content), match.a + match.size + 100)
                print(f"...{original_content[preview_start:preview_end]}...")
                
                confirm = input("Apply this change? (y/n): ").lower()
                if confirm == 'y':
                    return modified_content, True
            else:
                print(f"No good match found. Best match size: {match.size}")
    
    return original_content, False

def main():
    if len(sys.argv) < 2:
        print("Usage: debug_changes.py <report_file_path>")
        print("Example: debug_changes.py /path/to/ollama_file_analysis.txt")
        return
    
    report_file = sys.argv[1]
    if not os.path.exists(report_file):
        print(f"Report file not found: {report_file}")
        return
    
    # Parse the report file
    file_recommendations = parse_report_file(report_file)
    
    if not file_recommendations:
        print("No file recommendations found in the report.")
        return
    
    print(f"Found recommendations for {len(file_recommendations)} files.")
    
    # List files with recommendations
    for i, file_path in enumerate(file_recommendations.keys()):
        print(f"{i+1}. {file_path}")
    
    # Choose a file to work with
    file_idx = int(input("\nEnter the number of the file to process: ")) - 1
    if not (0 <= file_idx < len(file_recommendations)):
        print("Invalid selection.")
        return
    
    file_path = list(file_recommendations.keys())[file_idx]
    recommendations = file_recommendations[file_path]
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
    
    # Extract code changes
    code_changes = extract_code_changes(recommendations)
    
    if not code_changes:
        print("No code changes found in the recommendations.")
        return
    
    print(f"\nFound {len(code_changes)} code change sections.")
    
    # Choose a change to work with
    for i, change in enumerate(code_changes):
        preview = change[:100].replace('\n', ' ') + '...'
        print(f"{i+1}. {preview}")
    
    change_idx = int(input("\nEnter the number of the change to process: ")) - 1
    if not (0 <= change_idx < len(code_changes)):
        print("Invalid selection.")
        return
    
    selected_change = code_changes[change_idx]
    
    # Display code blocks
    code_blocks = display_code_blocks(selected_change)
    
    # Read the original file
    with open(file_path, 'r', errors='ignore') as f:
        original_content = f.read()
    
    # Create a backup
    backup_file = f"{file_path}.debug_backup"
    with open(backup_file, 'w', errors='ignore') as f:
        f.write(original_content)
    print(f"\nCreated backup at {backup_file}")
    
    # Apply manual change
    modified_content, changed = apply_manual_change(file_path, original_content, code_blocks)
    
    if changed:
        # Write the changes back to the file
        with open(file_path, 'w') as f:
            f.write(modified_content)
        print(f"\n✅ Applied changes to {file_path}")
    else:
        print("\nNo changes applied.")

if __name__ == "__main__":
    main()
