from datetime import datetime

import eventlet
from flask import Flask, render_template, send_file, send_from_directory
from flask_mqtt import Mqtt
from flask_socketio import SocketIO

from FeedEntity import FeedEntity
from gtfs_realtime import create_gtfs_proto_entity

eventlet.monkey_patch()

app = Flask(__name__)
app.config['MQTT_BROKER_URL'] = 'opendata.dekart.com'
app.config['MQTT_BROKER_PORT'] = 1945
app.config['MQTT_REFRESH_TIME'] = 1.0

mqtt = Mqtt(app)
socketio = SocketIO(app)
d_q = dict()

@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    mqtt.subscribe("telemetry/route/+")


@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    data = dict(
        topic=message.topic,
        payload=message.payload.decode()
    )
    #print(data)
    feedEntity = FeedEntity(data["payload"], data["topic"].split("/")[2], datetime.now().timestamp())
    #print(feedEntity.vehicle_id)
    if feedEntity.vehicle_trip_id == "57" and (feedEntity.vehicle_id == "1334" or feedEntity.vehicle_id == "1325") :
        #print("----", data)
        if feedEntity.vehicle_id not in d_q:
            d_q[feedEntity.vehicle_id] = list()
        d_q[feedEntity.vehicle_id].append(feedEntity)
        #print(d_q)
       # socketio.emit('mqtt_message', data=data)


@app.route("/get_gtfs_static", methods=["GET", "POST"])
def gtfs_file():
    print("download gtfs")
    return send_file("regia-chisinau-md_regia-chisinau-md_1605016016_regia-chisinau-md.zip", as_attachment=True)

@app.route('/get_data', methods=['GET', 'POST'])
def index():
    print("download feed")
    print(len(d_q))
    feed = create_gtfs_proto_entity(d_q)
    print("-------------------------------------------------")
    print("-------------------------------------------------")
    print("-------------------------------------------------")
    if feed is not None:
        with open('c.pb', 'wb') as f:
            print(feed)
            f.write(feed.SerializeToString())
    else:
        print("feed is none")
    return send_from_directory(directory=".", filename="c.pb", attachment_filename="c.pb")


@mqtt.on_log()
def handle_logging(client, userdata, level, buf):
    pass


socketio.run(app, host='192.168.100.11', port=5000, use_reloader=True, debug=True)
