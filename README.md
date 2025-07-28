# Flow Manager System

A FastAPI-powered backend microservice for defining, executing, and monitoring generic task flows with conditional logic.

## Features

- **Dynamic Task Loading:** Implement new tasks just by adding new modules to the `tasks/` folder—no need to touch core code.
- **Conditional Branching:** Structure flows with task success/failure handling.
- **Asynchronous Execution:** Tasks run asynchronously for efficiency.
- **REST API:** Create, start, monitor, and delete flows with robust endpoints.
- **Automated Testing:** Pytest suite covers flow logic and API integration.
- **Logging:** All core operations, task loads, and errors are logged.
- **Dockerized:** Build and run as an isolated container.

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
    Visit [http://localhost:8000/docs](http://localhost:8000/docs) for interactive API documentation.

4. **Run all tests:**
    ```
    python test_flow_manager.py
    PYTHONPATH=. pytest tests/
    ```
    > All tests must pass to ensure your setup is correct.

## Example API Usage

- **Create a flow:**  
  `POST /flow/create`  
  *(Body: JSON defining the flow with "id", "tasks" (with "task_type"), etc.)*
- **Execute a flow:**  
  `POST /flow/execute`  
  *(Body: `{ "execution_id": "<flow-exec-id>" }`)*
- **Check flow status:**  
  `GET /flow/{execution_id}/status`
- **Delete a flow execution:**  
  `DELETE /flow/{execution_id}`
- **Health check:**  
  `GET /health`

## Dynamic Tasks

- Place all pluggable task implementations in the `tasks/` directory.
- Each task must be a Python file `task_<task_type>.py` with a class `<TaskType>Task` inheriting from `BaseTask`.
- Example task modules:  
  - `tasks/task_fetch_data.py`   →  `FetchDataTask`
  - `tasks/task_process_data.py` →  `ProcessDataTask`
  - `tasks/task_store_data.py`   →  `StoreDataTask`
- Each task's `run()` method executes asynchronously and returns results or raises exceptions to signal failure.

## Flow Configuration Example (JSON)

```
{
"id": "example_flow",
"name": "Sample Data Pipeline",
"start_task": "task1",
"tasks": [
{ "name": "task1", "task_type": "fetch_data", "parameters": { "failure_rate": 0 } },
{ "name": "task2", "task_type": "process_data", "parameters": { "failure_rate": 0 } },
{ "name": "task3", "task_type": "store_data", "parameters": { "failure_rate": 0 } }
],
"conditions": []
}
```

## Docker Usage

Build and run in a container:
```
docker build -t flow-manager .
docker run -p 8000:8000 flow-manager
```
The app will be available at [http://localhost:8000/docs](http://localhost:8000/docs).

## Project Structure
flow-manager-system/
├── api.py
├── flow_manager.py
├── requirements.txt
├── Dockerfile
├── sample_flow.json
├── tasks/
│ ├── init.py
│ ├── base_task.py
│ ├── task_fetch_data.py
│ ├── task_process_data.py
│ ├── task_store_data.py
│ └── ...
├── tests/
│ ├── test_api_integration.py
│ ├── test_flow_failure.py
│ └── test_flow_success.py
└── README.md


## Testing

- Run all core and API tests after any changes:
```
python test_flow_manager.py
PYTHONPATH=. pytest tests/
```
