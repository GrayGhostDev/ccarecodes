#!/usr/bin/env python3
"""
Companion Care Medical Billing Code CLI Tool

This script provides a command-line interface for interacting with the
medical billing code automation system.
"""

import os
import sys
import json
import argparse
import logging
from typing import List, Dict, Any
from medical_code_automation import MedicalCodeAutomation

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("cli_tool.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("cli_tool")

def setup_parser() -> argparse.ArgumentParser:
    """Set up the command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="Companion Care Medical Billing Code CLI Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search for medical billing codes")
    search_parser.add_argument("query", help="Search query (code or description)")
    search_parser.add_argument("--max-results", type=int, default=20, 
                              help="Maximum number of results to return")
    search_parser.add_argument("--output", choices=["table", "json"], default="table",
                              help="Output format (default: table)")
    
    # Get details command
    details_parser = subparsers.add_parser("details", help="Get details for a specific code")
    details_parser.add_argument("code", help="Medical code to look up")
    details_parser.add_argument("--output", choices=["table", "json"], default="table",
                               help="Output format (default: table)")
    
    # Bulk lookup command
    bulk_parser = subparsers.add_parser("bulk", help="Look up multiple codes at once")
    bulk_parser.add_argument("codes", nargs="+", help="List of codes to look up")
    bulk_parser.add_argument("--output", choices=["table", "json"], default="table",
                            help="Output format (default: table)")
    
    # Estimate command
    estimate_parser = subparsers.add_parser("estimate", help="Estimate cost for a set of codes")
    estimate_parser.add_argument("codes", nargs="+", help="List of codes to include in the estimate")
    estimate_parser.add_argument("--quantities", help="JSON string mapping codes to quantities")
    estimate_parser.add_argument("--output", choices=["table", "json"], default="table",
                                help="Output format (default: table)")
    
    return parser

def print_table(headers: List[str], rows: List[List[Any]]) -> None:
    """Print data in a formatted table."""
    # Calculate column widths
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))
    
    # Print headers
    header_row = " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    print(header_row)
    print("-" * len(header_row))
    
    # Print rows
    for row in rows:
        print(" | ".join(str(cell).ljust(col_widths[i]) for i, cell in enumerate(row)))

def handle_search(args, automation: MedicalCodeAutomation) -> None:
    """Handle the search command."""
    results = automation.search_codes(args.query, args.max_results)
    
    if args.output == "json":
        print(json.dumps(results, indent=2))
    else:
        if not results:
            print(f"No results found for query: '{args.query}'")
            return
        
        headers = ["Code", "Description", "Price"]
        rows = []
        
        for result in results:
            price = result.get("price", "N/A")
            if price is not None:
                price = f"${price}"
            else:
                price = "N/A"
                
            rows.append([
                result["code"],
                result["description"],
                price
            ])
        
        print(f"Found {len(results)} results for query: '{args.query}'")
        print_table(headers, rows)

def handle_details(args, automation: MedicalCodeAutomation) -> None:
    """Handle the details command."""
    details = automation.get_code_details(args.code)
    
    if not details:
        print(f"Code '{args.code}' not found")
        return
    
    if args.output == "json":
        print(json.dumps(details, indent=2))
    else:
        print(f"Details for code: {args.code}")
        print(f"Description: {details.get('description', 'N/A')}")
        
        price = details.get("price")
        if price is not None:
            print(f"Price: ${price}")
        else:
            print("Price: N/A")
        
        if "additional_info" in details and details["additional_info"]:
            print("\nAdditional Information:")
            for key, value in details["additional_info"].items():
                print(f"  {key}: {value}")

def handle_bulk(args, automation: MedicalCodeAutomation) -> None:
    """Handle the bulk lookup command."""
    results = automation.bulk_update_codes(args.codes)
    
    if args.output == "json":
        print(json.dumps(results, indent=2))
    else:
        if not results:
            print("No codes found")
            return
        
        headers = ["Code", "Description", "Price"]
        rows = []
        
        for code in args.codes:
            if code in results:
                details = results[code]
                price = details.get("price", "N/A")
                if price is not None:
                    price = f"${price}"
                else:
                    price = "N/A"
                    
                rows.append([
                    code,
                    details.get("description", "N/A"),
                    price
                ])
            else:
                rows.append([code, "Not found", "N/A"])
        
        print(f"Retrieved {len(results)} out of {len(args.codes)} codes")
        print_table(headers, rows)

def handle_estimate(args, automation: MedicalCodeAutomation) -> None:
    """Handle the estimate command."""
    quantities = {}
    if args.quantities:
        try:
            quantities = json.loads(args.quantities)
        except json.JSONDecodeError:
            print("Error: Invalid JSON format for quantities")
            return
    
    # Get details for all codes
    code_details = automation.bulk_update_codes(args.codes)
    
    # Calculate the estimate
    items = []
    total = 0.0
    
    for code in args.codes:
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
    
    if args.output == "json":
        print(json.dumps({
            "items": items,
            "total": total,
            "currency": "USD"
        }, indent=2))
    else:
        headers = ["Code", "Description", "Price", "Quantity", "Total"]
        rows = []
        
        for item in items:
            rows.append([
                item["code"],
                item["description"],
                f"${item['price']:.2f}",
                item["quantity"],
                f"${item['item_total']:.2f}"
            ])
        
        print("Cost Estimate")
        print_table(headers, rows)
        print("\n" + "-" * 40)
        print(f"Total: ${total:.2f} USD")

def main() -> None:
    """Run the CLI tool."""
    parser = setup_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    automation = MedicalCodeAutomation()
    
    try:
        if args.command == "search":
            handle_search(args, automation)
        elif args.command == "details":
            handle_details(args, automation)
        elif args.command == "bulk":
            handle_bulk(args, automation)
        elif args.command == "estimate":
            handle_estimate(args, automation)
    except Exception as e:
        logger.error(f"Error executing command: {str(e)}")
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 