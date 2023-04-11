from datetime import datetime
import logging
from io import BytesIO
import json
import requests
import os

from flask import Flask, send_file, make_response
from flask_mqtt import Mqtt
from flask_socketio import SocketIO
from expiringdict import ExpiringDict

from structures import VehicleState
from gtfs_realtime import create_gtfs_feed
import constants as c

LOG = logging.getLogger("app")


# global dict that maintains state, the key is a string that represents the board id,
# and the value is a FeedEntity that represents the last known state of this vehicle
STATE = ExpiringDict(max_len=c.MAX_VEHICLES, max_age_seconds=c.STATE_TTL)

#global dictionary which stores the start time for each board
VEHICLE_START_TIME = ExpiringDict(max_len=c.MAX_VEHICLES, max_age_seconds=c.STATE_TTL)


app = Flask(__name__)
app.config["MQTT_BROKER_URL"] = c.MQTT_BROKER
app.config["MQTT_BROKER_PORT"] = c.MQTT_PORT
app.config["MQTT_REFRESH_TIME"] = 1.0
app.logger.propagate = False


socketio = SocketIO(app)

tranzy_routes = {}

with open("tranzy_key.txt", "r") as file:
    key = file.read()
    
with open("tranzy_routes.json", "r") as file:
    tranzy_routes = json.load(file)


def get_tranzy_data() -> dict:
    response = requests.get('https://api.tranzy.dev/v1/opendata/vehicles', 
                            headers={
                                "Content-Type":"application/json",
                                "X-API-KEY": os.environ.get("TRANZY_KEY", key),
                                "X-Agency-Id" : "4"
                            }
                        )
    return response.json()


def handle_message():
    tranzy_date = get_tranzy_data()
    for data in tranzy_date: 
        # if we got this far, it means we're dealing with something like this:
        # {"latitude": 47.037993, "longitude": 28.817931, "speed": 0, "direction": 151, "timestamp": "2021-04-07T21:39:12Z",
        #  "board": "1273", "rtu_id": "0000289", "route": "22"}
        board_id = data["label"]
        
        if data["route_id"] is None:
            continue
        if data["vehicle_type"] != 11:
            continue
        
        route_id = tranzy_routes[data["route_id"]]["route_short_name"]
        if route_id is None:
            continue
        try:
            state = STATE[board_id]
        except KeyError:
            # we've never seen this board before, let's create a data structure for it
            state = VehicleState(data, route_id)
            STATE[board_id] = state
            LOG.info("New board %s\t %s", board_id, state)
        else:
            # we've seen it before, we just update some of the attributes
            state.last_seen = datetime.strptime(data["timestamp"], c.FORMAT_TIME).timestamp()
            state.lat = data["latitude"]
            state.lon = data["longitude"]
            state.speed = data["speed"] / 3.6 if data["speed"] is not None else 0  # convert to m/s
            #state.direction = data["direction"]
            state.route_id = route_id  # we overwrite it each time, in case it moved to a different route

        try:
            VEHICLE_START_TIME[board_id]
        except KeyError:
            VEHICLE_START_TIME[board_id] = datetime.now().strftime(c.FORMAT_TIME)
            LOG.debug('updating board id = ' + board_id +' start time ')


@app.route("/", methods=["GET"])
def index():
    """Serve a simple status page that returns a string with the current state of all the vehicles"""
    pieces = [f"{board}: {status}" for board, status in STATE.items()]

    result = f"Total vehicles: {len(STATE)}\n\n"
    response = make_response(result + "\n".join(pieces), 200)
    response.mimetype = "text/plain"
    return response

@app.route("/start_times", methods=["GET"])
def start_times():
    """Serve a simple status page that returns a string with the current state of all the vehicles"""
    pieces = [f"{board}: {status}" for board, status in VEHICLE_START_TIME.items()]

    result = f"Total vehicles: {len(VEHICLE_START_TIME)}\n\n"
    response = make_response(result + "\n".join(pieces), 200)
    response.mimetype = "text/plain"
    return response


@app.route("/static", methods=["GET", "POST"])
def gtfs_static():
    LOG.debug("Send GTFS static")
    return send_file("data/rtec-chisinau-md-gtfs-static.zip", as_attachment=True)


@app.route("/rt", methods=["GET", "POST"])
def gtfs_realtime():
    handle_message()
    LOG.debug("Send live feed, %i raw entries", len(STATE))
    feed = create_gtfs_feed(STATE)
    with open("feed_human.txt", "w") as text_file:
        text_file.write(str(feed))
    mem = BytesIO()
    mem.write(feed.SerializeToString())
    mem.seek(0)
    name = datetime.now().strftime("gtfs-rtec-%Y-%m-%d--%H-%M-%S.pb")
    return send_file(mem, as_attachment=True, download_name=name, mimetype="application/protobuf")

@app.route("/rt-human", methods=["GET"])
def gtfs_realtime_human():
    LOG.debug("Send live feed human readable, %i raw entries", len(STATE))
    feed = create_gtfs_feed(STATE)
    response = make_response(str(feed), 200)
    response.mimetype = "text/plain"
    return response


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)5s %(funcName)s - %(message)s")

    host = "0.0.0.0"
    port = 5000
    LOG.info("Starting on %s:%i", host, port)
    socketio.run(app, host=host, port=port, use_reloader=True, debug=False)
