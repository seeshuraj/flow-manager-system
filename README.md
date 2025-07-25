# Flow Manager System

A powerful backend system to define, execute, and monitor task flows with conditional logic. Built using Python and FastAPI, this microservice enables flexible orchestration of sequential and dependent tasks via a REST API.

---

## Overview

The Flow Manager allows you to design workflows consisting of multiple tasks and conditional paths. Each flow can be created, executed asynchronously, and tracked for real-time status updates.

Key features include:

- Create and configure task flows with conditions.
- Execute flows and monitor individual task statuses.
- REST API endpoints to manage flow lifecycle.
- Background execution with task result aggregation.
- Error handling and failure propagation.
- Automated tests for core functionality and API integration.
- Dockerized for easy deployment and development.

---

## Getting Started

### Prerequisites

- Python 3.10+
- `pip` (Python package manager)
- Optional: Docker (for containerized deployment)

### Installation

1. Clone the repository:

    ```
    git clone https://github.com/seeshuraj/flow-manager-system.git
    cd flow-manager-system
    ```

2. (Optional) Create and activate a virtual environment:

    ```
    python3 -m venv venv
    source venv/bin/activate
    ```

3. Install dependencies:

    ```
    pip install -r requirements.txt
    ```

### Running the API Server

Start the FastAPI server locally using Uvicorn:
```
uvicorn api:app --reload
```

The server will be available at `http://localhost:8000`.

You can visit `http://localhost:8000/docs` to explore the interactive API documentation and test endpoints directly.

### Running Tests

Tests use `asyncio` to run flow manager functionality and API integration checks.

Run the tests with:
```
python3 test_flow_manager.py
```

Make sure the API server is running (see above) before running tests to allow API integration tests to pass.

---

## Usage

The API exposes a set of endpoints for managing flows:

- **`POST /flow/create`** - Create a new flow from a JSON configuration.
- **`POST /flow/execute`** - Trigger asynchronous execution of a flow.
- **`GET /flow/{execution_id}/status`** - Get the status and results of an ongoing or completed flow execution.
- **`DELETE /flow/{execution_id}`** - Delete a flow execution and related data.
- **`GET /health`** - Health check endpoint.

Example of a flow JSON config payload is documented in the API docs and includes tasks, conditions, and start task information.

---

## Docker Usage

For simplified deployment, you can use Docker.

Build the Docker image:

```
docker build -t flow-manager 
```

Run the container:
```
Run the container:
```

Access the API at `http://localhost:8000`.

---

## Project Structure

- `api.py` - FastAPI application defining API endpoints.
- `flow_manager.py` - Core logic for loading flows, managing executions, and task orchestration.
- `models.py` - Enum definitions and data models for tasks and flow statuses.
- `test_flow_manager.py` - Async test script validating main flow execution and API integration.
- `Dockerfile` - Containerization instructions.
- `requirements.txt` - Python dependencies list.

---

## Contribution

Contributions and suggestions are welcome! Please open issues or pull requests as needed.

---

## Future Enhancements

- Persistent storage for flow and execution data.
- User authentication and authorization for API endpoints.
- A web UI dashboard for visual flow composition and monitoring.
- Integration with message queues or external triggers.

---


