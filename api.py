from datetime import datetime
import logging
import json

import flask
from flask import jsonify, send_from_directory
import paho.mqtt.client as mqtt
from gtfs_realtime import create_gtfs_proto_entity

q = []

def on_message(client, userdata, message):
    q.append([message.topic, message.payload])


client_id = "bridge-gtfs-realtime"
client = mqtt.Client(client_id)

client.on_message = on_message

# ne conectăm, indicând adresa și portu din documentație
client.connect("opendata.dekart.com", port=1945)

# indicăm un ”topic” la care ne abonăm, pentru a primi telemetrie actuală
client.subscribe("telemetry/transport/+")

app = flask.Flask(__name__)
app.config["DEBUG"] = True
idd = 0


@app.route('/get_gtfs_static', methods=['GET'])
def gtfs_file():
    return send_from_directory(".", "./GTFS_Chisinau/Archive.zip", as_attachment=True)


prev_stamp = None

@app.route('/get_data', methods=['GET'])
def home():
    client.loop_read(100)

    if (len(q) >= 1):
        message = q.pop()
        my_json = message[1].decode('utf8').replace("'", '"')
        topic = message[0]
        data = json.loads(my_json)
        feed = create_gtfs_proto_entity(
            q,
            timestamp=datetime.now().timestamp(),
        )
        print(feed)
        f = open("feed.pb", "wb")
        # f.write(feed.SerializeToString())
        if ("0" in topic):
            f.write(feed.SerializeToString())
            print(data['timestamp'])
            f.close()
            return send_from_directory(".", "./feed.pb", as_attachment=True)
        else:
            # print(data['timestamp'])
            f.close()
            return send_from_directory(".", "./feed.pb", as_attachment=True)



    else:
        f = open("feed.pb", "wb")
        return send_from_directory(".", "./feed.pb", as_attachment=True)


app.run()
