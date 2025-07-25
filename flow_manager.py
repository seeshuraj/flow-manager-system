import uuid
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum
<<<<<<< HEAD
=======

class TaskStatus(Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    SKIPPED = "SKIPPED"
>>>>>>> 2a487aa (Docker container created)

class FlowStatus(Enum):
    CREATED = "CREATED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

<<<<<<< HEAD
class TaskStatus(Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    SKIPPED = "SKIPPED"


class FlowStatus(Enum):
    CREATED = "CREATED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


=======
>>>>>>> 2a487aa (Docker container created)
class TaskResult:
    def __init__(self, task_name: str):
        self.task_name = task_name
        self.status = None  # TaskStatus enum
        self.message = ""
        self.data = {}
<<<<<<< HEAD
        self.execution_time = None
        self.timestamp = None
        self.error = None


class FlowExecutionState:
    def __init__(self, flow_id: str, flow_name: str):
        self.flow_id = flow_id
        self.flow_name = flow_name
        self.status = FlowStatus.CREATED
        self.current_task = None
        self.completed_tasks = []
        self.started_at = None
        self.ended_at = None
        self.task_results: Dict[str, TaskResult] = {}
=======
        self.execution_time = 0.0
        self.timestamp = None
        self.error = None
>>>>>>> 2a487aa (Docker container created)

class FlowExecutionState:
    def __init__(self, flow_id: str, flow_name: str):
        self.flow_id = flow_id
        self.flow_name = flow_name
        self.status = FlowStatus.CREATED
        self.current_task = None
        self.completed_tasks = []
        self.started_at = None
        self.ended_at = None
        self.task_results: Dict[str, TaskResult] = {}

class FlowManager:
    def __init__(self):
        self.flows: Dict[str, FlowExecutionState] = {}
        self.flow_configs: Dict[str, Dict[str, Any]] = {}

    def load_flow_config(self, config: Dict[str, Any]):
<<<<<<< HEAD
        # Validate minimal required fields (expand as needed)
        if "id" not in config or "name" not in config or "tasks" not in config:
            raise ValueError("Flow config missing required 'id', 'name' or 'tasks'")
        return config  # In real code, parse/validate with Pydantic or similar

    def create_flow_execution(self, flow_config: Dict[str, Any]) -> str:
        execution_id = str(uuid.uuid4())
        flow_id = flow_config["id"]
        flow_name = flow_config.get("name", "UnnamedFlow")

        # Save config so it can be used during execution
        self.flow_configs[execution_id] = flow_config

        # Initialize execution state
=======
        if "id" not in config or "name" not in config or "tasks" not in config:
            raise ValueError("Flow config missing required 'id', 'name' or 'tasks'")
        return config

    def create_flow_execution(self, flow_config: Dict[str, Any]) -> str:
        execution_id = str(uuid.uuid4())
        flow_name = flow_config.get("name", "UnnamedFlow")
        self.flow_configs[execution_id] = flow_config
>>>>>>> 2a487aa (Docker container created)
        state = FlowExecutionState(flow_id=execution_id, flow_name=flow_name)
        self.flows[execution_id] = state
        return execution_id

    def get_flow_status(self, execution_id: str) -> Optional[FlowExecutionState]:
        return self.flows.get(execution_id)

    def get_flow_config(self, execution_id: str) -> Optional[Dict[str, Any]]:
        return self.flow_configs.get(execution_id)

    def remove_flow(self, execution_id: str) -> bool:
        existed = False
        if execution_id in self.flows:
            del self.flows[execution_id]
            existed = True
        if execution_id in self.flow_configs:
            del self.flow_configs[execution_id]
            existed = True
        return existed

<<<<<<< HEAD
    def get_all_flows(self) -> Dict[str, FlowExecutionState]:
        return self.flows

    def get_flow_summary(self) -> Dict[str, Any]:
        counts = {status.value: 0 for status in FlowStatus}
        for f in self.flows.values():
            counts[f.status.value] += 1
        return {
            "total_flows": len(self.flows),
            "status_counts": counts,
            "registered_task_types": []  # Add logic if needed
        }

    async def execute_flow(self, execution_id: str, flow_config: Dict[str, Any]) -> FlowExecutionState:
        if execution_id not in self.flows:
            raise ValueError("Execution ID not found")

        state = self.flows[execution_id]
        state.status = FlowStatus.RUNNING
        state.started_at = datetime.utcnow()
        tasks = flow_config["tasks"]

        # Simplified sequential execution simulation
        for task in tasks:
            task_name = task["name"]
            state.current_task = task_name

            # Create and add a TaskResult
            task_result = TaskResult(task_name=task_name)
            try:
                # Simulate task execution delay
                await asyncio.sleep(0.5)

                # Simulate success/failure based on failure_rate param
                failure_rate = task.get("parameters", {}).get("failure_rate", 0)
                import random
                if random.random() < failure_rate:
                    raise RuntimeError(f"Simulated failure in {task_name}")

                task_result.status = TaskStatus.SUCCESS
                task_result.message = "Completed successfully"
                task_result.data = {"info": f"Result of {task_name}"}
            except Exception as e:
                task_result.status = TaskStatus.FAILURE
                task_result.error = str(e)
                state.status = FlowStatus.FAILED
                state.task_results[task_name] = task_result
                state.ended_at = datetime.utcnow()
                return state

            # Save result
            task_result.timestamp = datetime.utcnow()
            state.task_results[task_name] = task_result
            state.completed_tasks.append(task_name)

        state.status = FlowStatus.COMPLETED
        state.current_task = None
        state.ended_at = datetime.utcnow()
        return state
=======
    async def execute_flow(self, execution_id: str, flow_config: Dict[str, Any]) -> FlowExecutionState:
        if execution_id not in self.flows:
            raise ValueError("Execution ID not found")

        state = self.flows[execution_id]
        state.status = FlowStatus.RUNNING
        state.started_at = datetime.utcnow()
        tasks = flow_config["tasks"]

        for task in tasks:
            task_name = task["name"]
            state.current_task = task_name

            task_result = TaskResult(task_name=task_name)
            try:
                await asyncio.sleep(0.5)

                failure_rate = task.get("parameters", {}).get("failure_rate", 0)
                import random
                if random.random() < failure_rate:
                    raise RuntimeError(f"Simulated failure in {task_name}")

                task_result.status = TaskStatus.SUCCESS
                task_result.message = "Completed successfully"
                task_result.data = {"info": f"Result of {task_name}"}
            except Exception as e:
                task_result.status = TaskStatus.FAILURE
                task_result.error = str(e)
                state.task_results[task_name] = task_result
                state.status = FlowStatus.FAILED
                state.ended_at = datetime.utcnow()
                return state

            task_result.timestamp = datetime.utcnow()
            state.task_results[task_name] = task_result
            state.completed_tasks.append(task_name)

        all_success = all(tr.status == TaskStatus.SUCCESS for tr in state.task_results.values())
        state.status = FlowStatus.COMPLETED if all_success else FlowStatus.FAILED
        state.current_task = None
        state.ended_at = datetime.utcnow()

        return state

>>>>>>> 2a487aa (Docker container created)
