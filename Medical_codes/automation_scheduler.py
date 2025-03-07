#!/usr/bin/env python3
"""
Companion Care Medical Billing Code Automation Scheduler

This script schedules periodic updates of the medical billing code cache
to ensure that the system always has up-to-date information.
"""

import os
import time
import json
import logging
import schedule
import argparse
import datetime
from typing import List, Dict, Any, Optional
from medical_code_automation import MedicalCodeAutomation

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("automation_scheduler.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("automation_scheduler")

class MedicalCodeAutomationScheduler:
    """
    Scheduler for automating medical billing code updates.
    """
    
    def __init__(self, common_codes_file: str = "common_codes.json"):
        """
        Initialize the scheduler.
        
        Args:
            common_codes_file: Path to a file containing commonly used codes to keep updated
        """
        self.automation = MedicalCodeAutomation()
        self.common_codes_file = common_codes_file
        self.common_codes = self._load_common_codes()
        self.last_full_update = None
        
        logger.info("Medical Code Automation Scheduler initialized")
    
    def _load_common_codes(self) -> List[str]:
        """Load the list of common codes from disk if it exists."""
        try:
            with open(self.common_codes_file, 'r') as f:
                data = json.load(f)
                if isinstance(data, list):
                    logger.info(f"Loaded {len(data)} common codes")
                    return data
                elif isinstance(data, dict) and "codes" in data and isinstance(data["codes"], list):
                    logger.info(f"Loaded {len(data['codes'])} common codes")
                    return data["codes"]
                else:
                    logger.warning("Invalid format in common codes file")
                    return []
        except (FileNotFoundError, json.JSONDecodeError):
            logger.info("No valid common codes file found, creating default")
            # Create a default file with some common HCPCS codes
            default_codes = [
                # Common evaluation and management codes
                "99201", "99202", "99203", "99204", "99205",  # Office/outpatient visit new
                "99211", "99212", "99213", "99214", "99215",  # Office/outpatient visit established
                # Common procedure codes
                "36415",  # Routine venipuncture
                "81001",  # Urinalysis, automated with microscopy
                "82607",  # Vitamin B-12
                "82947",  # Glucose, quantitative, blood
                "85025",  # Complete CBC with differential WBC
                # Common medical equipment codes
                "E0100",  # Cane
                "E0250",  # Hospital bed, fixed height
                "E0601",  # CPAP device
                "E1390",  # Oxygen concentrator
                "E0143"   # Walker, folding, wheeled
            ]
            self._save_common_codes(default_codes)
            return default_codes
    
    def _save_common_codes(self, codes: List[str]) -> None:
        """Save the list of common codes to disk."""
        try:
            os.makedirs(os.path.dirname(self.common_codes_file), exist_ok=True)
            with open(self.common_codes_file, 'w') as f:
                json.dump({"codes": codes, "updated_at": datetime.datetime.now().isoformat()}, f, indent=2)
                logger.info(f"Saved {len(codes)} common codes")
        except Exception as e:
            logger.error(f"Failed to save common codes: {str(e)}")
    
    def update_common_codes(self) -> None:
        """Update the cache for commonly used codes."""
        logger.info("Starting update of common codes")
        
        if not self.common_codes:
            logger.warning("No common codes to update")
            return
        
        try:
            # Update the codes in batches
            batch_size = 20
            for i in range(0, len(self.common_codes), batch_size):
                batch = self.common_codes[i:i+batch_size]
                logger.info(f"Updating batch of {len(batch)} common codes")
                
                self.automation.bulk_update_codes(batch)
                
                # Be nice to the API with a small delay between batches
                if i + batch_size < len(self.common_codes):
                    time.sleep(2)
            
            logger.info(f"Completed update of {len(self.common_codes)} common codes")
        except Exception as e:
            logger.error(f"Error updating common codes: {str(e)}")
    
    def perform_search_updates(self) -> None:
        """Perform searches for common terms to keep the cache updated with current data."""
        common_search_terms = [
            "wheelchair", "oxygen", "hospital bed", "diabetes", 
            "insulin", "physical therapy", "evaluation", "office visit"
        ]
        
        logger.info(f"Performing search updates for {len(common_search_terms)} terms")
        
        try:
            for term in common_search_terms:
                logger.info(f"Searching for term: '{term}'")
                self.automation.search_codes(term, max_results=10)
                time.sleep(2)  # Be nice to the API
            
            logger.info("Completed search updates")
        except Exception as e:
            logger.error(f"Error performing search updates: {str(e)}")
    
    def perform_full_update(self) -> None:
        """Perform a full update of the code cache."""
        logger.info("Starting full update")
        
        try:
            # Update common codes
            self.update_common_codes()
            
            # Perform search updates
            self.perform_search_updates()
            
            self.last_full_update = datetime.datetime.now()
            logger.info(f"Completed full update at {self.last_full_update}")
        except Exception as e:
            logger.error(f"Error performing full update: {str(e)}")
    
    def add_common_code(self, code: str) -> None:
        """Add a code to the list of common codes."""
        if code not in self.common_codes:
            self.common_codes.append(code)
            self._save_common_codes(self.common_codes)
            logger.info(f"Added code {code} to common codes")
            
            # Update the code immediately
            self.automation.get_code_details(code)
    
    def remove_common_code(self, code: str) -> None:
        """Remove a code from the list of common codes."""
        if code in self.common_codes:
            self.common_codes.remove(code)
            self._save_common_codes(self.common_codes)
            logger.info(f"Removed code {code} from common codes")
    
    def schedule_jobs(self) -> None:
        """Schedule the automation jobs."""
        # Update common codes every day at 2 AM
        schedule.every().day.at("02:00").do(self.update_common_codes)
        
        # Perform search updates every day at 3 AM
        schedule.every().day.at("03:00").do(self.perform_search_updates)
        
        # Perform a full update every Sunday at 1 AM
        schedule.every().sunday.at("01:00").do(self.perform_full_update)
        
        logger.info("Scheduled automation jobs")
    
    def run(self) -> None:
        """Run the scheduler."""
        self.schedule_jobs()
        
        # Perform an initial update
        logger.info("Performing initial update")
        self.perform_full_update()
        
        logger.info("Starting scheduler loop")
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check for pending jobs every minute

def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Companion Care Medical Billing Code Automation Scheduler"
    )
    
    parser.add_argument("--run-once", action="store_true",
                       help="Run a full update once and exit")
    parser.add_argument("--add-code", type=str,
                       help="Add a code to the list of common codes")
    parser.add_argument("--remove-code", type=str,
                       help="Remove a code from the list of common codes")
    parser.add_argument("--list-codes", action="store_true",
                       help="List all common codes")
    
    return parser.parse_args()

def main() -> None:
    """Run the scheduler."""
    args = parse_args()
    scheduler = MedicalCodeAutomationScheduler()
    
    if args.add_code:
        scheduler.add_common_code(args.add_code)
        return
    
    if args.remove_code:
        scheduler.remove_common_code(args.remove_code)
        return
    
    if args.list_codes:
        print("Common Codes:")
        for code in scheduler.common_codes:
            print(f"- {code}")
        return
    
    if args.run_once:
        scheduler.perform_full_update()
        return
    
    # Run the scheduler
    try:
        scheduler.run()
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
    except Exception as e:
        logger.error(f"Error running scheduler: {str(e)}")

if __name__ == "__main__":
    main() 