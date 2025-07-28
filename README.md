# Flow Manager System

A FastAPI-powered backend microservice for defining, executing, and monitoring generic task flows with conditional logic.

---

## Features

- Define task flows with conditional branching
- Execute flows asynchronously via REST API
- Monitor execution status and see detailed results
- Automated and manual testing
- Dockerized for easy deployment

---

## Quick Start

1. **Clone the repository:**
    ```
    git clone https://github.com/seeshuraj/flow-manager-system.git
    cd flow-manager-system
    ```

2. **Set up virtual environment:**
    ```
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

3. **Run the API server:**
    ```
    uvicorn api:app --reload
    ```
    Visit [http://localhost:8000/docs](http://localhost:8000/docs) for API docs.

4. **Run tests:**
    ```
    python test_flow_manager.py
    ```

---

## Example API Usage

- Create a flow: `POST /flow/create` (with JSON flow config)
- Execute a flow: `POST /flow/execute`
- Check status: `GET /flow/{execution_id}/status`
- Health check: `GET /health`

---

## Docker Usage

Build and run:

```
docker build -t flow-manager .
docker run -p 8000:8000 flow-manager
```
---
