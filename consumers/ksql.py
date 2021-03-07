"""Configures KSQL to combine station and turnstile data
Confirmation:
[{"@type":"currentStatus","statementText":"CREATE TABLE turnstile (\n     station_id INTEGER,\n     station_name VARCHAR,\n     line VARCHAR\n) WITH (\n    KAFKA_TOPIC='cta.turnstile',\n    VALUE_FORMAT='avro',\n    KEY='station_id'\n);","commandId":"table/TURNSTILE/create","commandStatus":{"status":"SUCCESS","message":"Table created"},"commandSequenceNumber":0},{"@type":"currentStatus","statementText":"CREATE TABLE turnstile_summary\nWITH (KAFKA_TOPIC = 'TURNSTILE_SUMMARY', VALUE_FORMAT= 'json') AS\n    SELECT station_id, COUNT(station_id) AS count\n    FROM turnstile\n    GROUP BY station_id;","commandId":"table/TURNSTILE_SUMMARY/create","commandStatus":{"status":"SUCCESS","message":"Table created and running"},"commandSequenceNumber":1}]

Manual Construction:
% docker exec -it kafka_project_ksql_1 bash
# ksql
ksql> server; http://localhost:8088
ksql> show topics;
ksql> CREATE TABLE turnstile (station_id INTEGER, station_name VARCHAR, line VARCHAR) WITH (KAFKA_TOPIC='cta-turnstile', VALUE_FORMAT='AVRO', KEY='station_id');
ksql> set 'auto.offset.reset'='earliest';
ksql> select * from TURNSTILE limit 10;

1612264738857 |     �����] | 40900 | Howard | red
1612264739016 |     �¼��] | 41400 | Roosevelt | red
1612264739029 |     �ü��] | 40240 | 79th | red
1612264739272 |     �Ƽ��] | 40610 | Ridgeland | green
1612264738504 |     ں���] | 40570 | California | blue
1612264738549 |     »���] | 40490 | Grand | blue
1612264738563 |     컼��] | 40380 | Clark/Lake | blue
1612264739328 |     �Ǽ��] | 41360 | California | green
1612264738608 |     ļ���] | 40430 | Clinton | blue
1612264738631 |     似��] | 40350 | UIC-Halsted | blue
Limit Reached
Query terminated

ksql> CREATE TABLE turnstile_summary with (KAFKA_TOPIC='TURNSTILE_SUMMARY', VALUE_FORMAT= 'JSON') AS SELECT station_id, COUNT(station_id) AS count FROM turnstile GROUP BY station_id;

Message
---------------------------
 Table created and running
---------------------------

ksql> SELECT * FROM TURNSTILE_SUMMARY LIMIT 10;
1612264776424 | 40590 | 40590 | 1
1612264852645 | 40430 | 40430 | 3
1612264862883 | 40130 | 40130 | 3
1612264867940 | 41000 | 41000 | 5
1612264878057 | 40230 | 40230 | 2
1612264878061 | 41240 | 41240 | 3
1612264893293 | 40750 | 40750 | 3
1612264893354 | 40380 | 40380 | 5
1612264893356 | 40260 | 40260 | 1
1612264933987 | 40100 | 40100 | 5
Limit Reached
Query terminated

ksql> terminate CTAS_TURNSTILE_SUMMARY_1;

 Message
-------------------
 Query terminated.
-------------------

ksql> drop table turnstile;

 Message
--------------------------------
 Source TURNSTILE was dropped.
--------------------------------
ksql> drop table turnstile_summary;

 Message
----------------------------------------
 Source TURNSTILE_SUMMARY was dropped.
----------------------------------------

% kafka-topics --zookeeper 127.0.0.1:2181 --topic TURNSTILE_SUMMARY --delete
"""
import json
import logging

import requests

import topic_check


logger = logging.getLogger(__name__)


KSQL_URL = "http://localhost:8088"

#
# TODO: Complete the following KSQL statements.
# TODO: For the first statement, create a `turnstile` table from your turnstile topic.
#       Make sure to use 'avro' datatype!
# TODO: For the second statement, create a `turnstile_summary` table by selecting from the
#       `turnstile` table and grouping on station_id.
#       Make sure to cast the COUNT of station id to `count`
#       Make sure to set the value format to JSON

KSQL_STATEMENT = """
CREATE TABLE turnstile (
     station_id INTEGER,
     station_name VARCHAR,
     line VARCHAR
) WITH (
    KAFKA_TOPIC='cta.turnstile',
    VALUE_FORMAT='avro',
    KEY='station_id'
);

CREATE TABLE turnstile_summary
WITH (KAFKA_TOPIC = 'TURNSTILE_SUMMARY', VALUE_FORMAT= 'json') AS
    SELECT station_id, COUNT(station_id) AS count
    FROM turnstile
    GROUP BY station_id;
"""


def execute_statement():
    """Executes the KSQL statement against the KSQL API"""
    if topic_check.topic_exists("TURNSTILE_SUMMARY") is True:
        return

    logging.debug("executing ksql statement...")

    resp = requests.post(
        f"{KSQL_URL}/ksql",
        headers={"Content-Type": "application/vnd.ksql.v1+json"},
        data=json.dumps(
            {
                "ksql": KSQL_STATEMENT,
                "streamsProperties": {"ksql.streams.auto.offset.reset": "earliest"},
            }
        ),
    )

    # Ensure that a 2XX status code was returned
    resp.raise_for_status()
    print(resp.text)


if __name__ == "__main__":
    execute_statement()
