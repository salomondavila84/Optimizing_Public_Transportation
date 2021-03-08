# Public Transit Status with Apache Kafka

Development of streaming event pipeline around Apache Kafka using public data from the [Chicago Transit Authority](https://www.transitchicago.com/data/). The event pipeline simulates and displays the status of train lines in real time.

Monitor website to watch trains move from station to station.

![Final User Interface](images/ui.png)


## Stack

* Docker
  - Docker compose used for Confluent Kafka images and postgresql 11
* Python 3.7
  - use of confluent, faust, Avro, and various custom classes


## Description

The Chicago Transit Authority (CTA) required a dashboard displaying system status for its commuters. Kafka's ecosystem with tools like REST Proxy and Kafka Connect were explored to achieve this task.

Architecture will look like so:

![Project Architecture](images/diagram.png)

### Step 1: Kafka Producers
Configure the train stations to emit the events. Sensor data simulates an action whenever a train arrives at the station.


1. `producers/models/producer.py`
1. Define a `value` schema for the arrival event in `producers/models/schemas/arrival_value.json` with the following attributes
	* `station_id`
	* `train_id`
	* `direction`
	* `line`
	* `train_status`
	* `prev_station_id`
	* `prev_direction`
1. `producers/models/station.py` :
	* A topic is created for each station in Kafka to track the arrival events
	* The station emits an `arrival` event to Kafka whenever the `Station.run()` function is called.
	* Ensure that events emitted to kafka are paired with the Avro `key` and `value` schemas
1. value` schema for the turnstile event in `producers/models/schemas/turnstile_value.json` with attributes
	* `station_id`
	* `station_name`
	* `line`
1. `producers/models/turnstile.py` :
	* A topic is created for each turnstile for each station in Kafka to track the turnstile events
	* The station emits a `turnstile` event to Kafka whenever the `Turnstile.run()` function is called.
	* events emitted with the Avro `key` and `value` schemas

### Step 2: Configure Kafka REST Proxy Producer
Our partners at the CTA have asked to send weather readings into Kafka from their weather hardware. Unfortunately, this hardware is old and we cannot use the Python Client Library due to hardware restrictions. Instead, the HTTP REST can send the data to Kafka from the hardware using Kafka's REST Proxy.


1. `value` schema for the weather event in `producers/models/schemas/weather_value.json` with attributes
	* `temperature`
	* `status`
1.  `producers/models/weather.py` :
	* A topic is created for weather events
	* The weather model emits `weather` event to Kafka REST Proxy whenever the `Weather.run()` function is called.
		* **NOTE**: HTTP requests to Kafka REST Proxy need to include the correct `Content-Type`. 
	* Events emitted to REST Proxy are paired with the Avro `key` and `value` schemas

### Step 3: Configure Kafka Connect
Extract station information from PostgreSQL database into Kafka using Kafka connect JDBC source connector

1. `producers/connectors.py`
	* Kafka Connect JDBC Source Connector Configuration Options
	* use the [Landoop Kafka Connect UI](http://localhost:8084) and [Landoop Kafka Topics UI](http://localhost:8085) to check the status and output of the Connector.
	* To delete a misconfigured connector: `CURL -X DELETE localhost:8083/connectors/stations`

### Step 4: Configure the Faust Stream Processor
Faust Stream Processing to transform the raw Stations table from Kafka Connect. The raw format from the database has superfluous data and the line color information is not conveniently configured. Need to ingest data from our Kafka Connect topic, and transform the data.

1. `consumers/faust_stream.py`
	* run this Faust processing application with the following command:
	* `faust -A faust_stream worker -l info`
	* On Pycharm use `worker` under *Parameters*

### Step 5: KSQL Table
Aggregate turnstile data for each of our stations. Need a count of tunstile events in a streaming format. Useful to summarize by station for an up-to-date count


1. `consumers/ksql.py`
* The KSQL CLI  `ksql` 
*  `python ksql.py`
*  `DROP TABLE <your_table>`. CLI  terminate a running query, `TERMINATE <query_name>`


### Step 6: Create Kafka Consumers
Consume the data in the web server to serve the transit status pages to commuters.


1. `consumers/consumer.py`
1. `consumers/models/line.py`
1. `consumers/models/weather.py`
1. `consumers/models/station.py`

### Documentation

* [Confluent Python Client Documentation](https://docs.confluent.io/current/clients/confluent-kafka-python/#)
* [Confluent Python Client Usage and Examples](https://github.com/confluentinc/confluent-kafka-python#usage)
* [REST Proxy API Reference](https://docs.confluent.io/current/kafka-rest/api.html#post--topics-(string-topic_name))
* [Kafka Connect JDBC Source Connector Configuration Options](https://docs.confluent.io/current/connect/kafka-connect-jdbc/source-connector/source_config_options.html)

## Directory Layout
The project consists of two main directories, `producers` and `consumers`.

The following directory layout indicates the files

```

├── consumers
│   ├── consumer.py *
│   ├── faust_stream.py *
│   ├── ksql.py *
│   ├── models
│   │   ├── lines.py
│   │   ├── line.py *
│   │   ├── station.py *
│   │   └── weather.py *
│   ├── requirements.txt
│   ├── server.py
│   ├── topic_check.py
│   └── templates
│       └── status.html
└── producers
    ├── connector.py *
    ├── models
    │   ├── line.py
    │   ├── producer.py *
    │   ├── schemas
    │   │   ├── arrival_key.json
    │   │   ├── arrival_value.json *
    │   │   ├── turnstile_key.json
    │   │   ├── turnstile_value.json *
    │   │   ├── weather_key.json
    │   │   └── weather_value.json *
    │   ├── station.py *
    │   ├── train.py
    │   ├── turnstile.py *
    │   ├── turnstile_hardware.py
    │   └── weather.py *
    ├── requirements.txt
    └── simulation.py
```

## Running and Testing

```%> docker-compose up```


| Service | Host URL | Docker URL | Username | Password |
| --- | --- | --- | --- | --- |
| Public Transit Status | [http://localhost:8888](http://localhost:8888) | n/a | ||
| Landoop Kafka Connect UI | [http://localhost:8084](http://localhost:8084) | http://connect-ui:8084 |
| Landoop Kafka Topics UI | [http://localhost:8085](http://localhost:8085) | http://topics-ui:8085 |
| Landoop Schema Registry UI | [http://localhost:8086](http://localhost:8086) | http://schema-registry-ui:8086 |
| Kafka | PLAINTEXT://localhost:9092,PLAINTEXT://localhost:9093,PLAINTEXT://localhost:9094 | PLAINTEXT://kafka0:9092,PLAINTEXT://kafka1:9093,PLAINTEXT://kafka2:9094 |
| REST Proxy | [http://localhost:8082](http://localhost:8082/) | http://rest-proxy:8082/ |
| Schema Registry | [http://localhost:8081](http://localhost:8081/ ) | http://schema-registry:8081/ |
| Kafka Connect | [http://localhost:8083](http://localhost:8083) | http://kafka-connect:8083 |
| KSQL | [http://localhost:8088](http://localhost:8088) | http://ksql:8088 |
| PostgreSQL | `jdbc:postgresql://localhost:5432/cta` | `jdbc:postgresql://postgres:5432/cta` | `cta_admin` | `chicago` |

access to services from local machine, will use the `Host URL` column.

configuring services that run within Docker Compose, like **Kafka Connect you must use the Docker URL**. When you configure the JDBC Source Kafka Connector, for example, use the value from the `Docker URL` column.

### Running the Simulation

Pieces to the simulation, the `producer` and `consumer`. In development only run one piece of the project at a time.


#### To run the `producer`:

1. `cd producers`
2. `virtualenv venv`
3. `. venv/bin/activate`
4. `pip install -r requirements.txt`
5. `python simulation.py`

Once the simulation is running, you may hit `Ctrl+C` at any time to exit.

#### To run the Faust Stream Processing Application:
1. `cd consumers`
2. `virtualenv venv`
3. `. venv/bin/activate`
4. `pip install -r requirements.txt`
5. `faust -A faust_stream worker -l info`


#### To run the KSQL Creation Script:
1. `cd consumers`
2. `virtualenv venv`
3. `. venv/bin/activate`
4. `pip install -r requirements.txt`
5. `python ksql.py`

#### To run the `consumer`:

** NOTE **: Do not run the consumer until you have reached Step 6!
1. `cd consumers`
2. `virtualenv venv`
3. `. venv/bin/activate`
4. `pip install -r requirements.txt`
5. `python server.py`

Once the server is running, you may hit `Ctrl+C` at any time to exit.
