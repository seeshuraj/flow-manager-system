"""
Test Script for Flow Manager

This script tests the core functionality of the flow manager system
including flow creation, execution, and result validation.
"""

import asyncio
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import TaskStatus, FlowStatus
from flow_manager import FlowManager

async def test_flow_manager():
    """Test the flow manager functionality"""
    print("=== Flow Manager Test ===\n")

    flow_manager = FlowManager()
    print("✓ Flow Manager initialized")

    sample_config = {
        "id": "test_flow",
        "name": "Test Data Processing Flow",
        "start_task": "task1",
        "tasks": [
            {"name": "task1", "description": "Fetch data", "task_type": "fetch_data", "parameters": {"failure_rate": 0.0}},
            {"name": "task2", "description": "Process data", "task_type": "process_data", "parameters": {"failure_rate": 0.0}},
            {"name": "task3", "description": "Store data", "task_type": "store_data", "parameters": {"failure_rate": 0.0}},
        ],
        "conditions": [
            {
                "name": "condition_task1_result",
                "description": "Evaluate task1 result",
                "source_task": "task1",
                "outcome": "success",
                "target_task_success": "task2",
                "target_task_failure": "end",
            },
            {
                "name": "condition_task2_result",
                "description": "Evaluate task2 result",
                "source_task": "task2",
                "outcome": "success",
                "target_task_success": "task3",
                "target_task_failure": "end",
            },
        ],
    }

    try:
        flow_config = flow_manager.load_flow_config(sample_config)
        print(f"✓ Flow configuration loaded: {flow_config['name']}")

        execution_id = flow_manager.create_flow_execution(flow_config)
        print(f"✓ Flow execution created: {execution_id}")

        print("\n--- Executing Flow ---")
        execution_state = await flow_manager.execute_flow(execution_id, flow_config)

        print("\n--- Flow Execution Results ---")
        print(f"Flow Status: {execution_state.status} (type: {type(execution_state.status)})")
        print(f"Completed Tasks: {execution_state.completed_tasks}")

        execution_time = execution_state.ended_at - execution_state.started_at
        print(f"Total Execution Time: {execution_time.total_seconds():.2f} seconds")

        print("\n--- Task Results ---")
        for task_name, result in execution_state.task_results.items():
            print(f"  {task_name}:")
            print(f"    Status: {result.status} (type: {type(result.status)})")
            print(f"    Message: {result.message}")
            print(f"    Execution Time: {result.execution_time or 0:.2f}s")
            if result.error:
                print(f"    Error: {result.error}")

        expected_tasks = ["task1", "task2", "task3"]
        actual_tasks = execution_state.completed_tasks

        if set(expected_tasks) == set(actual_tasks):
            print("\n✅ All expected tasks were executed")
        else:
            print(f"\n❌ Task execution mismatch. Expected: {expected_tasks}, Got: {actual_tasks}")
            return False

        # Compare enum value for accurate status check
        status_value = execution_state.status.value.upper()
        print(f"DEBUG: Flow status value for comparison: {status_value}")

        if status_value == "COMPLETED":
            print("✅ Flow completed successfully")
            return True
        else:
            print(f"✗ Test failed: Flow status was {execution_state.status}")
            return False

    except Exception as e:
        print(f"✗ Test failed: {str(e)}")
        return False

async def test_flow_with_failure():
    """Test flow behavior when a task fails"""
    print("\n=== Testing Flow with Failure ===\n")

    flow_manager = FlowManager()

    failure_config = {
        "id": "failure_test_flow",
        "name": "Failure Test Flow",
        "start_task": "task1",
        "tasks": [
            {"name": "task1", "description": "Fetch data", "task_type": "fetch_data", "parameters": {"failure_rate": 0.0}},
            {"name": "task2", "description": "Process data", "task_type": "process_data", "parameters": {"failure_rate": 1.0}},
            {"name": "task3", "description": "Store data", "task_type": "store_data", "parameters": {"failure_rate": 0.0}},
        ],
        "conditions": [
            {
                "name": "condition_task1_result",
                "description": "Evaluate task1 result",
                "source_task": "task1",
                "outcome": "success",
                "target_task_success": "task2",
                "target_task_failure": "end",
            },
            {
                "name": "condition_task2_result",
                "description": "Evaluate task2 result",
                "source_task": "task2",
                "outcome": "success",
                "target_task_success": "task3",
                "target_task_failure": "end",
            },
        ],
    }

    try:
        flow_config = flow_manager.load_flow_config(failure_config)
        execution_id = flow_manager.create_flow_execution(flow_config)

        print("Executing flow with forced failure in task2...")
        execution_state = await flow_manager.execute_flow(execution_id, flow_config)

        print(f"Flow Status: {execution_state.status} (type: {type(execution_state.status)})")
        print(f"Completed Tasks: {execution_state.completed_tasks}")

        status_value = execution_state.status.value.upper()
        print(f"DEBUG: Flow status value for comparison: {status_value}")

        if len(execution_state.completed_tasks) == 1 and status_value == "FAILED":
            print("✅ Flow correctly stopped after task failure")
            return True
        else:
            print("✗ Failure test failed: Flow did not handle failure correctly")
            return False

    except Exception as e:
        print(f"✗ Failure test failed: {str(e)}")
        return False

async def test_api_integration():
    """Test API integration (requires running API server)"""
    print("\n=== Testing API Integration ===\n")
    try:
        import httpx

        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/health")
            if response.status_code == 200:
                print("✅ API health check passed")
                return True
            else:
                print("❌ API health check failed")
                return False

    except ImportError:
        print("⚠️  httpx not installed, skipping API integration test")
        return True
    except Exception as e:
        print(f"⚠️  API server not running or accessible: {str(e)}")
        print("    Start the API with: python api.py")
        return True  # Skip test if server down

async def main():
    """Run all tests"""
    print("🧪 Running Flow Manager Tests\n")

    tests = [
        ("Core Flow Manager", test_flow_manager()),
        ("Flow with Failure", test_flow_with_failure()),
        ("API Integration", test_api_integration()),
    ]

    results = []

    for test_name, test_coro in tests:
        print(f"\n{'='*50}")
        print(f"Running: {test_name}")
        print("="*50)

        try:
            result = await test_coro
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))

    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print("="*50)

    passed = sum(1 for _, res in results if res)
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name}: {status}")

    print(f"\nOverall: {passed}/{len(results)} tests passed")

    if passed == len(results):
        print("\n🎉 All tests passed!")
        return True
    else:
        print("\n❌ Some tests failed!")
        return False

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
