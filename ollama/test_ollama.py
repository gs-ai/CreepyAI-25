#!/usr/bin/env python3
import sys
import os

# Print the path where Python is looking for modules
print("Python executable:", sys.executable)
print("Python version:", sys.version)
print("PYTHONPATH:", os.environ.get("PYTHONPATH", "Not set"))

try:
    import ollama
    print("✅ Ollama is installed correctly!")
    print(f"Ollama module location: {ollama.__file__}")
except ImportError as e:
    print(f"❌ Failed to import ollama: {e}")
    print("\nPlease run the following commands to fix the issue:")
    print(f"{sys.executable} -m pip install --upgrade pip")
    print(f"{sys.executable} -m pip install ollama==0.1.5")
