import pika

from chassis.event import Event
from chassis.mq.abstract_bus_connector import BusConnector


class RabbitBusConnector(BusConnector):
    async def send(self, event: Event):
        host, port = self.host.split(":")
        connection = pika.BlockingConnection(pika.ConnectionParameters(host, port))
        channel = connection.channel()

        channel.exchange_declare(exchange=EXCHANGE, exchange_type="topic")
        channel.basic_publish(
            exchange=EXCHANGE, routing_key=Routes.TASK_REQUESTS, body=json.dumps(obj)
        )
        connection.close()

    async def consume(self):
        pass
