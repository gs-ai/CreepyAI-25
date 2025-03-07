#!/usr/bin/env python3
import sys
import subprocess

def check_environment():
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")
    print(f"Python path: {sys.path}")
    
    try:
        import ollama
        print(f"Ollama is installed at: {ollama.__file__}")
        print(f"Ollama version: {ollama.__version__ if hasattr(ollama, '__version__') else 'version not available'}")
    except ImportError:
        print("Ollama is NOT installed in the current environment")
        
        # Try to pip install it
        print("\nAttempting to install ollama package...")
        subprocess.run([sys.executable, "-m", "pip", "install", "ollama"])
        
        # Check if installation worked
        try:
            import ollama
            print(f"Ollama was successfully installed at: {ollama.__file__}")
        except ImportError:
            print("Failed to install ollama package.")

if __name__ == "__main__":
    check_environment()
