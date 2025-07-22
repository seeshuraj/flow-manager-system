"""
Flow Manager Models

This module defines the core data models, enums, and data structures
used throughout the flow manager system.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from datetime import datetime
from abc import ABC, abstractmethod


class TaskStatus(Enum):
    """Enumeration for task execution status"""
    PENDING = "pending"
    RUNNING = "running" 
    SUCCESS = "success"
    FAILURE = "failure"
    SKIPPED = "skipped"


class FlowStatus(Enum):
    """Enumeration for flow execution status"""
    CREATED = "created"
    RUNNING = "running"
    SUCCESS = "success"
    FAILURE = "failure"
    ENDED = "ended"


@dataclass
class TaskResult:
    """Represents the result of a task execution"""
    task_name: str
    status: TaskStatus
    message: str = ""
    data: Dict[str, Any] = None
    execution_time: Optional[float] = None
    timestamp: Optional[datetime] = None
    error: Optional[str] = None

    def __post_init__(self):
        if self.data is None:
            self.data = {}
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class FlowExecutionState:
    """Represents the current state of flow execution"""
    flow_id: str
    flow_name: str
    current_task: Optional[str] = None
    status: FlowStatus = FlowStatus.CREATED
    completed_tasks: list = None
    task_results: Dict[str, TaskResult] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None

    def __post_init__(self):
        if self.completed_tasks is None:
            self.completed_tasks = []
        if self.task_results is None:
            self.task_results = {}
        if self.started_at is None:
            self.started_at = datetime.now()


@dataclass
class TaskConfig:
    """Configuration for a single task"""
    name: str
    description: str
    task_type: str = "generic"
    parameters: Dict[str, Any] = None

    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}


@dataclass
class ConditionConfig:
    """Configuration for a condition that determines flow control"""
    name: str
    description: str
    source_task: str
    outcome: str  # "success" or "failure"
    target_task_success: str
    target_task_failure: str


@dataclass
class FlowConfig:
    """Configuration for an entire flow"""
    id: str
    name: str
    start_task: str
    tasks: List[TaskConfig]
    conditions: List[ConditionConfig]

    def get_task_by_name(self, task_name: str) -> Optional[TaskConfig]:
        """Get task configuration by name"""
        for task in self.tasks:
            if task.name == task_name:
                return task
        return None

    def get_condition_for_task(self, task_name: str) -> Optional[ConditionConfig]:
        """Get condition configuration for a specific task"""
        for condition in self.conditions:
            if condition.source_task == task_name:
                return condition
        return None


class BaseTask(ABC):
    """Abstract base class for all tasks"""

    def __init__(self, config: TaskConfig):
        self.config = config
        self.name = config.name
        self.description = config.description
        self.parameters = config.parameters

    @abstractmethod
    async def execute(self, context: Dict[str, Any] = None) -> TaskResult:
        """Execute the task and return result"""
        pass

    def validate_parameters(self) -> bool:
        """Validate task parameters before execution"""
        return True
