import asyncio
import random
from tasks.base_task import BaseTask

class PrintTask(BaseTask):
    async def run(self) -> dict:
        failure_rate = self.parameters.get("failure_rate", 0)
        if random.random() < failure_rate:
            raise RuntimeError(f"Simulated failure in task {self.name}")

        message = self.parameters.get("message", "Default print task message")
        await asyncio.sleep(0.1)
        print(f"[{self.name}] {message}")
        return {"message_printed": message}

