#!/usr/bin/env python3
"""
Companion Care Medical Billing Code Automation Startup Script

This script provides a simple way to start the different components of the
medical billing code automation system.
"""

import os
import sys
import argparse
import subprocess
import logging
import time
import signal
import atexit

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("start.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("start")

# Keep track of running processes
processes = []

def cleanup():
    """Clean up running processes when the script exits."""
    for process in processes:
        if process.poll() is None:  # Process is still running
            logger.info(f"Terminating process {process.pid}")
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning(f"Process {process.pid} did not terminate, killing it")
                process.kill()

# Register the cleanup function to be called on exit
atexit.register(cleanup)

def signal_handler(sig, frame):
    """Handle signals (e.g., Ctrl+C)."""
    logger.info(f"Received signal {sig}, cleaning up")
    sys.exit(0)

# Register the signal handler for SIGINT (Ctrl+C) and SIGTERM
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def start_api_server(port=8000, debug=False):
    """Start the API server."""
    logger.info(f"Starting API server on port {port}")
    
    env = os.environ.copy()
    env["PORT"] = str(port)
    env["DEBUG"] = str(debug).lower()
    
    process = subprocess.Popen(
        [sys.executable, "api_server.py"],
        env=env
    )
    
    processes.append(process)
    logger.info(f"API server started with PID {process.pid}")
    
    # Wait a moment to ensure the server starts
    time.sleep(2)
    
    # Check if the process is still running
    if process.poll() is not None:
        logger.error(f"API server failed to start (exit code {process.returncode})")
        return False
    
    logger.info("API server is running")
    return True

def start_scheduler(run_once=False):
    """Start the automation scheduler."""
    logger.info("Starting automation scheduler")
    
    cmd = [sys.executable, "automation_scheduler.py"]
    if run_once:
        cmd.append("--run-once")
    
    process = subprocess.Popen(
        cmd
    )
    
    processes.append(process)
    logger.info(f"Automation scheduler started with PID {process.pid}")
    
    # If running once, wait for completion
    if run_once:
        process.wait()
        logger.info(f"Automation scheduler completed with exit code {process.returncode}")
        return process.returncode == 0
    
    # Wait a moment to ensure the scheduler starts
    time.sleep(2)
    
    # Check if the process is still running
    if process.poll() is not None:
        logger.error(f"Automation scheduler failed to start (exit code {process.returncode})")
        return False
    
    logger.info("Automation scheduler is running")
    return True

def run_cli_command(args):
    """Run a CLI command."""
    logger.info(f"Running CLI command: {' '.join(args)}")
    
    process = subprocess.Popen(
        [sys.executable, "cli_tool.py"] + args
    )
    
    process.wait()
    logger.info(f"CLI command completed with exit code {process.returncode}")
    return process.returncode == 0

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Companion Care Medical Billing Code Automation Startup Script"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # API server command
    api_parser = subparsers.add_parser("api", help="Start the API server")
    api_parser.add_argument("--port", type=int, default=8000, help="Port to listen on")
    api_parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    # Scheduler command
    scheduler_parser = subparsers.add_parser("scheduler", help="Start the automation scheduler")
    scheduler_parser.add_argument("--run-once", action="store_true", help="Run once and exit")
    
    # CLI command
    cli_parser = subparsers.add_parser("cli", help="Run a CLI command")
    cli_parser.add_argument("args", nargs=argparse.REMAINDER, help="Arguments to pass to the CLI tool")
    
    # All command
    all_parser = subparsers.add_parser("all", help="Start all components")
    all_parser.add_argument("--port", type=int, default=8000, help="Port for the API server")
    all_parser.add_argument("--debug", action="store_true", help="Enable debug mode for the API server")
    
    return parser.parse_args()

def main():
    """Run the startup script."""
    args = parse_args()
    
    if not args.command:
        print("Please specify a command. Use --help for more information.")
        return 1
    
    try:
        if args.command == "api":
            start_api_server(args.port, args.debug)
            # Keep the script running
            while all(process.poll() is None for process in processes):
                time.sleep(1)
        
        elif args.command == "scheduler":
            start_scheduler(args.run_once)
            # If not run_once, keep the script running
            if not args.run_once:
                while all(process.poll() is None for process in processes):
                    time.sleep(1)
        
        elif args.command == "cli":
            run_cli_command(args.args)
        
        elif args.command == "all":
            # Start both the API server and the scheduler
            api_success = start_api_server(args.port, args.debug)
            scheduler_success = start_scheduler()
            
            if not api_success or not scheduler_success:
                logger.error("Failed to start all components")
                return 1
            
            logger.info("All components started successfully")
            
            # Keep the script running
            while all(process.poll() is None for process in processes):
                time.sleep(1)
    
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 