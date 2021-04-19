# Overview
Expose the Roataway MQTT data stream in a GTFS realtime feed format

## Principle of operation
This program subscribes to the (route-specific MQTT topic)[https://github.com/roataway/api-documentation#telemetryroute],
consumes all incoming payloads and maintains an internal data structure with the latest known info about each vehicle.

The following table illustrates how attributes of the MQTT payloads are mapped to entries in the GTFS `FeedMessage`:

| Source attribute   | Target attribute                     | Notes                                  |
|--------------------|--------------------------------------|----------------------------------------|
| `timestamp`        | `VehiclePosition.timestamp`          |                                        |
| `latitude`         | `VehiclePosition.Position.latitude`  |                                        |
| `longitude`        | `VehiclePosition.Position.longitude` |                                        |
| `speed`            | `VehiclePosition.Position.speed`     |                                        |
| `direction`        | `VehiclePosition.Position.bearing`   |                                        |
| `board`            | `VehicleDescriptor.label`            | Board number, e.g. `"3890"`            |
| `rtu_id`           | `VehicleDescriptor.id`               | Tracker ID, e.g. `"0000123"`           |
| `route`            | `TripDescriptor.route_id`            | Human-readable route name, e.g. `"30"` |
| `route` (in topic) | not exposed                          | route_id_upstream, e.g. `1`            |


## Prerequisites

1. The [static GTFS data](https://github.com/roataway/gtfs-data) must be available as a ZIP file.
2. Ensure you can connect to [opendata.dekart.com](https://github.com/roataway/api-documentation) over MQTT.
3. Create a virtualenv and install the dependencies from `requirements.txt`.

### Producing the static GTFS feed

TODO figure out where to store it and how to get it, maybe use a git subrepo?


## Usage
### Serving the GTFS stream
1. Run `python app.py` to start the bridge
2. Open `http://localhost:5000` to view the current state of the worker in textual format

Other endpoints:
- `http://localhost:5000/get_gtfs_rt` - retrieve the live GTFS feed as ProtoBuf
- `http://localhost:5000/get_gtfs_static`- retrieve the complete static GTFS data set as an archive

### Consuming a GTFS stream
For testing purposes, you might need to consume your own feed to see if it looks right. You can do so by running
`python consumer.py <GTFS RT feed URL>`, e.g., `python consumer.py http://localhost:5000/get_gtfs_rt`. The data will
be dumped to stdout.


## References

- https://developers.google.com/transit/gtfs-realtime/reference
- https://github.com/roataway/api-documentation