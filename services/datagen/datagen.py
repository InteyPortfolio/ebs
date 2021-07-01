from fastapi import FastAPI, Depends
from pydantic import BaseModel
import pika
import yaml
from os import environ
import mimesis
import aiokafka
from chassis import Chassis
from dataclasses import dataclass

gen = mimesis.Generic()


# dependency
async def chassis():
    with open('/etc/config.yaml') as f:
        config = yaml.safe_load(f.read())
    chassis = Chassis(**config)
    # chassis.get_logger().debug("chassis deployed")
    return chassis


@dataclass
class NewObjectMessage:
    object: dict
    type: str = "NewObjectMessage"

class Object(BaseModel):
    id: int
    content: str


app = FastAPI()


@app.get('/health')
def health_check():
    return "Ready"


@app.get("/objects/{object_id}")
def get_object(object_id: int) -> Object:
    return Object(id=object_id, content="lorem?")


@app.get("/objects")
async def list():
    return []


@app.post("/objects")
async def create(chassis: Chassis = Depends(chassis)):
    """
    Generate new object. expects that called from Cron Job
    """
    # TODO: get post data
    obj = generate()

    logger = chassis.get_logger()
    logger.debug("send message")
    producer = chassis.mk_event_sender()
    await producer.start()
    await producer.send(NewObjectMessage(object=obj.dict()))
    return "ok"


def generate() -> Object:
    return Object(
        id=gen.numbers.integer_number(start=0),
        content="2+2",
    )
