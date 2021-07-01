"""
Инструментальные классы-фасады брокера Kafka
"""

import asyncio
import json
import random
from decimal import Decimal
from enum import Enum
from typing import Callable, Union, Sequence

from aiokafka import AIOKafkaConsumer, TopicPartition, AIOKafkaProducer
from chassis import Chassis
from dataclasses import asdict
from chassis.event import Event, EventSchema

# TODO: logging for chassis modules

class EventConsumer:
    """Consumer"""

    _bootstrap_servers: Union[str, Sequence] = None
    _group_id: str = None
    _topic_name: str = None

    _consumer: AIOKafkaConsumer = None
    _handler: Callable = None

    _topic = None

    # Признак того, что прослушивание приостановлено
    _is_suspended = False

    def __init__(self,
                 bootstrap_servers: Union[str, Sequence],
                 topic_name: str,
                 handler: Callable,
                 logger,
                 group_id: str = None,
                 is_suspended: bool = False):

        self._bootstrap_servers = bootstrap_servers
        self._group_id = group_id

        self._topic_name = topic_name
        self._handler = handler

        self._is_suspended = is_suspended

    @staticmethod
    def _kafka_value_deserializer(serialized):
        return json.loads(serialized)

    @property
    def is_suspended(self) -> bool:
        return self._is_suspended


    async def _start_consume(self, loop, reset=False):
        """Начать прослушивание очереди с остановкой текущей рутины"""

        self._consumer = AIOKafkaConsumer(
            self._topic_name,
            loop=loop,
            bootstrap_servers=self._bootstrap_servers,
            enable_auto_commit=False,
            auto_offset_reset="earliest",
            # value_deserializer=self._kafka_value_deserializer,
            group_id=self._group_id,
        )
        # Get cluster layout and join group `self._group_id`
        #logger.debug(f'Consumers for topic {self._topic_name} begun starting!')
        await self._consumer.start()
        # self._is_started = True

        if reset:
            #logger.debug("reset offset to 0")
            partitions = self._consumer.partitions_for_topic("events")
            for p in partitions:
                await self._consumer.commit({TopicPartition("events", p): 0})

        #logger.debug(f'Consumers for topic {self._topic_name} was started!')

        try:
            # Consume messages
            while True:
                msg = await self._consumer.getone()

                try:
                    await self._handler(msg.value)
                except Exception as e:
                    # Логируем необслуживаемое исключение и _отбрасываем_
                    # сообщение, приведшее к этому результату, что бы не останвливать
                    # процесс обработки целиком
                    #logger.error(e)
                    pass
                finally:
                    tp = TopicPartition(msg.topic, msg.partition)
                    await self._consumer.commit({tp: msg.offset + 1})

        except Exception as e:
            #logger.error(e)
            await self._consumer.stop()
            #logger.error(f'Consumers for topics {self.topics} was stopped!')

    async def start_consume(self, loop=None):
        """Начать прослушивание очереди"""

        loop = loop or asyncio.get_running_loop()
        asyncio.create_task(self._start_consume(loop))
        await asyncio.sleep(.1)

    async def stop_consume(self):
        """Stop consumer"""

        #logger.debug(f'Consumers begun shutdown!')
        try:
            await asyncio.wait_for(
                asyncio.create_task(self._consumer.stop()), timeout=1)
        except asyncio.TimeoutError:
            pass
            #logger.debug(f'Attention: consumer {self._consumer} stopped FORCED!')
        else:
            pass
            # logger.debug(f'Consumer {self._consumer} stopped!')

    def suspend_consume(self):
        """Приостановить прослушивание"""
        self._is_suspended = True

    def resume_consume(self):
        """Возобновить прослушивание"""
        self._is_suspended = False


class EventSender:
    """
    Сервис отправки события на шину
    """

    _producer: AIOKafkaProducer = None

    def __init__(self, config, logger):
        try:
            _bootstrap_servers = config['bootstrap_servers']
            self._events_topic = config['events_topic']
        except KeyError as e:
            raise InvalidConfiguration(e)

        self._producer = AIOKafkaProducer(
            bootstrap_servers=_bootstrap_servers,
            value_serializer=lambda value: json.dumps(value).encode()
        )

    async def start(self, **kwargs):
        # Стартуем продюсер
        await self._producer.start()

    async def stop(self):
        # Останавливаем продюсер
        await self._producer.stop()

    async def send(self, event: Event):
        """
        Отправить событие на шину событий
        """

        await self._producer.send(
            self._events_topic, EventSchema().dump(event)
        )
