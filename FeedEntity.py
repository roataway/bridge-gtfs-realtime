import json
import random
import string
from dataclasses import dataclass
from datetime import datetime, timedelta


class FeedEntity:
    id : str
    vehicle_id: str
    vehicle_label: str
    vehicle_timestamp: int
    feed_id: int
    vehicle_position_lat: float
    vehicle_position_lot: float
    vehicle_trip_id: str
    vehicle_speed: float

    def __init__(self, json_str, topic: str, timestamp: float):
        jsn = json.loads(json_str)
        self.id = self.randomword(6)
        self.vehicle_id = jsn['board']
        self.vehicle_label = 'troleibuz'
        datetime_object = datetime.strptime(jsn['timestamp'], '%Y-%m-%dT%H:%M:%SZ')
        self.vehicle_timestamp = int(datetime_object.timestamp())
        self.vehicle_position_lat = float(jsn['latitude'])
        self.vehicle_position_lot = float(jsn['longitude'])
        self.vehicle_speed = float(jsn['speed']) / 3.6
        self.vehicle_trip_id = topic

    def __str__(self):
        pass

    def randomword(self, length: int) -> str:
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(length))

