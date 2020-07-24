from fastapi import fastapi
from pydantic import BaseModel
import pika
from os import environ
import mimesis

gen = mimesis.Generic()


class Object(BaseModel):
    id: int
    name: str
    content: str


app = FastAPI()


@app.get("/init")
def start(queue_url: str):
    obj = generate()
    send_to_queue(queue_url, obj)


@app.get("/objects/{object_id}")
def get_object(object_id: int) -> Object:
    return Object(object_id, "dump", "lorem?")


def generate() -> Object:
    return Object(
        id=gen.numbers.integer_number(start=0),
        name=gen.text.title(),
        content=gen.text.text(),
    )


def send_to_queue(queue_url: str, obj: Object):
    connection = pika.BlockingConnection(pika.ConnectionParameters(queue_url))
    channel = connection.channel()
