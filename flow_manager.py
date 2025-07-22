"""
Flow Manager Core

This module contains the core flow management logic including the FlowManager class,
TaskFactory, and ConditionEvaluator that orchestrate task execution.
"""

import asyncio
import json
import uuid
from typing import Dict, Any, Optional, Type
from datetime import datetime

from models import (
    BaseTask, TaskResult, TaskStatus, FlowStatus, 
    TaskConfig, ConditionConfig, FlowConfig, FlowExecutionState
)
from tasks import FetchDataTask, ProcessDataTask, StoreDataTask


class TaskFactory:
    """Factory to create task instances based on configuration"""

    _task_registry: Dict[str, Type[BaseTask]] = {
        'fetch_data': FetchDataTask,
        'process_data': ProcessDataTask,
        'store_data': StoreDataTask,
    }

    @classmethod
    def register_task(cls, task_type: str, task_class: Type[BaseTask]):
        """Register a new task type"""
        cls._task_registry[task_type] = task_class

    @classmethod
    def create_task(cls, config: TaskConfig) -> BaseTask:
        """Create a task instance from configuration"""
        task_class = cls._task_registry.get(config.task_type)
        if not task_class:
            raise ValueError(f"Unknown task type: {config.task_type}")
        return task_class(config)

    @classmethod
    def get_registered_tasks(cls) -> Dict[str, Type[BaseTask]]:
        """Get all registered task types"""
        return cls._task_registry.copy()


class ConditionEvaluator:
    """Evaluates conditions to determine flow control"""

    def evaluate_condition(self, condition: ConditionConfig, task_result: TaskResult) -> str:
        """
        Evaluate a condition based on task result
        Returns the next task name or 'end'
        """
        if condition.outcome == "success":
            if task_result.status == TaskStatus.SUCCESS:
                return condition.target_task_success
            else:
                return condition.target_task_failure
        elif condition.outcome == "failure":
            if task_result.status == TaskStatus.FAILURE:
                return condition.target_task_success
            else:
                return condition.target_task_failure

        # Default behavior if condition doesn't match
        return condition.target_task_failure if task_result.status == TaskStatus.FAILURE else condition.target_task_success


class FlowManager:
    """Main Flow Manager that orchestrates task execution"""

    def __init__(self):
        self.task_factory = TaskFactory()
        self.condition_evaluator = ConditionEvaluator()
        self.active_flows: Dict[str, FlowExecutionState] = {}

    def load_flow_config(self, config_dict: Dict[str, Any]) -> FlowConfig:
        """Load flow configuration from dictionary"""
        flow_data = config_dict.get('flow', {})

        # Parse tasks
        tasks = []
        for task_data in flow_data.get('tasks', []):
            task_config = TaskConfig(
                name=task_data['name'],
                description=task_data['description'],
                task_type=task_data.get('task_type', task_data['name'].replace(' ', '_').lower()),
                parameters=task_data.get('parameters', {})
            )
            tasks.append(task_config)

        # Parse conditions
        conditions = []
        for condition_data in flow_data.get('conditions', []):
            condition_config = ConditionConfig(
                name=condition_data['name'],
                description=condition_data['description'],
                source_task=condition_data['source_task'],
                outcome=condition_data['outcome'],
                target_task_success=condition_data['target_task_success'],
                target_task_failure=condition_data['target_task_failure']
            )
            conditions.append(condition_config)

        return FlowConfig(
            id=flow_data['id'],
            name=flow_data['name'],
            start_task=flow_data['start_task'],
            tasks=tasks,
            conditions=conditions
        )

    def create_flow_execution(self, flow_config: FlowConfig) -> str:
        """Create a new flow execution instance"""
        execution_id = str(uuid.uuid4())

        execution_state = FlowExecutionState(
            flow_id=execution_id,
            flow_name=flow_config.name,
            status=FlowStatus.CREATED
        )

        self.active_flows[execution_id] = execution_state
        return execution_id

    async def execute_flow(self, execution_id: str, flow_config: FlowConfig) -> FlowExecutionState:
        """Execute a flow and return the final state"""

        if execution_id not in self.active_flows:
            raise ValueError(f"Flow execution {execution_id} not found")

        execution_state = self.active_flows[execution_id]
        execution_state.status = FlowStatus.RUNNING
        execution_state.started_at = datetime.now()

        try:
            # Start with the first task
            current_task_name = flow_config.start_task
            context = {'previous_results': {}}

            while current_task_name and current_task_name != "end":
                execution_state.current_task = current_task_name

                # Get task configuration
                task_config = flow_config.get_task_by_name(current_task_name)
                if not task_config:
                    execution_state.status = FlowStatus.FAILURE
                    raise ValueError(f"Task '{current_task_name}' not found in flow configuration")

                # Create and execute task
                task = self.task_factory.create_task(task_config)
                task_result = await task.execute(context)

                # Store task result
                execution_state.task_results[current_task_name] = task_result
                execution_state.completed_tasks.append(current_task_name)
                context['previous_results'][current_task_name] = task_result

                # Evaluate condition to determine next step
                condition = flow_config.get_condition_for_task(current_task_name)
                if condition:
                    next_task = self.condition_evaluator.evaluate_condition(condition, task_result)
                    current_task_name = next_task
                else:
                    # No condition defined, end the flow
                    break

                # If task failed and condition says to end, break the loop
                if current_task_name == "end":
                    break

            # Determine final flow status
            execution_state.current_task = None
            execution_state.ended_at = datetime.now()

            # Check if all tasks completed successfully
            all_successful = all(
                result.status == TaskStatus.SUCCESS 
                for result in execution_state.task_results.values()
            )

            if all_successful:
                execution_state.status = FlowStatus.SUCCESS
            else:
                # Check if any task failed
                any_failed = any(
                    result.status == TaskStatus.FAILURE 
                    for result in execution_state.task_results.values()
                )
                execution_state.status = FlowStatus.FAILURE if any_failed else FlowStatus.ENDED

        except Exception as e:
            execution_state.status = FlowStatus.FAILURE
            execution_state.ended_at = datetime.now()
            execution_state.current_task = None
            # In a real implementation, you'd use proper logging
            print(f"Flow execution failed: {str(e)}")

        return execution_state

    def get_flow_status(self, execution_id: str) -> Optional[FlowExecutionState]:
        """Get current status of a flow execution"""
        return self.active_flows.get(execution_id)

    def get_all_flows(self) -> Dict[str, FlowExecutionState]:
        """Get all active flows"""
        return self.active_flows.copy()

    def remove_flow(self, execution_id: str) -> bool:
        """Remove a flow execution from memory"""
        if execution_id in self.active_flows:
            del self.active_flows[execution_id]
            return True
        return False

    def get_flow_summary(self) -> Dict[str, Any]:
        """Get summary statistics of all flows"""
        flows = self.active_flows.values()
        return {
            "total_flows": len(flows),
            "status_counts": {
                status.value: sum(1 for f in flows if f.status == status)
                for status in FlowStatus
            },
            "registered_task_types": list(self.task_factory.get_registered_tasks().keys())
        }
