# Python Backend Flow Manager System

A microservice for managing sequential task execution with conditional flow control, built with FastAPI and Python.

## 🚀 Features

- **Sequential Task Execution**: Tasks execute one after another in a controlled manner
- **Conditional Flow Control**: Dynamic flow routing based on task success/failure
- **Generic Architecture**: Support for any number of tasks and conditions
- **RESTful API**: Complete microservice with FastAPI
- **Real-time Monitoring**: Track flow execution status and task results
- **Error Handling**: Comprehensive error management and recovery
- **Async Processing**: Non-blocking task execution with asyncio
- **Extensible Design**: Easy to add new task types

## 📋 Project Structure

```
flow_manager/
├── models.py              # Data models and enums
├── tasks.py              # Task implementations  
├── flow_manager.py       # Core flow management logic
├── api.py               # FastAPI microservice
├── test_flow_manager.py # Test scripts
├── requirements.txt     # Dependencies
├── sample_config.json   # Example flow configuration
└── README.md           # This file
```

## 🏗️ Architecture Overview

The Flow Manager system consists of several key components:

### Core Components

1. **Flow Manager Core**: Orchestrates the entire flow execution process
2. **Task Registry**: Factory pattern for creating and managing task instances  
3. **Condition Evaluator**: Evaluates task results against defined conditions
4. **State Manager**: Tracks flow execution state and task results
5. **API Layer**: FastAPI-based REST endpoints
6. **Configuration Loader**: Parses JSON flow configurations

### Design Patterns Used

- **Factory Pattern**: Task creation and instantiation
- **Strategy Pattern**: Different task implementations
- **Chain of Responsibility**: Sequential task execution
- **State Pattern**: Flow state management

## 💻 Installation

### Prerequisites

- Python 3.8+
- pip package manager

### Install Dependencies

```bash
pip install -r requirements.txt
```

## 🚦 Quick Start

### 1. Start the Microservice

```bash
python api.py
```

The API will be available at `http://localhost:8000`

### 2. View API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 3. Execute a Flow

```bash
curl -X POST "http://localhost:8000/flow/execute-sync" \
  -H "Content-Type: application/json" \
  -d @sample_config.json
```

### 4. Run Tests

```bash
python test_flow_manager.py
```

## 🎯 Flow Design Explanation

### How Tasks Depend on Each Other

Tasks in the flow manager system have a **sequential dependency** structure:

1. **Linear Execution**: Tasks execute one after another, never in parallel
2. **Data Flow**: Each task can access results from previously completed tasks
3. **Conditional Dependencies**: The next task to execute depends on the current task's result
4. **Context Sharing**: Task results are passed through a shared context object

### Task Success/Failure Evaluation

Each task execution is evaluated based on:

1. **Task Result Status**: 
   - `SUCCESS`: Task completed without errors
   - `FAILURE`: Task encountered an error or failed validation
   - `SKIPPED`: Task was not executed due to flow conditions

2. **Evaluation Criteria**:
   - Exception handling during task execution
   - Return value validation  
   - Custom business logic checks
   - Resource availability and constraints

### What Happens on Success/Failure

#### On Task Success:
1. Store task result in execution context
2. Evaluate associated condition for the task
3. Determine next task based on condition configuration
4. Continue to next task or end flow if no more tasks

#### On Task Failure:
1. Store error details and failure status
2. Evaluate failure condition (if defined)
3. Either:
   - End the flow immediately (default behavior)
   - Route to error handling task
   - Retry the failed task (if configured)

## 📚 API Documentation

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information and endpoint list |
| GET | `/health` | Health check |
| POST | `/flow/create` | Create a new flow from configuration |
| POST | `/flow/execute` | Execute a flow asynchronously |
| POST | `/flow/execute-sync` | Execute a flow synchronously |
| GET | `/flow/{id}/status` | Get flow execution status |
| GET | `/flows` | List all flows |
| GET | `/flows/summary` | Get flow summary statistics |

## 📖 Usage Examples

### Basic Flow Configuration

```json
{
  "flow": {
    "id": "data_processing_flow",
    "name": "Data Processing Pipeline", 
    "start_task": "task1",
    "tasks": [
      {
        "name": "task1",
        "description": "Fetch data from external API",
        "task_type": "fetch_data"
      },
      {
        "name": "task2", 
        "description": "Process and transform data",
        "task_type": "process_data"
      },
      {
        "name": "task3",
        "description": "Store processed data",
        "task_type": "store_data"
      }
    ],
    "conditions": [
      {
        "name": "fetch_condition",
        "description": "Continue to processing if fetch succeeds",
        "source_task": "task1",
        "outcome": "success",
        "target_task_success": "task2",
        "target_task_failure": "end"
      }
    ]
  }
}
```

### Python API Usage

```python
import asyncio
from flow_manager import FlowManager

async def example_usage():
    # Initialize flow manager
    manager = FlowManager()

    # Load configuration from JSON
    flow_config = manager.load_flow_config(config_dict)

    # Create and execute flow
    execution_id = manager.create_flow_execution(flow_config)
    result = await manager.execute_flow(execution_id, flow_config)

    print(f"Flow completed with status: {result.status}")

asyncio.run(example_usage())
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
python test_flow_manager.py
```

This will test:
- Core flow manager functionality
- Task execution and condition evaluation
- Error handling and failure scenarios
- API integration (if server is running)

## 🚀 Extending the System

### Adding New Task Types

1. Create a new task class inheriting from `BaseTask`:

```python
from models import BaseTask, TaskResult, TaskStatus

class CustomTask(BaseTask):
    async def execute(self, context: Dict[str, Any] = None) -> TaskResult:
        # Implement your task logic
        return TaskResult(
            task_name=self.name,
            status=TaskStatus.SUCCESS,
            message="Custom task completed"
        )
```

2. Register the task in the TaskFactory:

```python
from flow_manager import TaskFactory
TaskFactory.register_task('custom_task', CustomTask)
```

## 🔧 Configuration

Tasks can be configured with custom parameters:

```json
{
  "name": "fetch_data",
  "description": "Fetch data with custom settings",
  "task_type": "fetch_data",
  "parameters": {
    "data_source": "https://api.example.com/data",
    "timeout": 30,
    "retry_count": 3,
    "failure_rate": 0.1
  }
}
```

## 📊 Monitoring and Observability

The system provides built-in monitoring capabilities:

- **Real-time Status**: Track flow execution progress
- **Task Metrics**: Execution time, success/failure rates  
- **Error Tracking**: Detailed error messages and stack traces
- **Flow History**: Complete audit trail of all executions

Access monitoring through the API:
- `GET /flows/summary` - Overall system statistics
- `GET /flow/{id}/status` - Individual flow status
- `GET /flow/{id}/tasks/{name}/result` - Specific task results

## 📄 Implementation Details

### Code Implementation

The system consists of four main Python modules:

1. **`models.py`**: Defines data structures, enums, and base classes
2. **`tasks.py`**: Contains concrete task implementations (Fetch, Process, Store)
3. **`flow_manager.py`**: Core orchestration engine with TaskFactory and ConditionEvaluator
4. **`api.py`**: FastAPI microservice providing RESTful endpoints

### Example Tasks

The system includes three example tasks:

- **FetchDataTask**: Simulates fetching data from external sources
- **ProcessDataTask**: Transforms and processes data from previous tasks
- **StoreDataTask**: Stores processed data to a destination

Each task can be configured with parameters like failure rates for testing different scenarios.

