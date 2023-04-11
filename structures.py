from datetime import datetime, timedelta

import constants as c


class VehicleState:
    """A class to represent the state of a vehicle, ready for serialization to ProtoBuf"""

    rtu_id: str  # unique ID of each tracker
    board_name: str
    last_seen: int
    lat: float
    lon: float
    speed: float
    #direction: int
    route_id: str

    def __init__(self, data: dict, route_id: str):
        self.rtu_id = data["route_id"]
        self.board_name = data["label"]
        self.last_seen = ((datetime.strptime(data["timestamp"], c.FORMAT_TIME))+timedelta(hours=3)).timestamp() #TODO: get rid of substracting days, must use timezones
        self.lat = data["latitude"]
        self.lon = data["longitude"]
        self.speed = data["speed"] / 3.6 if data["speed"] is not None else 0  # convert to m/s
        #self.direction = data["direction"]
        self.route_id = route_id

    def __str__(self):
        return (
            f"lat:{self.lat:.4f}  lon:{self.lon:.4f}  route_upstream_id:{self.route_id: <3} "
            f"route_gtfs_id:{c.ROUTE_ID_MAP.get(self.route_id, 'unknown'): <3}  "
            f"@{datetime.fromtimestamp(self.last_seen)}Z"
        )
