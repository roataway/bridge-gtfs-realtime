# bridge-gtfs-realtime
Expose the MQTT data stream in a GTFS realtime feeds format


## Prerequisites

1. The [static GTFS data](https://github.com/roataway/gtfs-data) must be available as a ZIP file.
2. Ensure you can connect to [opendata.dekart.com](https://github.com/roataway/api-documentation) over MQTT.
3. Create a virtualenv and install the dependencies from `requirements.txt`.

### Producing the static GTFS feed

TODO figure out where to store it and how to get it, maybe use a git subrepo?


## Usage
1. Run `python api.py` to start the bridge
2. Open `http://localhost:5000/get_data` to access the realtime feed