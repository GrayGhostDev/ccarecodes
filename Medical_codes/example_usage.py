#!/usr/bin/env python3
"""
Companion Care Medical Billing Code Automation - Example Usage

This script demonstrates how to use the medical code automation system
in a real-world scenario.
"""

import json
import logging
from medical_code_automation import MedicalCodeAutomation

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("example_usage")

def example_patient_visit():
    """
    Simulate a patient visit and generate a bill using the medical code automation system.
    
    Scenario: A patient with diabetes comes in for a routine check-up, gets a blood glucose test,
    and is prescribed a new wheelchair.
    """
    logger.info("Starting example: Patient Visit")
    
    # Initialize the medical code automation
    automation = MedicalCodeAutomation()
    
    # Step 1: Find the appropriate codes for the visit
    logger.info("\nStep 1: Finding appropriate codes for the visit")
    
    # Office visit for established patient (moderate complexity)
    office_visit_results = automation.search_codes("office visit established patient", max_results=10)
    office_visit_code = None
    for result in office_visit_results:
        if "99214" in result["code"]:  # Moderate complexity established patient visit
            office_visit_code = result
            break
    
    if office_visit_code:
        logger.info(f"Selected office visit code: {office_visit_code['code']} - {office_visit_code['description']}")
    else:
        logger.warning("Could not find appropriate office visit code")
        office_visit_code = {"code": "99214", "description": "Office visit, established patient (moderate complexity)"}
    
    # Blood glucose test
    glucose_test_results = automation.search_codes("glucose blood test", max_results=10)
    glucose_test_code = None
    for result in glucose_test_results:
        if "82947" in result["code"]:  # Glucose blood test
            glucose_test_code = result
            break
    
    if glucose_test_code:
        logger.info(f"Selected glucose test code: {glucose_test_code['code']} - {glucose_test_code['description']}")
    else:
        logger.warning("Could not find appropriate glucose test code")
        glucose_test_code = {"code": "82947", "description": "Glucose; quantitative, blood"}
    
    # Wheelchair
    wheelchair_results = automation.search_codes("wheelchair", max_results=10)
    wheelchair_code = None
    for result in wheelchair_results:
        if "E0143" in result["code"]:  # Folding walker with wheels
            wheelchair_code = result
            break
    
    if wheelchair_code:
        logger.info(f"Selected wheelchair code: {wheelchair_code['code']} - {wheelchair_code['description']}")
    else:
        logger.warning("Could not find appropriate wheelchair code")
        wheelchair_code = {"code": "E0143", "description": "Walker, folding, wheeled"}
    
    # Step 2: Get detailed information for the selected codes
    logger.info("\nStep 2: Getting detailed information for the selected codes")
    
    codes = [
        office_visit_code["code"],
        glucose_test_code["code"],
        wheelchair_code["code"]
    ]
    
    code_details = automation.bulk_update_codes(codes)
    
    for code in codes:
        if code in code_details:
            details = code_details[code]
            price = details.get("price", "N/A")
            logger.info(f"Code: {code}, Description: {details.get('description', 'N/A')}, Price: ${price}")
    
    # Step 3: Generate a bill for the patient
    logger.info("\nStep 3: Generating a bill for the patient")
    
    # Define quantities for each code
    quantities = {
        office_visit_code["code"]: 1,
        glucose_test_code["code"]: 1,
        wheelchair_code["code"]: 1
    }
    
    # Calculate the bill
    items = []
    total = 0.0
    
    for code in codes:
        if code in code_details:
            details = code_details[code]
            quantity = quantities.get(code, 1)
            
            # Get price (default to 0 if not available)
            price = details.get('price')
            if price is None:
                price = 0.0
            else:
                try:
                    price = float(price)
                except (ValueError, TypeError):
                    price = 0.0
            
            item_total = price * quantity
            total += item_total
            
            items.append({
                "code": code,
                "description": details.get('description', ''),
                "price": price,
                "quantity": quantity,
                "item_total": item_total
            })
    
    # Print the bill
    logger.info("Patient Bill:")
    logger.info("-" * 80)
    logger.info(f"{'Code':<10} {'Description':<50} {'Price':<10} {'Qty':<5} {'Total':<10}")
    logger.info("-" * 80)
    
    for item in items:
        logger.info(f"{item['code']:<10} {item['description'][:50]:<50} ${item['price']:<9.2f} {item['quantity']:<5} ${item['item_total']:<9.2f}")
    
    logger.info("-" * 80)
    logger.info(f"{'Total:':<76} ${total:<9.2f}")
    
    # Step 4: Save the bill to a file
    logger.info("\nStep 4: Saving the bill to a file")
    
    bill_data = {
        "patient_id": "12345",
        "patient_name": "John Doe",
        "date": "2023-07-15",
        "items": items,
        "total": total,
        "currency": "USD"
    }
    
    with open("example_bill.json", "w") as f:
        json.dump(bill_data, f, indent=2)
    
    logger.info("Bill saved to example_bill.json")
    
    # Return the bill data for potential further processing
    return bill_data

def example_insurance_claim():
    """
    Simulate generating an insurance claim using the medical code automation system.
    
    This example builds on the patient visit example and generates a claim for insurance.
    """
    logger.info("\nStarting example: Insurance Claim")
    
    # Get the bill data from the patient visit example
    bill_data = example_patient_visit()
    
    # Step 1: Prepare the claim data
    logger.info("\nStep 1: Preparing the claim data")
    
    claim_data = {
        "claim_id": "CL-2023-12345",
        "patient_id": bill_data["patient_id"],
        "patient_name": bill_data["patient_name"],
        "provider_id": "P-9876",
        "provider_name": "Companion Care Medical Center",
        "date_of_service": bill_data["date"],
        "diagnosis_codes": [
            {"code": "E11.9", "description": "Type 2 diabetes mellitus without complications"}
        ],
        "procedure_codes": []
    }
    
    # Add the procedure codes from the bill
    for item in bill_data["items"]:
        claim_data["procedure_codes"].append({
            "code": item["code"],
            "description": item["description"],
            "price": item["price"],
            "quantity": item["quantity"]
        })
    
    # Step 2: Save the claim to a file
    logger.info("\nStep 2: Saving the claim to a file")
    
    with open("example_claim.json", "w") as f:
        json.dump(claim_data, f, indent=2)
    
    logger.info("Claim saved to example_claim.json")
    
    # Return the claim data for potential further processing
    return claim_data

if __name__ == "__main__":
    # Run the examples
    example_patient_visit()
    example_insurance_claim() 