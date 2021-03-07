"""Defines trends calculations for stations

Edit Run Configuration:
Parameters "worker"

faust_stream.py worker
+ƒaµS† v1.10.4+---------------------------------------------------------------------------------------+
| id          | stations-stream                                                                       |
| transport   | [URL('kafka://localhost:9092')]                                                       |
| store       | memory:                                                                               |
| web         | http://scopewave:6066                                                                 |
| log         | -stderr- (warn)                                                                       |
| pid         | 24068                                                                                 |
| hostname    | ScopeWave                                                                             |
| platform    | CPython 3.7.6 (Windows AMD64)                                                         |
| drivers     |                                                                                       |
|   transport | aiokafka=1.1.6                                                                        |
|   web       | aiohttp=3.6.2                                                                         |
| datadir     | D:\PycharmProjects\Optimizing_Public_transportation\consumers\stations-stream-data    |
| appdir      | D:\PycharmProjects\Optimizing_Public_transportation\consumers\stations-stream-data\v1 |
+-------------+---------------------------------------------------------------------------------------+
 OK ^
[2021-03-07 05:32:55,935] [24068] [WARNING] 40010: <TransformedStation: station_id=40010, station_name='Austin', order=29, line='blue'>
[2021-03-07 05:32:55,937] [24068] [WARNING] 40010: <TransformedStation: station_id=40010, station_name='Austin', order=29, line='blue'>
...
"""
import logging

import faust


logger = logging.getLogger(__name__)


# Faust will ingest records from Kafka in this format
class Station(faust.Record):
    stop_id: int
    direction_id: str
    stop_name: str
    station_name: str
    station_descriptive_name: str
    station_id: int
    order: int
    red: bool
    blue: bool
    green: bool


# Faust will produce records to Kafka in this format
class TransformedStation(faust.Record):
    station_id: int
    station_name: str
    order: int
    line: str


# TODO: Define a Faust Stream that ingests data from the Kafka Connect stations topic and
#   places it into a new topic with only the necessary information.
app = faust.App("stations-stream", broker="kafka://localhost:9092", store="memory://")
# TODO: Define the input Kafka Topic. Hint: What topic did Kafka Connect output to?
topic = app.topic("cta.stations", value_type=Station)  # adding 'cta.' due to topic.prefix
# TODO: Define the output Kafka Topic
out_topic = app.topic("cta.stations.table", key_type=str, partitions=1, value_type=TransformedStation)
# TODO: Define a Faust Table
table = app.Table("station.summary",
                  default=TransformedStation,
                  partitions=1,
                  changelog_topic=out_topic,)


# TODO: Using Faust, transform input `Station` records into `TransformedStation` records. Note that
# "line" is the color of the station. So if the `Station` record has the field `red` set to true,
# then you would set the `line` of the `TransformedStation` record to the string `"red"`
#
@app.agent(topic)
async def transform_event(stream):
    async for event in stream:
        transformed_station = TransformedStation(
            station_id=event.station_id,
            station_name=event.station_name,
            order=event.order,
            line="red" if event.red == True else "blue" if event.blue == True else "green"
        )
        await out_topic.send(key="New Data: ", value=transformed_station)
        table[event.station_id] = transformed_station
        print(f"{event.station_id}: {table[event.station_id]}")


if __name__ == "__main__":
    app.main()
