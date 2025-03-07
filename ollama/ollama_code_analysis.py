import os
import hashlib
import difflib
import ollama
import logging
import shutil
import datetime
from concurrent.futures import ThreadPoolExecutor

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Default paths
DEFAULT_BASE_DIR = os.path.abspath("/Users/mbaosint/Desktop/Projects/CreepyAI")
BACKUP_DIR = None  # Will be set based on user input

# Ollama configuration
OLLAMA_MODEL = "qwen2.5-coder:7b"
MAX_ANALYSIS_SIZE = 5 * 1024 * 1024  # Skip AI analysis on files larger than 5MB
MAX_LINES = 1000  # AI analyzes only first 500 and last 200 lines of large files
NUM_THREADS = 4  # Number of concurrent AI requests

# File types to analyze
ANALYZABLE_EXTENSIONS = {".py"}  # Prioritize Python files only

def get_user_input():
    """Query the user for directory path and other settings."""
    print("\n=== CreepyAI Automatic Code Analyzer and Fixer ===")
    base_dir = input(f"Enter the directory path to analyze (default: {DEFAULT_BASE_DIR}): ").strip()
    if not base_dir:
        base_dir = DEFAULT_BASE_DIR
    
    base_dir = os.path.abspath(base_dir)
    if not os.path.exists(base_dir):
        raise ValueError(f"Directory '{base_dir}' does not exist!")
    
    # Create a backup directory
    global BACKUP_DIR
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    BACKUP_DIR = os.path.join(os.path.dirname(base_dir), f"{os.path.basename(base_dir)}_backup_{timestamp}")
    
    # Set up report file
    report_file = os.path.join(base_dir, "ollama_file_analysis.txt")
    
    # Exclude dir (typically the directory containing this script)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    return base_dir, script_dir, report_file

def create_backup(file_path):
    """Create a backup of a file before modifying it."""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    
    # Preserve the relative path structure
    rel_path = os.path.relpath(file_path, start=BASE_DIR)
    backup_file = os.path.join(BACKUP_DIR, rel_path)
    backup_dir = os.path.dirname(backup_file)
    
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    shutil.copy2(file_path, backup_file)
    logging.info(f"Created backup: {backup_file}")
    return backup_file

# Function to compute SHA256 hash of a file
def compute_hash(file_path):
    """Computes the SHA256 hash of a file."""
    hasher = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        logging.error(f"Error computing hash for {file_path}: {e}")
        return None

# Function to scan directory recursively and compute file hashes
def scan_files(base_dir, exclude_dir):
    """
    Scans the directory, computes hashes, and returns a dictionary where each hash maps to a list of file paths.
    """
    file_hashes = {}
    for root, _, files in os.walk(base_dir):
        # Skip the exclude directory and backup files
        if os.path.abspath(root).startswith(os.path.abspath(exclude_dir)):
            continue
        for file in files:
            if file.endswith(".import_backup") or "backup" in root.lower():
                continue  # Skip backup files and directories

            file_path = os.path.normpath(os.path.join(root, file))
            file_hash = compute_hash(file_path)
            if file_hash:
                file_hashes.setdefault(file_hash, []).append(file_path)
    return file_hashes

# Function to analyze differences between files in groups of identical hash
def analyze_differences(identical_files, report):
    """
    Compares duplicate files and uses AI to summarize key differences.
    """
    report.write("=== IDENTICAL FILES ===\n")
    for paths in identical_files.values():
        if len(paths) > 1:
            report.write("\n".join(paths) + "\n\n")

    report.write("=== FILE DIFFERENCES ANALYSIS ===\n")
    for file_list in identical_files.values():
        if len(file_list) == 1:
            continue  # Skip unique files

        ref_file = file_list[0]
        for file in file_list[1:]:
            if os.path.exists(ref_file) and os.path.exists(file):
                try:
                    with open(ref_file, "r", errors="ignore") as f1, open(file, "r", errors="ignore") as f2:
                        diff = difflib.unified_diff(f1.readlines(), f2.readlines(), fromfile=ref_file, tofile=file)
                        diff_text = "".join(diff)
                    if diff_text:
                        prompt = (
                            f"Analyze the differences between these two code files:\n{diff_text}\n"
                            "Summarize the key differences and note if any redundant sections should be deleted."
                        )
                        response = ollama.chat(model=OLLAMA_MODEL, messages=[{"role": "user", "content": prompt}])
                        analysis = response["message"]["content"]
                        report.write(f"Comparison: {ref_file} <--> {file}\n{analysis}\n\n")
                except Exception as e:
                    logging.error(f"Error comparing {ref_file} and {file}: {e}")
                    report.write(f"Error comparing {ref_file} and {file}: {e}\n\n")

