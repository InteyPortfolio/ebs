import pika
from os import environ
import json
import time
from uuid import uuid4
from tqdm import tqdm
from random import randint


class Routes:
    TASK_REQUESTS = "tasks-requests"
    PROCESSING = "processing"


class MessageTypes:
    start = "START_PROCESSING"
    finish = "END_PROCESSING"


EXCHANGE = "ebs"


class Processor:
    def __init__(self, id_: str, config: dict):
        host, port = environ.get("QUEUE_URL").split(":")
        print(f"initialize. QUEUE_URL:'{host}:{port}'")
        self.conn = pika.BlockingConnection(pika.ConnectionParameters(host, port))
        self.channel = self.conn.channel()
        self.id = id_
        if config['process_time']  == "rnd":
            self.min_time = config["rnd"]["min"]
            self.max_time = config["rnd"]["max"]
        else:
            self.min_time = config["process_time"]
            self.max_time = config["process_time"]

    def consume(self):
        self.channel.exchange_declare(exchange=EXCHANGE, exchange_type="topic")
        result = self.channel.queue_declare("processor_consume")
        queue_name = result.method.queue
        self.channel.queue_bind(
            exchange=EXCHANGE, queue=queue_name, routing_key=Routes.TASK_REQUESTS
        )

        self.channel.basic_consume(
            queue=queue_name, on_message_callback=self.callback, auto_ack=True
        )

        self.channel.start_consuming()

    def callback(self, ch, method, properties, body):
        data = json.loads(body.decode("utf8"))
        print(f"processor {self.id} got message with route {method.routing_key}")
        if method.routing_key == Routes.TASK_REQUESTS:
            print("process", data)
            spend_time = randint(self.min_time, self.max_time) * 10

            self.send_to_queue(MessageTypes.start, data["id"])
            for i in tqdm(range(spend_time)):
                time.sleep(0.1)
            self.send_to_queue(MessageTypes.finish, data["id"], spend_time)

    def send_to_queue(self, msg_type: str, obj_id: str, time=None):
        host, port = environ.get("QUEUE_URL").split(":")
        connection = pika.BlockingConnection(pika.ConnectionParameters(host, port))
        channel = connection.channel()
        channel.exchange_declare(exchange=EXCHANGE, exchange_type="topic")
        result = channel.queue_declare("processor_results")
        channel.queue_bind(
            exchange=EXCHANGE, queue=result.method.queue, routing_key=Routes.PROCESSING
        )

        data = dict(type=msg_type, target=obj_id, processor=self.id)
        if time is None:
            data["spend"] = time

        channel.basic_publish(
            exchange=EXCHANGE, routing_key=Routes.PROCESSING, body=json.dumps(data)
        )
        connection.close()

def read_config():
    with open('./config.json') as f:
        config = json.load(f)
        return config

if __name__ == "__main__":
    id_ = uuid4().hex
    config =read_config()
    p = Processor(id_, config)
    p.consume()
