from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

from fastapi import FastAPI, Depends
from pydantic import BaseModel
import pika
from os import environ
import mimesis
import json

# models
@dataclass
class Event:
    payload: dict
    id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: str = field(default_factory=lambda: str(datetime.now()))

class Object(BaseModel):
    id: int
    name: str
    content: str


# DI
class EventSender:
    def __init__(self, stream: str):
        pass

    def send(self, event: Event):
        pass



def event_sender():
    rabbit = environ.get("RABBIT_HOST")
    return EventSender(rabbit, "objects")


def generator() -> Object:
    gen = mimesis.Generic()
    return Object(
        id=gen.numbers.integer_number(start=0),
        name=gen.text.word(),
        content=gen.text.word(),
    )

app = FastAPI()

EXCHANGE = "ebs"


@app.get("/health")
def health_check():
    return "Ready"


@app.get("/objects/{object_id}")
def get_object(object_id: int) -> Object:
    return Object(id=object_id, name="dump", content="lorem?")


@app.post("/objects")
def create(sender = Depends(event_sender), generator=Depends(generator)):
    """
    Generate new object. expects that called from Cron Job
    """
    obj = generator()
    sender.send(Event(payload=obj.dict()))


# def send_to_queue(connection, obj: Object):
#     global connection
#     host, port = environ.get("QUEUE_URL").split(":")
#
#     connection = pika.BlockingConnection(pika.ConnectionParameters(host, port))
#     print("send message", obj)
#     channel = connection.channel()
#     channel.exchange_declare(exchange=EXCHANGE, exchange_type="topic")
#     channel.basic_publish(
#         exchange=EXCHANGE, routing_key="objects", body=json.dumps(obj.dict())
#     )
#     connection.close()
