import asyncio
import random
from tasks.base_task import BaseTask

class StoreDataTask(BaseTask):
    async def run(self) -> dict:
        # Optional failure simulation parameter
        failure_rate = self.parameters.get("failure_rate", 0)
        if random.random() < failure_rate:
            raise RuntimeError(f"Simulated failure in task {self.name}")

        # Simulate data storing delay and action
        await asyncio.sleep(0.5)

        # Example return indicating data stored successfully
        stored_info = {
            "stored": True,
            "details": f"Data stored for task {self.name}"
        }
        print(f"[{self.name}] Stored data: {stored_info}")
        return stored_info

