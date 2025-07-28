import asyncio
import random
from tasks.base_task import BaseTask

class ProcessDataTask(BaseTask):
    async def run(self) -> dict:
        failure_rate = self.parameters.get("failure_rate", 0)
        if random.random() < failure_rate:
            raise RuntimeError(f"Simulated failure in task {self.name}")

        # Simulate some data processing work
        await asyncio.sleep(0.5)  # simulate processing delay

        # Example processed data output
        processed_data = {
            "processed": True,
            "details": f"Processed data for task {self.name}"
        }
        print(f"[{self.name}] Processed data: {processed_data}")
        return processed_data

