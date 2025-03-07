#!/usr/bin/env python3
"""
Companion Care Medical Billing Code Automation Wrapper Script

This script is a simple wrapper that runs the start.py script in the Medical_codes directory.
"""

import os
import sys
import subprocess

def main():
    """Run the start.py script in the Medical_codes directory."""
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the Medical_codes directory
    medical_codes_dir = os.path.join(script_dir, "Medical_codes")
    
    # Path to the start.py script in the Medical_codes directory
    start_script = os.path.join(medical_codes_dir, "start.py")
    
    # Check if the script exists
    if not os.path.exists(start_script):
        print(f"Error: {start_script} not found")
        return 1
    
    # Get the Python interpreter path
    python_path = sys.executable
    
    # Pass all command-line arguments to the start.py script
    cmd = [python_path, start_script] + sys.argv[1:]
    
    # Run the script from the Medical_codes directory
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