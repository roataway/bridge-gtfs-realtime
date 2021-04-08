from datetime import datetime

from util import random_word


class FeedEntity:
    """A class to represent the state of a vehicle, ready for serialization to ProtoBuf"""

    id: str
    label: str
    last_seen: int
    feed_id: int
    lat: float
    lon: float
    speed: float
    direction: int
    trip_id: str

    def __init__(self, data: dict, route_id: str):
        self.id = data["rtu_id"]
        self.label = data["board"]
        datetime_object = datetime.strptime(data["timestamp"], "%Y-%m-%dT%H:%M:%SZ")
        self.last_seen = datetime_object.timestamp()  # this must be the time when the server received it?
        self.lat = data["latitude"]
        self.lon = data["longitude"]
        self.speed = data["speed"] / 3.6  # convert to m/s
        self.direction = data["direction"]
        self.trip_id = route_id

    def __str__(self):
        return (
            f"lat:{self.lat}, lon:{self.lon}, route_id:{self.trip_id} "
            f"@{datetime.fromtimestamp(self.last_seen)}Z"
        )
