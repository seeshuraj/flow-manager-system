import pytest
import asyncio
from flow_manager import FlowManager, FlowStatus, TaskStatus

@pytest.mark.asyncio
async def test_success_flow():
    fm = FlowManager()
    flow_config = {
        "id": "flow_success",
        "name": "Successful Flow",
        "start_task": "task1",
        "tasks": [
            {"name": "task1", "task_type": "print", "parameters": {"message": "Task 1", "failure_rate": 0}},
            {"name": "task2", "task_type": "wait", "parameters": {"seconds": 0, "failure_rate": 0}},
            {"name": "task3", "task_type": "print", "parameters": {"message": "Task 3", "failure_rate": 0}},
        ],
        "conditions": []
    }

    execution_id = fm.create_flow_execution(flow_config)
    state = await fm.execute_flow(execution_id, flow_config)

    assert state.status == FlowStatus.COMPLETED
    assert set(state.completed_tasks) == {"task1", "task2", "task3"}
    for result in state.task_results.values():
        assert result.status == TaskStatus.SUCCESS
        assert result.error is None