# Function to analyze a single file and generate recommendations
def analyze_file_recommendations(file_path):
    """
    Sends file content to AI for analysis, suggesting redundant code to delete and improvements to make.
    """
    try:
        file_size = os.path.getsize(file_path)
        if file_size > MAX_ANALYSIS_SIZE:
            logging.info(f"Skipping {file_path} (size {file_size} bytes) for AI analysis.")
            return f"Skipping {file_path} due to size ({file_size} bytes).\n\n", None

        with open(file_path, "r", errors="ignore") as f:
            lines = f.readlines()

        if len(lines) > MAX_LINES:
            content = "".join(lines[:500]) + "\n...[content truncated]...\n" + "".join(lines[-200:])
        else:
            content = "".join(lines)

        prompt = (
            f"Analyze the following code from {file_path}:\n\n{content}\n\n"
            "Identify redundant code sections to remove, suggest improvements, and specify where functionality is missing. "
            "IMPORTANT: For each issue, provide the exact code modifications needed, including line numbers where possible. "
            "Format your response with 'ISSUE:', 'RECOMMENDATION:', and 'CODE CHANGES:' sections for each problem found."
        )
        response = ollama.chat(model=OLLAMA_MODEL, messages=[{"role": "user", "content": prompt}])
        analysis = response["message"]["content"]
        
        # Check if we have code modification suggestions
        has_changes = "CODE CHANGES:" in analysis
        
        return f"=== Recommendations for {file_path} ===\n{analysis}\n\n", has_changes

    except Exception as e:
        logging.error(f"Error analyzing {file_path}: {e}")
        return f"Error analyzing {file_path}: {e}\n\n", None

def implement_code_changes(file_path, analysis):
    """
    Implement the code changes suggested by AI.
    """
    if "CODE CHANGES:" not in analysis:
        logging.info(f"No specific code changes found for {file_path}")
        return False
    
    try:
        # Create backup before modifying
        create_backup(file_path)
        
        # Extract code change sections
        changes_sections = analysis.split("CODE CHANGES:")
        changes_to_make = changes_sections[1:] if len(changes_sections) > 1 else []
        
        if not changes_to_make:
            return False
        
        # Get current file content
        with open(file_path, 'r', errors='ignore') as f:
            file_content = f.read()
            original_lines = file_content.splitlines()
        
        modified_content = file_content
        changes_made = False
        
        import re
        
        # Implement each code change section
        for change_section in changes_to_make:
            # Try multiple approaches to apply changes
            
            # APPROACH 1: Look for line numbers in the change description
            line_pattern = re.compile(r'line[s]?\s+(\d+)(?:\s*-\s*|\s+to\s+|[-,]\s*)(\d+)', re.IGNORECASE)
            line_matches = line_pattern.findall(change_section)
            
            if line_matches:
                for start_str, end_str in line_matches:
                    try:
                        start_line = max(0, int(start_str) - 1)  # Convert to 0-indexed
                        end_line = min(len(original_lines), int(end_str))
                        
                        # Find code blocks (replacement text)
                        code_block_pattern = re.compile(r'```(?:python)?\n(.*?)\n```', re.DOTALL)
                        code_blocks = code_block_pattern.findall(change_section)
                        
                        if code_blocks and len(code_blocks) >= 1:
                            replacement = code_blocks[-1].strip()  # Use the last code block as replacement
                            
                            # Replace the lines
                            new_lines = original_lines[:start_line] + replacement.splitlines() + original_lines[end_line:]
                            modified_content = "\n".join(new_lines)
                            changes_made = True
                            logging.info(f"Applied line-based change to lines {start_line+1}-{end_line}")
                    except (ValueError, IndexError) as e:
                        logging.error(f"Error processing line numbers: {e}")
            
            # APPROACH 2: Look for before/after code blocks
            code_block_pattern = re.compile(r'```(?:python)?\n(.*?)\n```', re.DOTALL)
            code_blocks = code_block_pattern.findall(change_section)
            
            if len(code_blocks) >= 2 and not changes_made:
                try:
                    # First block is often the "before" code, second is "after" code
                    old_code = code_blocks[0].strip()
                    new_code = code_blocks[1].strip()
                    
                    if old_code and new_code and old_code in modified_content:
                        modified_content = modified_content.replace(old_code, new_code)
                        changes_made = True
                        logging.info(f"Applied block replacement change")
                except Exception as e:
                    logging.error(f"Error applying code block replacement: {e}")
            
            # APPROACH 3: Look for specific "Replace..." or "Change..." instructions with code
            if not changes_made and len(code_blocks) >= 1:
                replace_pattern = re.compile(r'(?:Replace|Change|Update|Modify)[:\s]+(.*?)(?:with|to)[:\s]+', re.IGNORECASE | re.DOTALL)
                replace_matches = replace_pattern.findall(change_section)
                
                if replace_matches and len(replace_matches) > 0:
                    target_text = replace_matches[0].strip()
                    replacement = code_blocks[-1].strip()
                    
                    # Remove any code formatting that might be in the instruction
                    target_text = re.sub(r'`(.*?)`', r'\1', target_text).strip()
                    
                    if target_text and target_text in modified_content:
                        modified_content = modified_content.replace(target_text, replacement)
                        changes_made = True
                        logging.info(f"Applied targeted replacement")
            
            # APPROACH 4: Smart diff matching for small changes
            if not changes_made and len(code_blocks) >= 2:
                import difflib
                
                old_code = code_blocks[0].strip()
                new_code = code_blocks[1].strip()
                
                # Find best match for the old code in the file
                matcher = difflib.SequenceMatcher(None, modified_content, old_code)
                match = matcher.find_longest_match(0, len(modified_content), 0, len(old_code))
                
                if match.size > len(old_code) * 0.8:  # If we found at least 80% match
                    before_match = modified_content[:match.a]
                    after_match = modified_content[match.a + match.size:]
                    modified_content = before_match + new_code + after_match
                    changes_made = True
                    logging.info(f"Applied fuzzy match replacement")
        
        # Write the changes back to the file
        if changes_made:
            with open(file_path, 'w') as f:
                f.write(modified_content)
            logging.info(f"✅ Applied code changes to {file_path}")
            return True
        else:
            logging.info(f"⚠️ Could not apply changes to {file_path} - No suitable pattern found")
            return False
            
    except Exception as e:
        logging.error(f"Error implementing changes for {file_path}: {e}")
        return False

