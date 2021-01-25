import pika
from os import environ
import sys
import json
from uuid import uuid4


REPEATS = int(environ.get("DISTRIBUTION_COUNT", "3"))


class Routes:
    OBJECTS = "objects"
    TASK_REQUESTS = "tasks-requests"


EXCHANGE = "ebs"


class Distributor:
    """
    Async Distributor based on queue. Accepts message of gotten object,
    and then, repeats it in 3 meta-objects, and distribute them between
    processors
    """

    # exchange_name = '...'

    def __init__(self, config):
        host, port = environ.get("QUEUE_URL").split(":")
        self.config = config
        print(f"initialize. QUEUE_URL:'{host}:{port}'")

        self.conn = pika.BlockingConnection(pika.ConnectionParameters(host, port))
        self.channel = self.conn.channel()

    def consume(self):
        self.channel.exchange_declare(exchange=EXCHANGE, exchange_type="topic")
        res = self.channel.queue_declare("distributor_consume")
        self.channel.queue_bind(
            exchange=EXCHANGE, queue=res.method.queue, routing_key=Routes.OBJECTS
        )
        self.channel.basic_consume(
            queue=res.method.queue, on_message_callback=self.callback, auto_ack=True
        )
        self.channel.start_consuming()


    def send_to_queue(self, obj: dict):
        print("send to queue obj", obj)
        host, port = environ.get("QUEUE_URL").split(":")
        connection = pika.BlockingConnection(pika.ConnectionParameters(host, port))
        channel = connection.channel()

        channel.exchange_declare(exchange=EXCHANGE, exchange_type="topic")
        channel.basic_publish(
            exchange=EXCHANGE, routing_key=Routes.TASK_REQUESTS, body=json.dumps(obj)
        )
        connection.close()


    def callback(self, ch, method, properties, body):
        data = json.loads(body.decode("utf8"))
        print("Distributor got message with route", method.routing_key)
        REPEATS = self.config['distribution']
        if method.routing_key == Routes.OBJECTS:
            for i in range(REPEATS):
                virtual = dict(id=uuid4().hex, object=data)
                # push in channel
                self.send_to_queue(virtual)


def read_config():
    with open('./config.json') as f:
        config = json.load(f)
        return config

if __name__ == "__main__":
    conf = read_config()
    consumer = Distributor(conf)
    consumer.consume()
