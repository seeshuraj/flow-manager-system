"""
FastAPI Microservice for Flow Manager

This module provides a RESTful API interface for the Flow Manager system,
enabling users to create, execute, and monitor flows through HTTP endpoints.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime

from models import FlowExecutionState, TaskResult, TaskStatus, FlowStatus
from flow_manager import FlowManager


# Pydantic model matching expected flow config JSON structure
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


class TaskResultResponse(BaseModel):
    task_name: str
    status: str
    message: str
    data: Dict[str, Any] = {}
    execution_time: Optional[float] = None
    timestamp: Optional[datetime] = None
    error: Optional[str] = None


class FlowSummaryResponse(BaseModel):
    total_flows: int
    status_counts: Dict[str, int]
    registered_task_types: List[str]


# FastAPI app instance
app = FastAPI(
    title="Flow Manager API",
    description="A microservice for managing sequential task execution with conditions",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


flow_manager = FlowManager()


def serialize_execution_state(state: FlowExecutionState) -> FlowExecutionResponse:
    task_results = {}
    for task_name, result in state.task_results.items():
        task_results[task_name] = {
            "task_name": result.task_name,
            "status": result.status.value,
            "message": result.message,
            "data": result.data,
            "execution_time": result.execution_time,
            "timestamp": result.timestamp,
            "error": result.error
        }

    return FlowExecutionResponse(
        execution_id=state.flow_id,
        flow_name=state.flow_name,
        status=state.status.value,
        current_task=state.current_task,
        completed_tasks=state.completed_tasks,
        started_at=state.started_at,
        ended_at=state.ended_at,
        task_results=task_results
    )


@app.get("/")
async def root():
    return {
        "service": "Flow Manager API",
        "version": "1.0.0",
        "description": "Manage sequential task execution with conditions",
        "endpoints": {
            "POST /flow/create": "Create a new flow from configuration",
            "POST /flow/execute": "Execute a flow asynchronously",
            "POST /flow/execute-sync": "Execute a flow synchronously",
            "GET /flow/{execution_id}/status": "Get flow execution status",
            "GET /flows": "List all flows",
            "GET /flows/summary": "Get flow summary statistics",
            "GET /health": "Health check endpoint"
        }
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}


@app.post("/flow/create", response_model=Dict[str, str])
async def create_flow(flow_config: FlowConfig):
    """
    Create a new flow from JSON configuration.
    The flow configuration is expected as the request body directly.
    """
    try:
        flow_config_obj = flow_manager.load_flow_config(flow_config.dict())
        execution_id = flow_manager.create_flow_execution(flow_config_obj)

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
    try:
        execution_id = request.execution_id

        execution_state = flow_manager.get_flow_status(execution_id)
        if not execution_state:
            raise HTTPException(status_code=404, detail=f"Flow execution {execution_id} not found")

        # You need to have your flow config stored/retrieved for execution
        # For demo only: raise error if config is missing
        flow_config = flow_manager.get_flow_config(execution_id)
        if flow_config is None:
            raise HTTPException(status_code=400, detail="Flow configuration not found for execution")

        async def execute_async():
            await flow_manager.execute_flow(execution_id, flow_config)

        background_tasks.add_task(execute_async)

        return serialize_execution_state(execution_state)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute flow: {str(e)}")


@app.post("/flow/execute-sync", response_model=FlowExecutionResponse)
async def execute_flow_sync(flow_config: FlowConfig):
    try:
        flow_config_obj = flow_manager.load_flow_config(flow_config.dict())
        execution_id = flow_manager.create_flow_execution(flow_config_obj)
        execution_state = await flow_manager.execute_flow(execution_id, flow_config_obj)

        return serialize_execution_state(execution_state)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute flow: {str(e)}")


@app.get("/flow/{execution_id}/status", response_model=FlowExecutionResponse)
async def get_flow_status(execution_id: str):
    execution_state = flow_manager.get_flow_status(execution_id)
    if not execution_state:
        raise HTTPException(status_code=404, detail=f"Flow execution {execution_id} not found")
    return serialize_execution_state(execution_state)


@app.get("/flows", response_model=Dict[str, FlowExecutionResponse])
async def list_all_flows():
    all_flows = flow_manager.get_all_flows()
    return {eid: serialize_execution_state(state) for eid, state in all_flows.items()}


@app.get("/flows/summary", response_model=FlowSummaryResponse)
async def get_flows_summary():
    summary = flow_manager.get_flow_summary()
    return FlowSummaryResponse(
        total_flows=summary["total_flows"],
        status_counts=summary["status_counts"],
        registered_task_types=summary["registered_task_types"]
    )


@app.get("/flow/{execution_id}/tasks/{task_name}/result", response_model=TaskResultResponse)
async def get_task_result(execution_id: str, task_name: str):
    execution_state = flow_manager.get_flow_status(execution_id)
    if not execution_state:
        raise HTTPException(status_code=404, detail=f"Flow execution {execution_id} not found")
    if task_name not in execution_state.task_results:
        raise HTTPException(status_code=404, detail=f"Task {task_name} not found in flow execution")
    task_result = execution_state.task_results[task_name]
    return TaskResultResponse(
        task_name=task_result.task_name,
        status=task_result.status.value,
        message=task_result.message,
        data=task_result.data,
        execution_time=task_result.execution_time,
        timestamp=task_result.timestamp,
        error=task_result.error
    )


@app.delete("/flow/{execution_id}")
async def delete_flow(execution_id: str):
    success = flow_manager.remove_flow(execution_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Flow execution {execution_id} not found")
    return {"message": f"Flow execution {execution_id} deleted successfully"}


# Error Handlers
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return JSONResponse(status_code=400, content={"message": f"Invalid input: {str(exc)}"})


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(status_code=500, content={"message": f"Internal server error: {str(exc)}"})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
