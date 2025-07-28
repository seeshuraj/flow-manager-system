import asyncio
import random
from tasks.base_task import BaseTask

class FetchDataTask(BaseTask):
    async def run(self) -> dict:
        failure_rate = self.parameters.get("failure_rate", 0)
        if random.random() < failure_rate:
            raise RuntimeError(f"Simulated failure in task {self.name}")

        # Simulate a delayed data fetching task
        await asyncio.sleep(0.5)
        data = {
            "data": f"Sample fetched data for task {self.name}"
        }
        print(f"[{self.name}] Fetched data: {data}")
        return data

