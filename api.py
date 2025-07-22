from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio

from flow_manager import FlowManager, FlowExecutionState, TaskStatus


# Pydantic models for request and response

class TaskConfig(BaseModel):
    name: str
    description: Optional[str] = None
    task_type: str
    parameters: Dict[str, Any] = {}


class ConditionConfig(BaseModel):
    name: str
    description: Optional[str] = None
    source_task: str
    outcome: str
    target_task_success: str
    target_task_failure: str


class FlowConfig(BaseModel):
    id: str
    name: str
    start_task: str
    tasks: List[TaskConfig]
    conditions: List[ConditionConfig]


class FlowExecutionRequest(BaseModel):
    execution_id: str = Field(..., description="Flow execution ID")


class FlowExecutionResponse(BaseModel):
    execution_id: str
    flow_name: str
    status: str
    current_task: Optional[str] = None
    completed_tasks: List[str] = []
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    task_results: Dict[str, Dict[str, Any]] = {}


app = FastAPI(title="Flow Manager API")


flow_manager = FlowManager()


def serialize_execution_state(state: FlowExecutionState) -> FlowExecutionResponse:
    task_results = {}
    for task_name, result in state.task_results.items():
        task_results[task_name] = {
            "task_name": result.task_name,
            "status": result.status.value if result.status else None,
            "message": result.message,
            "data": result.data,
            "execution_time": result.execution_time,
            "timestamp": result.timestamp,
            "error": result.error
        }
    return FlowExecutionResponse(
        execution_id=state.flow_id,
        flow_name=state.flow_name,
        status=state.status.value if state.status else None,
        current_task=state.current_task,
        completed_tasks=state.completed_tasks,
        started_at=state.started_at,
        ended_at=state.ended_at,
        task_results=task_results,
    )


@app.post("/flow/create", response_model=Dict[str, str])
async def create_flow(flow_config: FlowConfig):
    try:
        flow_obj = flow_manager.load_flow_config(flow_config.dict())
        execution_id = flow_manager.create_flow_execution(flow_obj)
        return {
            "execution_id": execution_id,
            "flow_name": flow_config.name,
            "status": "created",
            "message": "Flow created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create flow: {str(e)}")


@app.post("/flow/execute", response_model=FlowExecutionResponse)
async def execute_flow_async(background_tasks: BackgroundTasks, request: FlowExecutionRequest):
    execution_id = request.execution_id
    execution_state = flow_manager.get_flow_status(execution_id)
    if not execution_state:
        raise HTTPException(status_code=404, detail=f"Flow execution {execution_id} not found")

    flow_config = flow_manager.get_flow_config(execution_id)
    if flow_config is None:
        raise HTTPException(status_code=400, detail="Flow configuration not found for execution")

    async def run_execution():
        await flow_manager.execute_flow(execution_id, flow_config)

    background_tasks.add_task(run_execution)
    return serialize_execution_state(execution_state)


@app.get("/flow/{execution_id}/status", response_model=FlowExecutionResponse)
async def get_flow_status(execution_id: str):
    execution_state = flow_manager.get_flow_status(execution_id)
    if not execution_state:
        raise HTTPException(status_code=404, detail=f"Flow execution {execution_id} not found")
    return serialize_execution_state(execution_state)


@app.delete("/flow/{execution_id}")
async def delete_flow(execution_id: str):
    success = flow_manager.remove_flow(execution_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Flow execution {execution_id} not found")
    return {"message": f"Flow execution {execution_id} deleted successfully"}
