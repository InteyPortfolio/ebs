from kafka.producer import KafkaProducer
import logging,sys

class KafkaLogHandler(logging.Handler):
    """
    """
    def __init__(self, bootstrap_servers, topic, key=None):
        logging.Handler.__init__(self)
        self.key = key
        self.producer = KafkaProducer(bootstrap_servers=bootstrap_servers, value_serializer=lambda m: json.dumps(m).encode('ascii'))
        self.topic = topic

    def emit(self, record):
        #drop kafka logging to avoid infinite recursion
        if record.name == 'kafka':
            return
        try:
            #use default formatting
            msg = record
            #produce message
            if self.key is None:
                print(msg)
                # self.producer.send(self.topic, value=msg)
            else:
                # self.producer.send(self.topic, key=self.key, value=msg)
        except:
            import traceback
            ei = sys.exc_info()
            traceback.print_exception(ei[0], ei[1], ei[2], None, sys.stderr)
            del ei

    def close(self):
        # self.producer.stop()
        logging.Handler.close(self)

