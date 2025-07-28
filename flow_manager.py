import uuid
import asyncio
import importlib
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

# Configure logging at the module level
logging.basicConfig(
    level=logging.DEBUG,  # Adjust this to INFO or WARNING in production
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


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
        for task in config["tasks"]:
            if "task_type" not in task:
                raise ValueError(f"Task '{task.get('name', '')}' missing 'task_type'")
        return config

    def create_flow_execution(self, flow_config: Dict[str, Any]) -> str:
        execution_id = str(uuid.uuid4())
        flow_name = flow_config.get("name", "UnnamedFlow")
        self.flow_configs[execution_id] = flow_config
        state = FlowExecutionState(flow_id=execution_id, flow_name=flow_name)
        self.flows[execution_id] = state
        logger.info(f"Created new flow execution: {execution_id} for flow '{flow_name}'")
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
            logger.info(f"Deleted flow state for execution ID {execution_id}")
        if execution_id in self.flow_configs:
            del self.flow_configs[execution_id]
            logger.info(f"Deleted flow config for execution ID {execution_id}")
            existed = True
        return existed

    async def execute_flow(self, execution_id: str, flow_config: Dict[str, Any]) -> FlowExecutionState:
        if execution_id not in self.flows:
            raise ValueError("Execution ID not found")

        state = self.flows[execution_id]
        state.status = FlowStatus.RUNNING
        state.started_at = datetime.utcnow()
        logger.info(f"Started execution of flow '{state.flow_name}' with ID {execution_id}")

        tasks = flow_config["tasks"]

        for task in tasks:
            task_name = task["name"]
            task_type = task["task_type"]
            parameters = task.get("parameters", {})

            state.current_task = task_name
            task_result = TaskResult(task_name=task_name)

            try:
                logger.debug(f"Loading task '{task_name}' of type '{task_type}' with parameters {parameters}")
                module_name = f"tasks.task_{task_type.lower()}"
                class_name = ''.join(part.capitalize() for part in task_type.split('_')) + "Task"
                module = importlib.import_module(module_name)
                task_class = getattr(module, class_name)
                logger.debug(f"Instantiating {class_name} from {module_name}")

                task_instance = task_class(name=task_name, parameters=parameters)
                logger.debug(f"Executing task '{task_name}'...")
                result_data = await task_instance.run()
                logger.info(f"Task '{task_name}' completed successfully with result: {result_data}")

                task_result.status = TaskStatus.SUCCESS
                task_result.message = "Completed successfully"
                task_result.data = result_data

            except Exception as e:
                logger.error(f"Task '{task_name}' failed with error: {e}")
                task_result.status = TaskStatus.FAILURE
                task_result.error = str(e)
                state.task_results[task_name] = task_result
                state.status = FlowStatus.FAILED
                state.ended_at = datetime.utcnow()
                logger.warning(f"Flow execution {execution_id} failed during task '{task_name}'")
                return state

            task_result.timestamp = datetime.utcnow()
            state.task_results[task_name] = task_result
            state.completed_tasks.append(task_name)

        all_success = all(tr.status == TaskStatus.SUCCESS for tr in state.task_results.values())
        state.status = FlowStatus.COMPLETED if all_success else FlowStatus.FAILED
        state.current_task = None
        state.ended_at = datetime.utcnow()
        logger.info(f"Flow execution {execution_id} completed with status {state.status.value}")

        return state

