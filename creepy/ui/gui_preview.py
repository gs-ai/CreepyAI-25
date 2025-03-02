import tkinter as tk
import sys
import os

# Add the project directory to the Python path if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the GUI class
from creepyai_gui import CreepyAIGUI

if __name__ == "__main__":
    # Create the root Tkinter window
    root = tk.Tk()
    
    # Initialize the GUI
    app = CreepyAIGUI(root)
    
    # Print instructions
    print("CreepyAI GUI Preview")
    print("--------------------")
    print("This is a preview of the CreepyAI GUI interface.")
    print("Feel free to interact with all elements to test functionality.")
    print("Note: Some features may not be fully functional in preview mode.")
    
    # Start the main loop to display the GUI
    root.mainloop()
