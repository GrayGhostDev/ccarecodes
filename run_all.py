#!/usr/bin/env python3
"""
Companion Care Medical Billing Code Automation - Run All Components

This script runs all the components of the medical billing code automation system:
1. API Server
2. Streamlit Web Application
"""

import os
import sys
import time
import signal
import subprocess
import webbrowser
import atexit
import socket
import shutil

# Keep track of running processes
processes = []

def cleanup():
    """Clean up running processes when the script exits."""
    for process in processes:
        if process.poll() is None:  # Process is still running
            print(f"Terminating process {process.pid}")
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print(f"Process {process.pid} did not terminate, killing it")
                process.kill()

# Register the cleanup function to be called on exit
atexit.register(cleanup)

def signal_handler(sig, frame):
    """Handle signals (e.g., Ctrl+C)."""
    print(f"\nReceived signal {sig}, cleaning up")
    sys.exit(0)

# Register the signal handler for SIGINT (Ctrl+C) and SIGTERM
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def find_free_port(start_port=8000, max_attempts=100):
    """Find a free port starting from start_port."""
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('localhost', port)) != 0:
                return port
    return None

def start_api_server():
    """Start the API server."""
    print("Starting API server...")
    
    # Find a free port
    port = find_free_port(8000)
    if port is None:
        print("Error: Could not find a free port for the API server")
        return False
    
    print(f"Using port {port} for the API server")
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the Medical_codes directory
    medical_codes_dir = os.path.join(script_dir, "Medical_codes")
    
    # Path to the api_server.py script
    api_script = os.path.join(medical_codes_dir, "api_server.py")
    
    # Check if the script exists
    if not os.path.exists(api_script):
        print(f"Error: {api_script} not found")
        return False
    
    # Get the Python interpreter path
    python_path = sys.executable
    
    # Set environment variables
    env = os.environ.copy()
    env["PORT"] = str(port)
    
    # Run the script
    process = subprocess.Popen(
        [python_path, api_script],
        cwd=medical_codes_dir,
        env=env
    )
    processes.append(process)
    print(f"API server started with PID {process.pid}")
    
    # Wait a moment to ensure the server starts
    time.sleep(2)
    
    # Check if the process is still running
    if process.poll() is not None:
        print(f"API server failed to start (exit code {process.returncode})")
        return False
    
    print(f"API server is running at http://localhost:{port}")
    return port

def start_streamlit_app():
    """Start the Streamlit web application."""
    print("Starting Streamlit web application...")
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the Medical_codes directory
    medical_codes_dir = os.path.join(script_dir, "Medical_codes")
    
    # Path to the streamlit_app.py script
    streamlit_script = os.path.join(medical_codes_dir, "streamlit_app.py")
    
    # Check if the script exists
    if not os.path.exists(streamlit_script):
        print(f"Error: {streamlit_script} not found")
        return False
    
    # Find the streamlit executable
    streamlit_path = shutil.which("streamlit")
    if not streamlit_path:
        print("Error: streamlit command not found. Please install streamlit with 'pip install streamlit'")
        return False
    
    # Run the script
    process = subprocess.Popen(
        [streamlit_path, "run", streamlit_script],
        cwd=medical_codes_dir
    )
    processes.append(process)
    print(f"Streamlit web application started with PID {process.pid}")
    
    # Wait a moment to ensure the application starts
    time.sleep(5)
    
    # Check if the process is still running
    if process.poll() is not None:
        print(f"Streamlit web application failed to start (exit code {process.returncode})")
        return False
    
    print("Streamlit web application is running at http://localhost:8501")
    return True

def open_browser():
    """Open the web browser to the Streamlit application."""
    print("Opening web browser...")
    webbrowser.open("http://localhost:8501")

def main():
    """Run all components."""
    print("Starting all components...")
    
    # Start the API server
    api_port = start_api_server()
    if not api_port:
        print("Failed to start API server")
        return 1
    
    # Start the Streamlit web application
    streamlit_success = start_streamlit_app()
    
    if not streamlit_success:
        print("Failed to start Streamlit web application")
        return 1
    
    # Open the web browser
    open_browser()
    
    print("\nAll components started successfully")
    print(f"API server is running at http://localhost:{api_port}")
    print("Streamlit web application is running at http://localhost:8501")
    print("Press Ctrl+C to stop all components")
    
    # Keep the script running
    try:
        while all(process.poll() is None for process in processes):
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 