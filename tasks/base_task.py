from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseTask(ABC):
    def __init__(self, name: str, parameters: Dict[str, Any]):
        self.name = name
        self.parameters = parameters

    @abstractmethod
    async def run(self) -> Dict[str, Any]:
        pass

