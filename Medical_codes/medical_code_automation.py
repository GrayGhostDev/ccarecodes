#!/usr/bin/env python3
"""
Companion Care Medical Billing Code Automation

This script automates the retrieval of HCPCS medical billing codes from the Clinical Tables NLM API
and provides functionality to relay this information to the end user through an API.
"""

import requests
import json
import logging
import time
from typing import Dict, List, Any, Optional, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("medical_code_automation.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("medical_code_automation")

class MedicalCodeAutomation:
    """
    Automation class for retrieving and processing medical billing codes.
    """
    
    BASE_URL = "https://clinicaltables.nlm.nih.gov/api/hcpcs/v3"
    
    def __init__(self, cache_file: str = "code_cache.json"):
        """
        Initialize the medical code automation system.
        
        Args:
            cache_file: Path to the file where code data will be cached
        """
        self.cache_file = cache_file
        self.code_cache = self._load_cache()
        logger.info("Medical Code Automation initialized")
    
    def _load_cache(self) -> Dict[str, Any]:
        """Load the code cache from disk if it exists."""
        try:
            with open(self.cache_file, 'r') as f:
                cache = json.load(f)
                logger.info(f"Loaded {len(cache)} codes from cache")
                return cache
        except (FileNotFoundError, json.JSONDecodeError):
            logger.info("No valid cache found, starting with empty cache")
            return {}
    
    def _save_cache(self) -> None:
        """Save the current code cache to disk."""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.code_cache, f)
                logger.info(f"Saved {len(self.code_cache)} codes to cache")
        except Exception as e:
            logger.error(f"Failed to save cache: {str(e)}")
    
    def search_codes(self, query: str, max_results: int = 20) -> List[Dict[str, Any]]:
        """
        Search for medical billing codes based on a query string.
        
        Args:
            query: The search term (code or description)
            max_results: Maximum number of results to return
            
        Returns:
            A list of matching code entries
        """
        logger.info(f"Searching for codes with query: '{query}'")
        
        try:
            # Format: /search?terms=query&maxList=max_results
            response = requests.get(
                f"{self.BASE_URL}/search",
                params={
                    "terms": query,
                    "maxList": max_results,
                    "df": "code,display",  # Request specific fields
                    "ef": "code,display,short_desc,long_desc"  # Extra fields
                },
                timeout=10
            )
            
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"API response: {data}")
            
            # API returns [total_count, codes, extra_data, display_data]
            if len(data) >= 4:
                results = []
                total_count = data[0]
                codes = data[1]
                extra_data = data[2]
                display_data = data[3]
                
                # Process the results into a more usable format
                for i, code in enumerate(codes):
                    if i < len(display_data):
                        display_info = display_data[i]
                        
                        # Create a code entry with available information
                        code_entry = {
                            "code": code,
                            "description": display_info[1] if len(display_info) > 1 else "",
                            "price": None  # Price not available from the API
                        }
                        
                        # Add extra data if available
                        if extra_data and isinstance(extra_data, dict):
                            for field, values in extra_data.items():
                                if i < len(values):
                                    code_entry[field] = values[i]
                        
                        results.append(code_entry)
                        
                        # Update cache with this code
                        self.code_cache[code_entry["code"]] = code_entry
                
                # Save updated cache
                self._save_cache()
                
                logger.info(f"Found {len(results)} matching codes")
                return results
            else:
                logger.warning(f"Unexpected API response format: {data}")
                return []
                
        except Exception as e:
            logger.error(f"Error searching for codes: {str(e)}")
            return []
    
    def get_code_details(self, code: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information for a specific medical code.
        
        Args:
            code: The medical code to look up
            
        Returns:
            A dictionary with code details or None if not found
        """
        logger.info(f"Getting details for code: {code}")
        
        # Check cache first
        if code in self.code_cache:
            logger.info(f"Code {code} found in cache")
            return self.code_cache[code]
        
        try:
            # Search for the code instead of using /items endpoint
            response = requests.get(
                f"{self.BASE_URL}/search",
                params={
                    "terms": code,
                    "maxList": 1,
                    "df": "code,display",
                    "ef": "code,display,short_desc,long_desc"
                },
                timeout=10
            )
            
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"API response: {data}")
            
            # Check if we found the code
            if len(data) >= 4 and data[0] > 0 and len(data[1]) > 0:
                codes = data[1]
                extra_data = data[2]
                display_data = data[3]
                
                # Check if the first result matches our code
                if codes[0] == code:
                    display_info = display_data[0]
                    
                    # Create a code entry with available information
                    code_details = {
                        "code": code,
                        "description": display_info[1] if len(display_info) > 1 else "",
                        "price": None  # Price not available from the API
                    }
                    
                    # Add extra data if available
                    if extra_data and isinstance(extra_data, dict):
                        additional_info = {}
                        for field, values in extra_data.items():
                            if len(values) > 0:
                                additional_info[field] = values[0]
                        
                        code_details["additional_info"] = additional_info
                    
                    # Update cache with this code
                    self.code_cache[code] = code_details
                    self._save_cache()
                    
                    logger.info(f"Retrieved details for code {code}")
                    return code_details
            
            logger.warning(f"Code {code} not found")
            return None
                
        except Exception as e:
            logger.error(f"Error getting code details: {str(e)}")
            return None
    
    def bulk_update_codes(self, code_list: List[str]) -> Dict[str, Any]:
        """
        Update information for multiple codes at once.
        
        Args:
            code_list: List of codes to update
            
        Returns:
            Dictionary mapping codes to their details
        """
        logger.info(f"Bulk updating {len(code_list)} codes")
        
        results = {}
        codes_to_fetch = []
        
        # Check which codes we need to fetch vs. which are in cache
        for code in code_list:
            if code in self.code_cache:
                results[code] = self.code_cache[code]
            else:
                codes_to_fetch.append(code)
        
        # Fetch codes not in cache (in batches to avoid overloading the API)
        batch_size = 10
        for i in range(0, len(codes_to_fetch), batch_size):
            batch = codes_to_fetch[i:i+batch_size]
            logger.info(f"Fetching batch of {len(batch)} codes")
            
            for code in batch:
                details = self.get_code_details(code)
                if details:
                    results[code] = details
            
            # Be nice to the API with a small delay between batches
            if i + batch_size < len(codes_to_fetch):
                time.sleep(1)
        
        logger.info(f"Completed bulk update, retrieved {len(results)} codes")
        return results

# Example usage
if __name__ == "__main__":
    automation = MedicalCodeAutomation()
    
    # Example: Search for wheelchair-related codes
    results = automation.search_codes("wheelchair")
    print(f"Found {len(results)} wheelchair-related codes")
    
    # Print the first few results
    for i, result in enumerate(results[:5]):
        print(f"{i+1}. {result['code']}: {result['description']} - ${result.get('price', 'N/A')}")
    
    # Example: Get details for a specific code
    if results:
        first_code = results[0]['code']
        details = automation.get_code_details(first_code)
        print(f"\nDetails for {first_code}:")
        print(json.dumps(details, indent=2)) 