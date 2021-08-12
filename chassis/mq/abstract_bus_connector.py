from abc import ABC, abstractmethod

from chassis.event import Event


class BusConnector(ABC):
    def __init__(self, host: str, stream: str):
        self.host = host
        self.stream = stream

    @abstractmethod
    async def send(self, event: Event):
        pass

    @abstractmethod
    async def consume(self):
        pass