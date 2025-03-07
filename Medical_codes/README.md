# Companion Care Medical Billing Code Automation

This system automates the retrieval and management of medical billing codes (HCPCS) from the Clinical Tables NLM API and provides functionality to relay this information to the end user through an API.

## Features

- Retrieve medical billing codes from the Clinical Tables NLM API
- Search for codes by description or code
- Get detailed information for specific codes
- Bulk lookup of multiple codes
- Estimate costs for a set of codes
- Automated cache updates to ensure up-to-date information
- REST API for integration with front-end applications
- Command-line interface for direct interaction
- User-friendly Streamlit web application

## Components

The system consists of the following components:

1. **Medical Code Automation Core** (`medical_code_automation.py`): The core functionality for retrieving and processing medical billing codes.
2. **API Server** (`api_server.py`): A REST API for the front-end application to interact with the medical code automation system.
3. **CLI Tool** (`cli_tool.py`): A command-line interface for interacting with the medical code automation system.
4. **Automation Scheduler** (`automation_scheduler.py`): A scheduler that periodically updates the code cache to ensure up-to-date information.
5. **Streamlit Web Application** (`streamlit_app.py`): A user-friendly web interface for searching, viewing details, and estimating costs.

## Installation

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Set up environment variables (optional):

Create a `.env` file in the `Medical_codes` directory with the following variables:

```
PORT=8000
DEBUG=False
```

## Usage

### API Server

Start the API server:

```bash
python api_server.py
```

The API server will be available at `http://localhost:8000` (or the port specified in the environment variables).

#### API Endpoints

- `GET /health`: Health check endpoint
- `GET /api/codes/search?q=<query>&max_results=<max_results>`: Search for codes
- `GET /api/codes/<code>`: Get details for a specific code
- `POST /api/codes/bulk`: Look up multiple codes at once
- `POST /api/codes/estimate`: Estimate the total cost for a set of codes

### CLI Tool

The CLI tool provides a command-line interface for interacting with the medical code automation system.

```bash
# Search for codes
python cli_tool.py search "wheelchair" --max-results 10 --output json

# Get details for a specific code
python cli_tool.py details E0143 --output table

# Look up multiple codes at once
python cli_tool.py bulk E0143 E0250 E0601 --output table

# Estimate cost for a set of codes
python cli_tool.py estimate E0143 E0250 E0601 --quantities '{"E0143": 2, "E0250": 1, "E0601": 1}' --output table
```

### Automation Scheduler

The automation scheduler periodically updates the code cache to ensure up-to-date information.

```bash
# Start the scheduler
python automation_scheduler.py

# Run a full update once and exit
python automation_scheduler.py --run-once

# Add a code to the list of common codes
python automation_scheduler.py --add-code E0143

# Remove a code from the list of common codes
python automation_scheduler.py --remove-code E0143

# List all common codes
python automation_scheduler.py --list-codes
```

### Streamlit Web Application

The Streamlit web application provides a user-friendly interface for searching, viewing details, and estimating costs for medical billing codes.

```bash
# Run the Streamlit application
python streamlit_app.py
```

The application will be available at `http://localhost:8501` in your web browser.

#### Features

- **Search Codes**: Search for medical billing codes by description or code
- **Code Details**: View detailed information for specific codes
- **Cost Estimator**: Estimate costs for a set of codes
- **Bulk Lookup**: Look up multiple codes at once
- **User-Friendly Interface**: Easy to use web interface

## Integration with Front-end Applications

The API server provides a REST API that can be used to integrate with front-end applications. Here's an example of how to use the API with JavaScript:

```javascript
// Search for codes
fetch('http://localhost:8000/api/codes/search?q=wheelchair&max_results=10')
  .then(response => response.json())
  .then(data => console.log(data));

// Get details for a specific code
fetch('http://localhost:8000/api/codes/E0143')
  .then(response => response.json())
  .then(data => console.log(data));

// Look up multiple codes at once
fetch('http://localhost:8000/api/codes/bulk', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    codes: ['E0143', 'E0250', 'E0601']
  })
})
  .then(response => response.json())
  .then(data => console.log(data));

// Estimate cost for a set of codes
fetch('http://localhost:8000/api/codes/estimate', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    codes: ['E0143', 'E0250', 'E0601'],
    quantities: {
      'E0143': 2,
      'E0250': 1,
      'E0601': 1
    }
  })
})
  .then(response => response.json())
  .then(data => console.log(data));
```

## Data Caching

The system caches code data to reduce API calls and improve performance. The cache is stored in the `code_cache.json` file in the `Medical_codes` directory.

## Common Codes

The system maintains a list of commonly used codes that are periodically updated. The list is stored in the `common_codes.json` file in the `Medical_codes` directory.

## Logging

The system logs information to the following files:

- `medical_code_automation.log`: Logs from the core automation system
- `api_server.log`: Logs from the API server
- `cli_tool.log`: Logs from the CLI tool
- `automation_scheduler.log`: Logs from the automation scheduler

## License

This project is licensed under the MIT License. 