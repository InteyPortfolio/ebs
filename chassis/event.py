import json


class Event:
    pass


class EventSchema:
    def dump(self, event):
        return json.dumps(event)
