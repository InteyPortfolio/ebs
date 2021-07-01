# import pika
from os import environ
import json
import time
from uuid import uuid4
from tqdm import tqdm
from random import randint
from bus.kafka_consumer import Consumer, Producer
from bus.topics import EVENTS
from dataclasses import dataclass, asdict
import asyncio
from loguru import logger


class MessageTypes:
    start = "START_PROCESSING"
    finish = "END_PROCESSING"


@dataclass
class ProcessingStarted:
    task_id: str
    type: str = "ProcessingStarted"


@dataclass
class ProcessingFinished:
    task_id: str
    spend_time: str
    type: str = "ProcessingFinished"


class Processor:
    def __init__(self, id_: str):
        host, port = environ.get("QUEUE_URL").split(":")
        self.consumer = Consumer(brokers=[f"{host}:{port}"],
                                 topic_name=EVENTS,
                                 handler=self.callback,
                                 # join consumers for concurrent processing
                                 group_id="processors")

        self.producer = Producer(brokers=[f"{host}:{port}"],
                                 topic_name=EVENTS)

    async def consume(self):
        loop = asyncio.get_running_loop()
        await self.consumer._start_consume(loop)

    async def callback(self, body):
        logger.debug("start processing")
        """ reads message and start processing """
        data = json.loads(body)
        print("process", data)
        spend_time = randint(3, 10) * 10 # from 3 to 10 seconds

        await self.producer.send(ProcessingStarted(task_id=data["id"]))
        for i in tqdm(range(spend_time)):
            time.sleep(0.1)
        await self.producer.send(ProcessingFinished(task_id=data["id"], spend_time=spend_time))
        logger.debug("processing done")

async def main():
    id_ = uuid4().hex
    p = Processor(id_)
    await p.consume()

if __name__ == "__main__":

    asyncio.run(main())
