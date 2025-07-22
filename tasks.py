"""
Task Implementations

This module contains concrete implementations of tasks for the flow manager system.
Each task inherits from BaseTask and implements the execute method.
"""

import asyncio
import json
import random
import time
from typing import Dict, Any
from datetime import datetime

from models import BaseTask, TaskResult, TaskStatus


class FetchDataTask(BaseTask):
    """Task to fetch data from a source"""

    async def execute(self, context: Dict[str, Any] = None) -> TaskResult:
        """Simulate fetching data from an external source"""
        start_time = time.time()

        try:
            # Simulate network delay
            await asyncio.sleep(1)

            # Simulate potential failure based on parameters
            failure_rate = self.parameters.get('failure_rate', 0.1)
            if random.random() < failure_rate:
                return TaskResult(
                    task_name=self.name,
                    status=TaskStatus.FAILURE,
                    message="Failed to fetch data from external source",
                    error="Connection timeout",
                    execution_time=time.time() - start_time
                )

            # Simulate successful data fetching
            mock_data = {
                "records": [
                    {"id": 1, "name": "Item 1", "value": 100},
                    {"id": 2, "name": "Item 2", "value": 200},
                    {"id": 3, "name": "Item 3", "value": 300}
                ],
                "total_count": 3,
                "source": self.parameters.get('data_source', 'default_api')
            }

            return TaskResult(
                task_name=self.name,
                status=TaskStatus.SUCCESS,
                message="Successfully fetched data",
                data=mock_data,
                execution_time=time.time() - start_time
            )

        except Exception as e:
            return TaskResult(
                task_name=self.name,
                status=TaskStatus.FAILURE,
                message="Error during data fetching",
                error=str(e),
                execution_time=time.time() - start_time
            )


class ProcessDataTask(BaseTask):
    """Task to process fetched data"""

    async def execute(self, context: Dict[str, Any] = None) -> TaskResult:
        """Process data from previous task"""
        start_time = time.time()

        try:
            # Get data from context (from previous task)
            previous_results = context.get('previous_results', {}) if context else {}
            input_data = {}

            # Look for data from fetch task
            for task_name, result in previous_results.items():
                if 'fetch' in task_name.lower() or 'task1' in task_name.lower():
                    if result.status == TaskStatus.SUCCESS:
                        input_data = result.data
                        break

            if not input_data:
                return TaskResult(
                    task_name=self.name,
                    status=TaskStatus.FAILURE,
                    message="No data available to process",
                    error="Missing input data from previous task",
                    execution_time=time.time() - start_time
                )

            # Simulate processing delay
            await asyncio.sleep(1.5)

            # Simulate potential processing failure
            failure_rate = self.parameters.get('failure_rate', 0.05)
            if random.random() < failure_rate:
                return TaskResult(
                    task_name=self.name,
                    status=TaskStatus.FAILURE,
                    message="Data processing failed",
                    error="Processing algorithm error",
                    execution_time=time.time() - start_time
                )

            # Process the data (transform, aggregate, etc.)
            records = input_data.get('records', [])
            processed_data = {
                "processed_records": [
                    {
                        **record,
                        "processed": True,
                        "doubled_value": record.get('value', 0) * 2,
                        "category": "high" if record.get('value', 0) > 150 else "low"
                    }
                    for record in records
                ],
                "summary": {
                    "total_records": len(records),
                    "total_value": sum(record.get('value', 0) for record in records),
                    "processing_method": self.parameters.get('method', 'standard')
                }
            }

            return TaskResult(
                task_name=self.name,
                status=TaskStatus.SUCCESS,
                message="Data processed successfully",
                data=processed_data,
                execution_time=time.time() - start_time
            )

        except Exception as e:
            return TaskResult(
                task_name=self.name,
                status=TaskStatus.FAILURE,
                message="Error during data processing",
                error=str(e),
                execution_time=time.time() - start_time
            )


class StoreDataTask(BaseTask):
    """Task to store processed data"""

    async def execute(self, context: Dict[str, Any] = None) -> TaskResult:
        """Store processed data to a destination"""
        start_time = time.time()

        try:
            # Get processed data from context
            previous_results = context.get('previous_results', {}) if context else {}
            processed_data = {}

            # Look for data from process task
            for task_name, result in previous_results.items():
                if 'process' in task_name.lower() or 'task2' in task_name.lower():
                    if result.status == TaskStatus.SUCCESS:
                        processed_data = result.data
                        break

            if not processed_data:
                return TaskResult(
                    task_name=self.name,
                    status=TaskStatus.FAILURE,
                    message="No processed data available to store",
                    error="Missing processed data from previous task",
                    execution_time=time.time() - start_time
                )

            # Simulate storage delay
            await asyncio.sleep(0.8)

            # Simulate potential storage failure
            failure_rate = self.parameters.get('failure_rate', 0.02)
            if random.random() < failure_rate:
                return TaskResult(
                    task_name=self.name,
                    status=TaskStatus.FAILURE,
                    message="Failed to store data",
                    error="Database connection error",
                    execution_time=time.time() - start_time
                )

            # Simulate successful storage
            storage_info = {
                "stored_records": len(processed_data.get('processed_records', [])),
                "storage_location": self.parameters.get('storage_path', '/data/processed/'),
                "storage_format": self.parameters.get('format', 'json'),
                "timestamp": datetime.now().isoformat()
            }

            return TaskResult(
                task_name=self.name,
                status=TaskStatus.SUCCESS,
                message="Data stored successfully",
                data=storage_info,
                execution_time=time.time() - start_time
            )

        except Exception as e:
            return TaskResult(
                task_name=self.name,
                status=TaskStatus.FAILURE,
                message="Error during data storage",
                error=str(e),
                execution_time=time.time() - start_time
            )
