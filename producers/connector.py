"""Configures a Kafka Connector for Postgres Station data
make sure postgres isn't running:

 Start -> Run -> "services.msc"
 diable the postgres service

$ curl http://127.0.0.1:8083/connectors/stations | python -m json.tool
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   673  100   673    0     0   657k      0 --:--:-- --:--:-- --:--:--  657k
{
    "name": "stations",
    "config": {
        "connector.class": "io.confluent.connect.jdbc.JdbcSourceConnector",
        "incrementing.column.name": "stop_id",
        "connection.password": "chicago",
        "tasks.max": "1",
        "batch.max.rows": "500",
        "table.whitelist": "stations",
        "mode": "incrementing",
        "key.converter.schemas.enable": "false",
        "topic.prefix": "cta.",
        "connection.user": "cta_admin",
        "poll.interval.ms": "50000",
        "value.converter.schemas.enable": "false",
        "name": "stations",
        "connection.url": "jdbc:postgresql://postgres:5432/cta",
        "value.converter": "org.apache.kafka.connect.json.JsonConverter",
        "key.converter": "org.apache.kafka.connect.json.JsonConverter"
    },
    "tasks": [
        {
            "connector": "stations",
            "task": 0
        }
    ],
    "type": "source"
}

"""
import json
import logging

import requests


logger = logging.getLogger(__name__)


KAFKA_CONNECT_URL = "http://localhost:8083/connectors"
CONNECTOR_NAME = "stations"

def configure_connector():
    """Starts and configures the Kafka Connect connector"""
    logging.debug("creating or updating kafka connect connector...")

    resp = requests.get(f"{KAFKA_CONNECT_URL}/{CONNECTOR_NAME}")
    if resp.status_code == 200:
        logging.debug("connector already created skipping recreation")
        return

    # TODO: Complete the Kafka Connect Config below.
    # Directions: Use the JDBC Source Connector to connect to Postgres. Load the `stations` table
    # using incrementing mode, with `stop_id` as the incrementing column name.
    # Make sure to think about what an appropriate topic prefix would be, and how frequently Kafka
    # Connect should run this connector (hint: not very often!)

    # TODO: Complete the Kafka Connect Config below.
    # Directions: Use the JDBC Source Connector to connect to Postgres. Load the `stations` table
    # using incrementing mode, with `stop_id` as the incrementing column name.
    # Make sure to think about what an appropriate topic prefix would be, and how frequently Kafka
    # Connect should run this connector (hint: not very often!)

    resp = requests.post(
        KAFKA_CONNECT_URL,
        headers={"Content-Type": "application/json"},
        data=json.dumps(
            {
                "name": CONNECTOR_NAME,
                "config": {
                    "connector.class": "io.confluent.connect.jdbc.JdbcSourceConnector",
                    "connection.url": "jdbc:postgresql://postgres:5432/cta",  # ToDo: Note db location
                    "connection.user": "cta_admin",  # per docker-compose
                    "connection.password": "chicago",  # per docker-compose
                    "key.converter": "org.apache.kafka.connect.json.JsonConverter",
                    "key.converter.schemas.enable": "false",
                    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
                    "value.converter.schemas.enable": "false",
                    "batch.max.rows": "500",
                    "topic.prefix": "cta.",  # prefix added to topic
                    "mode": "incrementing",  # bulk, incrementing, or timestamp
                    "incrementing.column.name": "stop_id",  # REQUIRED in table, automatic increasing
                    "table.whitelist": "stations",  # table with station data, added to prefix for topic name
                    "tasks.max": 1,
                    "poll.interval.ms": "50000"
                }
            }
        ),
    )

    ## Ensure a healthy response was given
    resp.raise_for_status()
    logging.debug("connector created successfully")


if __name__ == "__main__":
    configure_connector()