# Main execution
if __name__ == "__main__":
    try:
        BASE_DIR, EXCLUDE_DIR, REPORT_FILE = get_user_input()
        logging.info(f"Starting analysis of {BASE_DIR}")
        logging.info(f"Backups will be stored in {BACKUP_DIR}")
        
        logging.info("Scanning files and computing hashes...")
        file_hash_dict = scan_files(BASE_DIR, EXCLUDE_DIR)
        
        # Aggregate unique file paths for AI analysis
        all_files = [f for paths in file_hash_dict.values() for f in paths if f.endswith(tuple(ANALYZABLE_EXTENSIONS))]

        with open(REPORT_FILE, "w") as report:
            logging.info("Analyzing file differences using Qwen2.5-Coder:7B...")
            analyze_differences(file_hash_dict, report)

            report.write("=== FILE RECOMMENDATIONS ===\n")
            logging.info(f"Processing {len(all_files)} Python files with AI recommendations...")

            # Run AI analysis in parallel using threads
            modified_files = []
            with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
                results = list(executor.map(lambda f: (f, analyze_file_recommendations(f)), all_files))
                
                # Process results and implement changes where possible
                for file_path, (analysis, has_changes) in results:
                    report.write(analysis)
                    
                    if has_changes:
                        user_input = input(f"\nAI suggested changes for {file_path}. Apply them? (y/n): ").lower()
                        if user_input == 'y':
                            if implement_code_changes(file_path, analysis):
                                modified_files.append(file_path)
                                report.write(f"✅ Applied changes to {file_path}\n\n")
                            else:
                                report.write(f"⚠️ Failed to apply changes to {file_path}\n\n")
            
            # Summary of modifications
            report.write("\n=== MODIFICATION SUMMARY ===\n")
            report.write(f"Total files modified: {len(modified_files)}\n")
            for file in modified_files:
                report.write(f"- {file}\n")

        logging.info(f"✅ Analysis complete! See report: {REPORT_FILE}")
        logging.info(f"✅ Modified {len(modified_files)} files")
        
    except Exception as e:
        logging.error(f"Error in main execution: {e}")
        print(f"Error: {e}")
