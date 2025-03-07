# Companion Care Medical Billing Code Automation

This system automates the retrieval and management of medical billing codes (HCPCS) from the Clinical Tables NLM API and provides functionality to relay this information to the end user through an API.

## Quick Start

You can run the system from the root directory using the following wrapper scripts:

```bash
# Start the API server
python api_server.py

# Use the CLI tool
python cli_tool.py search "wheelchair"

# Run the automation scheduler
python automation_scheduler.py

# Run the example usage script
python example_usage.py

# Use the start script to start multiple components
python start.py all

# Run the Streamlit web application
python streamlit_app.py

# Run all components at once (API server and Streamlit app)
python run_all.py
```

## Streamlit Web Application

The Streamlit web application provides a user-friendly interface for searching, viewing details, and estimating costs for medical billing codes. To run the application:

```bash
python streamlit_app.py
```

The application will be available at http://localhost:8501 in your web browser.

### Features

- **Search Codes**: Search for medical billing codes by description or code
- **Code Details**: View detailed information for specific codes
- **Cost Estimator**: Estimate costs for a set of codes
- **Bulk Lookup**: Look up multiple codes at once
- **User-Friendly Interface**: Easy to use web interface

## Running All Components

To run all components at once (API server and Streamlit web application), use the run_all.py script:

```bash
python run_all.py
```

This will:
1. Start the API server on port 8000
2. Start the Streamlit web application on port 8501
3. Open the Streamlit web application in your default web browser

To stop all components, press Ctrl+C in the terminal.

## Documentation

For detailed documentation, please see the [Medical_codes/README.md](Medical_codes/README.md) file.

## Installation

1. Install the required dependencies:

```bash
pip install -r Medical_codes/requirements.txt
```

2. Set up environment variables (optional):

Create a `.env` file in the `Medical_codes` directory with the following variables:

```
PORT=8000
DEBUG=False
```

## Components

The system consists of the following components:

1. **Medical Code Automation Core**: The core functionality for retrieving and processing medical billing codes.
2. **API Server**: A REST API for the front-end application to interact with the medical code automation system.
3. **CLI Tool**: A command-line interface for interacting with the medical code automation system.
4. **Automation Scheduler**: A scheduler that periodically updates the code cache to ensure up-to-date information.
5. **Streamlit Web Application**: A user-friendly web interface for searching, viewing details, and estimating costs.

## API Endpoints

- `GET /health`: Health check endpoint
- `GET /api/codes/search?q=<query>&max_results=<max_results>`: Search for codes
- `GET /api/codes/<code>`: Get details for a specific code
- `POST /api/codes/bulk`: Look up multiple codes at once
- `POST /api/codes/estimate`: Estimate the total cost for a set of codes

## License

This project is licensed under the MIT License. 