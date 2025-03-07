#!/usr/bin/env python3
"""
Companion Care Medical Billing Code Streamlit Application Wrapper Script

This script is a simple wrapper that runs the streamlit_app.py script in the Medical_codes directory.
"""

import os
import sys
import subprocess
import shutil

def main():
    """Run the streamlit_app.py script in the Medical_codes directory."""
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the Medical_codes directory
    medical_codes_dir = os.path.join(script_dir, "Medical_codes")
    
    # Path to the streamlit_app.py script in the Medical_codes directory
    streamlit_script = os.path.join(medical_codes_dir, "streamlit_app.py")
    
    # Check if the script exists
    if not os.path.exists(streamlit_script):
        print(f"Error: {streamlit_script} not found")
        return 1
    
    # Find the streamlit executable
    streamlit_path = shutil.which("streamlit")
    if not streamlit_path:
        print("Error: streamlit command not found. Please install streamlit with 'pip install streamlit'")
        return 1
    
    # Run the script with streamlit from the Medical_codes directory
    cmd = [streamlit_path, "run", streamlit_script] + sys.argv[1:]
    
    # Run the script
    try:
        process = subprocess.Popen(cmd, cwd=medical_codes_dir)
        process.wait()
        return process.returncode
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        return 0
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 