#!/usr/bin/env python3
"""
Companion Care Medical Billing Code Streamlit Application

This script provides a user-friendly web interface for the medical billing code automation system
using Streamlit.
"""

import os
import json
import time
import streamlit as st
import pandas as pd
from medical_code_automation import MedicalCodeAutomation

# Set page configuration - MUST be the first Streamlit command
st.set_page_config(
    page_title="Companion Care Medical Billing Codes",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize the medical code automation
@st.cache_resource
def get_automation():
    return MedicalCodeAutomation()

automation = get_automation()

# Add custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #4A90E2;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #4A90E2;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #F0F7FF;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .code-box {
        background-color: #F5F5F5;
        padding: 0.5rem;
        border-radius: 0.3rem;
        font-family: monospace;
    }
    .highlight {
        color: #4A90E2;
        font-weight: bold;
    }
    .footer {
        margin-top: 3rem;
        text-align: center;
        color: #888888;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for storing data between pages
if 'search_results' not in st.session_state:
    st.session_state.search_results = None
if 'selected_codes' not in st.session_state:
    st.session_state.selected_codes = []
if 'quantities' not in st.session_state:
    st.session_state.quantities = {}
if 'estimate_results' not in st.session_state:
    st.session_state.estimate_results = None

# Sidebar navigation
st.sidebar.markdown("# Navigation")
page = st.sidebar.radio("Select a page:", [
    "Home",
    "Search Codes",
    "Code Details",
    "Cost Estimator",
    "Bulk Lookup",
    "About"
])

# Home page
if page == "Home":
    st.markdown('<div class="main-header">Companion Care Medical Billing Codes</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
    Welcome to the Companion Care Medical Billing Code Application. This tool helps you search for, 
    view details of, and estimate costs for medical billing codes (HCPCS).
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="sub-header">Features</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        - **Search Codes**: Search for medical billing codes by description or code
        - **Code Details**: View detailed information for specific codes
        - **Cost Estimator**: Estimate costs for a set of codes
        """)
    
    with col2:
        st.markdown("""
        - **Bulk Lookup**: Look up multiple codes at once
        - **Data Caching**: Fast access to frequently used codes
        - **User-Friendly Interface**: Easy to use web interface
        """)
    
    st.markdown('<div class="sub-header">Getting Started</div>', unsafe_allow_html=True)
    
    st.markdown("""
    To get started, use the navigation menu on the left to select a page:
    
    1. **Search Codes**: Search for medical billing codes by description or code
    2. **Code Details**: View detailed information for a specific code
    3. **Cost Estimator**: Estimate costs for a set of codes
    4. **Bulk Lookup**: Look up multiple codes at once
    5. **About**: Learn more about this application
    """)

# Search Codes page
elif page == "Search Codes":
    st.markdown('<div class="main-header">Search Medical Billing Codes</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
    Search for medical billing codes by description or code. For example, try searching for "wheelchair", 
    "oxygen", or "evaluation".
    </div>
    """, unsafe_allow_html=True)
    
    # Search form
    with st.form("search_form"):
        query = st.text_input("Search Query", placeholder="Enter a description or code")
        max_results = st.slider("Maximum Results", min_value=5, max_value=50, value=20, step=5)
        submitted = st.form_submit_button("Search")
        
        if submitted and query:
            with st.spinner("Searching..."):
                results = automation.search_codes(query, max_results)
                st.session_state.search_results = results
    
    # Display search results
    if st.session_state.search_results is not None:
        st.markdown(f"<div class='sub-header'>Search Results ({len(st.session_state.search_results)} found)</div>", unsafe_allow_html=True)
        
        if len(st.session_state.search_results) > 0:
            # Convert results to DataFrame for better display
            df = pd.DataFrame(st.session_state.search_results)
            
            # Add a column for adding to cost estimator
            df['Add to Estimator'] = False
            
            # Display the DataFrame with checkboxes
            edited_df = st.data_editor(
                df,
                column_config={
                    "code": "Code",
                    "description": "Description",
                    "Add to Estimator": st.column_config.CheckboxColumn(
                        "Add to Estimator",
                        help="Select to add to cost estimator",
                        default=False,
                    ),
                },
                hide_index=True,
                use_container_width=True
            )
            
            # Add selected codes to the session state
            if st.button("Add Selected Codes to Estimator"):
                selected_rows = edited_df[edited_df['Add to Estimator']]
                for _, row in selected_rows.iterrows():
                    code = row['code']
                    if code not in st.session_state.selected_codes:
                        st.session_state.selected_codes.append(code)
                        st.session_state.quantities[code] = 1
                
                st.success(f"Added {len(selected_rows)} code(s) to the estimator")
                st.balloons()
        else:
            st.info("No results found. Try a different search query.")

# Code Details page
elif page == "Code Details":
    st.markdown('<div class="main-header">Code Details</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
    View detailed information for a specific medical billing code.
    </div>
    """, unsafe_allow_html=True)
    
    # Code input
    code = st.text_input("Enter a Medical Code", placeholder="e.g., E0143")
    
    if st.button("Get Details") and code:
        with st.spinner("Getting code details..."):
            details = automation.get_code_details(code)
            
            if details:
                st.markdown(f"<div class='sub-header'>Details for Code: {code}</div>", unsafe_allow_html=True)
                
                # Create two columns for better layout
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**Code:** {details['code']}")
                    st.markdown(f"**Description:** {details['description']}")
                    
                    # Display price if available
                    price = details.get('price')
                    if price is not None:
                        st.markdown(f"**Price:** ${price}")
                    else:
                        st.markdown("**Price:** Not available")
                
                with col2:
                    # Display additional information if available
                    if 'additional_info' in details and details['additional_info']:
                        st.markdown("**Additional Information:**")
                        for key, value in details['additional_info'].items():
                            st.markdown(f"- **{key}:** {value}")
                
                # Add to estimator button
                if st.button("Add to Estimator"):
                    if details['code'] not in st.session_state.selected_codes:
                        st.session_state.selected_codes.append(details['code'])
                        st.session_state.quantities[details['code']] = 1
                        st.success(f"Added {details['code']} to the estimator")
                        st.balloons()
                    else:
                        st.info(f"Code {details['code']} is already in the estimator")
            else:
                st.error(f"Code '{code}' not found")

# Cost Estimator page
elif page == "Cost Estimator":
    st.markdown('<div class="main-header">Cost Estimator</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
    Estimate the total cost for a set of medical billing codes. You can add codes from the Search Codes page
    or enter them manually below.
    </div>
    """, unsafe_allow_html=True)
    
    # Display selected codes
    st.markdown('<div class="sub-header">Selected Codes</div>', unsafe_allow_html=True)
    
    if len(st.session_state.selected_codes) > 0:
        # Create a form for editing quantities
        with st.form("quantities_form"):
            for code in st.session_state.selected_codes:
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.markdown(f"**{code}**")
                
                with col2:
                    st.session_state.quantities[code] = st.number_input(
                        f"Quantity for {code}",
                        min_value=1,
                        value=st.session_state.quantities.get(code, 1),
                        key=f"qty_{code}"
                    )
                
                with col3:
                    if st.checkbox(f"Remove {code}", key=f"remove_{code}"):
                        st.session_state.selected_codes.remove(code)
                        del st.session_state.quantities[code]
            
            submitted = st.form_submit_button("Update Quantities")
        
        # Calculate estimate button
        if st.button("Calculate Estimate"):
            with st.spinner("Calculating estimate..."):
                # Get details for all codes
                code_details = automation.bulk_update_codes(st.session_state.selected_codes)
                
                # Calculate the estimate
                items = []
                total = 0.0
                
                for code in st.session_state.selected_codes:
                    if code in code_details:
                        details = code_details[code]
                        quantity = st.session_state.quantities.get(code, 1)
                        
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
                
                st.session_state.estimate_results = {
                    "items": items,
                    "total": total
                }
        
        # Display estimate results
        if st.session_state.estimate_results is not None:
            st.markdown('<div class="sub-header">Estimate Results</div>', unsafe_allow_html=True)
            
            # Create a DataFrame for better display
            items_df = pd.DataFrame(st.session_state.estimate_results["items"])
            
            # Format the price and item_total columns
            items_df["price"] = items_df["price"].apply(lambda x: f"${x:.2f}")
            items_df["item_total"] = items_df["item_total"].apply(lambda x: f"${x:.2f}")
            
            # Display the DataFrame
            st.dataframe(
                items_df[["code", "description", "price", "quantity", "item_total"]],
                column_config={
                    "code": "Code",
                    "description": "Description",
                    "price": "Price",
                    "quantity": "Quantity",
                    "item_total": "Total"
                },
                hide_index=True,
                use_container_width=True
            )
            
            # Display the total
            st.markdown(f"<div class='highlight'>Total: ${st.session_state.estimate_results['total']:.2f}</div>", unsafe_allow_html=True)
            
            # Download estimate as CSV
            csv = items_df.to_csv(index=False)
            st.download_button(
                label="Download Estimate as CSV",
                data=csv,
                file_name="medical_code_estimate.csv",
                mime="text/csv"
            )
            
            # Download estimate as JSON
            json_str = json.dumps(st.session_state.estimate_results, indent=2)
            st.download_button(
                label="Download Estimate as JSON",
                data=json_str,
                file_name="medical_code_estimate.json",
                mime="application/json"
            )
    else:
        st.info("No codes selected. Add codes from the Search Codes page or enter them manually below.")
        
        # Manual code entry
        st.markdown('<div class="sub-header">Add Codes Manually</div>', unsafe_allow_html=True)
        
        with st.form("manual_code_form"):
            manual_code = st.text_input("Enter a Medical Code", placeholder="e.g., E0143")
            manual_quantity = st.number_input("Quantity", min_value=1, value=1)
            submitted = st.form_submit_button("Add Code")
            
            if submitted and manual_code:
                # Check if the code exists
                details = automation.get_code_details(manual_code)
                
                if details:
                    if manual_code not in st.session_state.selected_codes:
                        st.session_state.selected_codes.append(manual_code)
                        st.session_state.quantities[manual_code] = manual_quantity
                        st.success(f"Added {manual_code} to the estimator")
                        st.balloons()
                    else:
                        st.info(f"Code {manual_code} is already in the estimator")
                else:
                    st.error(f"Code '{manual_code}' not found")

# Bulk Lookup page
elif page == "Bulk Lookup":
    st.markdown('<div class="main-header">Bulk Code Lookup</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
    Look up multiple medical billing codes at once. Enter a list of codes separated by commas, spaces, or newlines.
    </div>
    """, unsafe_allow_html=True)
    
    # Bulk code input
    bulk_codes = st.text_area("Enter Medical Codes", placeholder="e.g., E0143, K0001, E0961")
    
    if st.button("Look Up Codes") and bulk_codes:
        # Parse the input
        codes = [code.strip() for code in bulk_codes.replace(",", " ").replace("\n", " ").split() if code.strip()]
        
        if codes:
            with st.spinner(f"Looking up {len(codes)} codes..."):
                # Get details for all codes
                code_details = automation.bulk_update_codes(codes)
                
                st.markdown(f"<div class='sub-header'>Results ({len(code_details)} found)</div>", unsafe_allow_html=True)
                
                if code_details:
                    # Create a list of dictionaries for the DataFrame
                    results = []
                    for code in codes:
                        if code in code_details:
                            details = code_details[code]
                            results.append({
                                "code": code,
                                "description": details.get("description", ""),
                                "price": details.get("price", "N/A"),
                                "found": True
                            })
                        else:
                            results.append({
                                "code": code,
                                "description": "",
                                "price": "N/A",
                                "found": False
                            })
                    
                    # Convert to DataFrame for better display
                    df = pd.DataFrame(results)
                    
                    # Add a column for adding to cost estimator
                    df['Add to Estimator'] = False
                    
                    # Display the DataFrame with checkboxes
                    edited_df = st.data_editor(
                        df,
                        column_config={
                            "code": "Code",
                            "description": "Description",
                            "price": "Price",
                            "found": st.column_config.CheckboxColumn(
                                "Found",
                                help="Whether the code was found",
                                disabled=True
                            ),
                            "Add to Estimator": st.column_config.CheckboxColumn(
                                "Add to Estimator",
                                help="Select to add to cost estimator",
                                default=False,
                            ),
                        },
                        hide_index=True,
                        use_container_width=True
                    )
                    
                    # Add selected codes to the session state
                    if st.button("Add Selected Codes to Estimator"):
                        selected_rows = edited_df[edited_df['Add to Estimator']]
                        for _, row in selected_rows.iterrows():
                            code = row['code']
                            if code not in st.session_state.selected_codes and row['found']:
                                st.session_state.selected_codes.append(code)
                                st.session_state.quantities[code] = 1
                        
                        st.success(f"Added {len(selected_rows)} code(s) to the estimator")
                        st.balloons()
                else:
                    st.info("No codes found. Please check your input and try again.")
        else:
            st.error("Please enter at least one code")

# About page
elif page == "About":
    st.markdown('<div class="main-header">About</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
    This application was developed for Companion Care to automate the medical billing code process.
    It retrieves medical billing codes from the Clinical Tables NLM API and provides a user-friendly
    interface for searching, viewing details, and estimating costs.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="sub-header">Features</div>', unsafe_allow_html=True)
    
    st.markdown("""
    - **Search Codes**: Search for medical billing codes by description or code
    - **Code Details**: View detailed information for specific codes
    - **Cost Estimator**: Estimate costs for a set of codes
    - **Bulk Lookup**: Look up multiple codes at once
    - **Data Caching**: Fast access to frequently used codes
    - **User-Friendly Interface**: Easy to use web interface
    """)
    
    st.markdown('<div class="sub-header">Data Source</div>', unsafe_allow_html=True)
    
    st.markdown("""
    The medical billing codes are retrieved from the Clinical Tables NLM API:
    
    <a href="https://clinicaltables.nlm.nih.gov/apidoc/hcpcs/v3/doc.html" target="_blank">
    https://clinicaltables.nlm.nih.gov/apidoc/hcpcs/v3/doc.html
    </a>
    
    The API provides access to HCPCS (Healthcare Common Procedure Coding System) Level II codes,
    which are established by CMS's Alpha-Numeric Editorial Panel.
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="sub-header">Technologies Used</div>', unsafe_allow_html=True)
    
    st.markdown("""
    - **Python**: Programming language
    - **Streamlit**: Web application framework
    - **Pandas**: Data manipulation and analysis
    - **Requests**: HTTP library for API calls
    """)
    
    st.markdown('<div class="footer">© 2025 Companion Care. All rights reserved.</div>', unsafe_allow_html=True)

# Add a footer to all pages
st.markdown('<div class="footer">© 2025 Companion Care. All rights reserved.</div>', unsafe_allow_html=True)

def main():
    """Main function for the Streamlit application."""
    pass

if __name__ == "__main__":
    main() 