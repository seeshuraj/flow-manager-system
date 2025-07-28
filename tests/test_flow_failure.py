import pytest
import asyncio
from flow_manager import FlowManager, FlowStatus, TaskStatus

@pytest.mark.asyncio
async def test_flow_with_failure():
    fm = FlowManager()
    flow_config = {
        "id": "flow_failure",
        "name": "Flow with Failure",
        "start_task": "task1",
        "tasks": [
            {"name": "task1", "task_type": "print", "parameters": {"message": "Task 1", "failure_rate": 0}},
            {"name": "task2", "task_type": "print", "parameters": {"message": "Task 2", "failure_rate": 1}},  # always fails
            {"name": "task3", "task_type": "wait", "parameters": {"seconds": 0}},
        ],
        "conditions": []
    }

    execution_id = fm.create_flow_execution(flow_config)
    state = await fm.execute_flow(execution_id, flow_config)

    assert state.status == FlowStatus.FAILED
    assert "task1" in state.completed_tasks
    assert "task2" in state.task_results
    assert state.task_results["task2"].status == TaskStatus.FAILURE
    assert "task3" not in state.completed_tasks

