#!/usr/bin/env python3
"""
Companion Care Medical Billing Code Example Usage Wrapper Script

This script is a simple wrapper that runs the example_usage.py script in the Medical_codes directory.
"""

import os
import sys
import subprocess

def main():
    """Run the example_usage.py script in the Medical_codes directory."""
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the Medical_codes directory
    medical_codes_dir = os.path.join(script_dir, "Medical_codes")
    
    # Path to the example_usage.py script in the Medical_codes directory
    example_script = os.path.join(medical_codes_dir, "example_usage.py")
    
    # Check if the script exists
    if not os.path.exists(example_script):
        print(f"Error: {example_script} not found")
        return 1
    
    # Get the Python interpreter path
    python_path = sys.executable
    
    # Pass all command-line arguments to the example_usage.py script
    cmd = [python_path, example_script] + sys.argv[1:]
    
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