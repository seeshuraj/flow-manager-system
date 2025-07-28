import asyncio
import random
from tasks.base_task import BaseTask

class WaitTask(BaseTask):
    async def run(self) -> dict:
        failure_rate = self.parameters.get("failure_rate", 0)
        if random.random() < failure_rate:
            raise RuntimeError(f"Simulated failure in task {self.name}")

        seconds = self.parameters.get("seconds", 1)
        print(f"[{self.name}] Waiting for {seconds} seconds")
        await asyncio.sleep(seconds)
        return {"waited_seconds": seconds}

