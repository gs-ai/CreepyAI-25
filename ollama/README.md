# CreepyAI Ollama Tools

This directory contains tools for code analysis and improvement using Ollama models.

## Tools

### ollama_code_analysis.py

Main code analysis tool that:
1. Scans directories for Python files
2. Identifies duplicate files
3. Uses the Ollama API to analyze code and suggest improvements
4. Applies recommended changes when possible

#### Usage

```bash
python ollama_code_analysis.py
```

You'll be prompted to enter the directory path you want to analyze.

### debug_changes.py

Helper script for manually applying AI suggestions that couldn't be applied automatically.

#### Usage

```bash
python debug_changes.py /path/to/ollama_file_analysis.txt
```

This interactive tool will:
1. Parse the analysis report
2. Let you select a file that needs changes
3. Display the recommended code changes
4. Guide you through manually applying those changes

## Requirements

- Ollama running locally with the `qwen2.5-coder:7b` model
- Python 3.8+
- Required packages: ollama, difflib, logging

## Tips for Better Results

1. Run Ollama locally with sufficient GPU memory
2. Start with smaller, focused directories for analysis
3. Review the suggested changes carefully before applying
4. Use the debug_changes.py tool for complex modifications

## Log Files

The analysis results are saved to `ollama_file_analysis.txt` in the target directory.
