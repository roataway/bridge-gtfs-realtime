from datetime import datetime

from util import random_word
import constants as c


class VehicleState:
    """A class to represent the state of a vehicle, ready for serialization to ProtoBuf"""

    rtu_id: str  # unique ID of each tracker
    board_name: str
    last_seen: int
    lat: float
    lon: float
    speed: float
    direction: int
    route_id: str

    def __init__(self, data: dict, route_id: str):
        self.rtu_id = data["rtu_id"]
        self.board_name = data["board"]
        self.last_seen = datetime.strptime(data["timestamp"], c.FORMAT_TIME).timestamp()
        self.lat = data["latitude"]
        self.lon = data["longitude"]
        self.speed = data["speed"] / 3.6  # convert to m/s
        self.direction = data["direction"]
        self.route_id = route_id

    def __str__(self):
        return (
            f"lat:{self.lat}, lon:{self.lon}, route_id:{self.route_id} "
            f"@{datetime.fromtimestamp(self.last_seen)}Z"
        )
