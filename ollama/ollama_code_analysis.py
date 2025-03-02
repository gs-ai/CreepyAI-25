import os
import hashlib
import difflib
import ollama

# Set base directory for analysis
BASE_DIR = "/Users/mbaosint/Desktop/Projects/CreepyAI"
OLLAMA_DIR = os.path.join(BASE_DIR, "ollama")  # Directory to exclude
OLLAMA_MODEL = "codellama:13b"  # Best model for code analysis
REPORT_FILE = os.path.join(OLLAMA_DIR, "ollama_file_analysis.txt")

# Function to compute SHA256 hash of a file (efficiently, in chunks)
def compute_hash(file_path):
    hasher = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        return f"Error: {e}"

# Identify all files and compute hashes, skipping the ollama directory
file_hashes = {}
file_paths = []

for root, _, files in os.walk(BASE_DIR):
    if root.startswith(OLLAMA_DIR):  # Skip the ollama directory
        continue
    for file in files:
        file_path = os.path.join(root, file)
        file_paths.append(file_path)
        file_hashes[file_path] = compute_hash(file_path)

# Group files by hash (identical files)
identical_files = {}
for path, file_hash in file_hashes.items():
    identical_files.setdefault(file_hash, []).append(path)

# Write results to disk immediately (to save RAM)
with open(REPORT_FILE, "w") as report:

    # Log identical files
    report.write("=== IDENTICAL FILES ===\n")
    for paths in identical_files.values():
        if len(paths) > 1:
            report.write("\n".join(paths) + "\n\n")

    # Log differences
    report.write("\n=== FILE DIFFERENCES ANALYSIS ===\n")

    # Compare non-identical files and stream analysis
    for file_list in identical_files.values():
        if len(file_list) == 1:
            continue  # Skip unique files

        ref_file = file_list[0]
        for file in file_list[1:]:
            if os.path.exists(ref_file) and os.path.exists(file):
                try:
                    # Stream file differences line by line
                    with open(ref_file, "r", errors="ignore") as f1, open(file, "r", errors="ignore") as f2:
                        diff = difflib.unified_diff(f1, f2, fromfile=ref_file, tofile=file)
                        diff_text = "".join(diff)

                    if diff_text:
                        # AI-based summarization (streamed directly to file)
                        prompt = f"Analyze the differences between these two code files:\n{diff_text}\nSummarize key differences."
                        response = ollama.chat(model=OLLAMA_MODEL, messages=[{"role": "user", "content": prompt}])
                        analysis = response["message"]["content"]

                        # Write to report file immediately
                        report.write(f"Comparison: {ref_file} <--> {file}\n{analysis}\n\n")

                except Exception as e:
                    report.write(f"Error comparing {ref_file} and {file}: {e}\n\n")

print(f"✅ Analysis complete! See report: {REPORT_FILE}")
