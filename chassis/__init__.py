from .logger import KafkaLogHandler
from loguru import logger
from .mq import EventSender, EventConsumer

class Chassis:
    def __init__(self, config: dict):
        self.config
        self.kafka = self.config['kafka']
        self.logging = self.config['logging']
        self.event_sender = self.config['event_sender']
        self.__logger = None

    def get_logger():
        handler = KafkaLogHandler(**self.kafka, **self.logging)
        if self.__logger is None:
            logger.add(handler)
            self.__logger = logger
        return self.__logger

    def mk_event_sender(self):
        return EventSender(**self.kafka, **self.event_sender, logger=self.get_logger())

    def mk_event_consumer(self):
        pass
