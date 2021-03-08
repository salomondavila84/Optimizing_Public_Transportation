import time
from confluent_kafka.avro import AvroConsumer, CachedSchemaRegistryClient
from confluent_kafka.cimpl import OFFSET_BEGINNING

BROKER_URL = "127.0.0.1:9092"
SCHEMA_REGISTRY_URL = "http://127.0.0.1:8081"
schema_registry = CachedSchemaRegistryClient({"url": SCHEMA_REGISTRY_URL})

def on_assign(c, partitions):
    """Callback for when topic assignment takes place"""
    for partition in partitions:
        partition.offset = OFFSET_BEGINNING  # not 0 since it will take the smallest offset
    c.assign(partitions)

c = AvroConsumer({"bootstrap.servers": BROKER_URL, "group.id": "kafka_consumer"}, schema_registry=schema_registry)
#TOPIC_NAME = "cta.stations.arrivals.ohare"
#c.subscribe([TOPIC_NAME], on_assign=on_assign)
c.subscribe(["^cta.stations.arrivals."], on_assign=on_assign)


if __name__ == "__main__":
    while True:
        message = c.poll(0.1)
        if message is None:
            print("no message received by consumer")
        elif message.error() is not None:
            print(f"error from consumer {message.error()}")
        else:
            try:
                print(message.topic())
                print(message.value())
            except KeyError as e:
                print(f"Failed to unpack message {e}")
        time.sleep(0.1)