import uuid
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum


class TaskStatus(Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    SKIPPED = "SKIPPED"


class FlowStatus(Enum):
    CREATED = "CREATED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class TaskResult:
    def __init__(self, task_name: str):
        self.task_name = task_name
        self.status: Optional[TaskStatus] = None
        self.message: str = ""
        self.data: Dict[str, Any] = {}
        self.execution_time: float = 0.0
        self.timestamp: Optional[datetime] = None
        self.error: Optional[str] = None


class FlowExecutionState:
    def __init__(self, flow_id: str, flow_name: str):
        self.flow_id = flow_id
        self.flow_name = flow_name
        self.status: FlowStatus = FlowStatus.CREATED
        self.current_task: Optional[str] = None
        self.completed_tasks: List[str] = []
        self.started_at: Optional[datetime] = None
        self.ended_at: Optional[datetime] = None
        self.task_results: Dict[str, TaskResult] = {}


class FlowManager:
    def __init__(self):
        self.flows: Dict[str, FlowExecutionState] = {}
        self.flow_configs: Dict[str, Dict[str, Any]] = {}

    def load_flow_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        if "id" not in config or "name" not in config or "tasks" not in config:
            raise ValueError("Flow config missing required 'id', 'name' or 'tasks'")
        return config

    def create_flow_execution(self, flow_config: Dict[str, Any]) -> str:
        execution_id = str(uuid.uuid4())
        flow_name = flow_config.get("name", "UnnamedFlow")
        self.flow_configs[execution_id] = flow_config
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
                await asyncio.sleep(0.5)  # Simulate processing delay

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

