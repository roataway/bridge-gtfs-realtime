from datetime import datetime
import logging
from io import BytesIO
import json

import eventlet
from flask import Flask, send_file, make_response
from flask_mqtt import Mqtt
from flask_socketio import SocketIO
from expiringdict import ExpiringDict

from structures import FeedEntity
from gtfs_realtime import create_gtfs_proto_entity
import constants as c
from util import random_word

LOG = logging.getLogger("app")

eventlet.monkey_patch()

# global dict that maintains state, the key is a string that represents the board id,
# and the value is a FeedEntity that represents the last known state of this vehicle
STATE = ExpiringDict(max_len=c.MAX_VEHICLES, max_age_seconds=c.STATE_TTL)

app = Flask(__name__)
app.config["MQTT_BROKER_URL"] = c.MQTT_BROKER
app.config["MQTT_BROKER_PORT"] = c.MQTT_PORT
app.config["MQTT_REFRESH_TIME"] = 1.0
app.logger.propagate = False


mqtt = Mqtt(app)
socketio = SocketIO(app)


@mqtt.on_connect()
def handle_connect(_client, _userdata, _flags, _rc):
    mqtt.subscribe("telemetry/route/+")


@mqtt.on_message()
def handle_mqtt_message(_client, _userdata, message):
    payload = message.payload.decode()
    route_id = message.topic.split("/")[-1]
    # LOG.debug('%s->%s', message.topic, route_id)

    try:
        data = json.loads(payload)
    except ValueError:
        LOG.debug("Payload parsing error, ignoring it")
        return

    # if we got this far, it means we're dealing with something like this:
    # {"latitude": 47.037993, "longitude": 28.817931, "speed": 0, "direction": 151, "timestamp": "2021-04-07T21:39:12Z",
    #  "board": "1273", "rtu_id": "0000289", "route": "22"}
    board_id = data["board"]
    try:
        state = STATE[board_id]
    except KeyError:
        # we've never seen this board before, let's create a data structure for it
        state = FeedEntity(data, route_id)
        STATE[board_id] = state
        LOG.info("New board %s\t %s", board_id, state)
    else:
        # we've seen it before, we just update some of the attributes
        timestamp = datetime.strptime(data["timestamp"], c.FORMAT_TIME)
        state.vehicle_timestamp = timestamp.timestamp()
        state.id = random_word(6)  # TODO is this necessary?
        state.vehicle_position_lat = data["latitude"]
        state.vehicle_position_lot = data["longitude"]
        state.vehicle_speed = data["speed"] / 3.6  # convert to m/s
        state.vehicle_route_id = route_id  # we overwrite it each time, in case it moved to a different route


@app.route("/", methods=["GET"])
def index():
    """Serve a simple status page that returns a string with the current state of all the vehicles"""
    pieces = [f"{board}: {status}" for board, status in STATE.items()]

    result = f"Total vehicles: {len(STATE)}\n\n"
    response = make_response(result + "\n".join(pieces), 200)
    response.mimetype = "text/plain"
    return response


@app.route("/get_gtfs_static", methods=["GET", "POST"])
def gtfs_static():
    LOG.debug("Send GTFS static")
    return send_file("regia-chisinau-md_regia-chisinau-md_1605016016_regia-chisinau-md.zip", as_attachment=True)


@app.route("/get_data", methods=["GET", "POST"])
def gtfs_realtime():
    LOG.debug("Send live feed, %i entries", len(STATE))
    feed = create_gtfs_proto_entity(STATE)
    if feed is not None:
        mem = BytesIO()
        mem.write(feed.SerializeToString())
        mem.seek(0)
        return send_file(mem, as_attachment=True, attachment_filename="c.pb", mimetype="application/protobuf")
    else:
        LOG.debug("No feed to send")
        return c.NO_CONTENT


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)5s %(funcName)s - %(message)s")

    host = "localhost"
    port = 5000
    LOG.info("Starting on %s:%i", host, port)
    socketio.run(app, host=host, port=port, use_reloader=True, debug=False)
