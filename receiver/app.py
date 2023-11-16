import connexion
from connexion import NoContent
import yaml
import logging
import logging.config
import uuid
import datetime
import json
from pykafka import KafkaClient
import time

# Load the app config file
with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

# Load the log config file
with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

# Initialize KafkaClient at startup
try:
    logger.info("Initializing Kafka client")
    kafka_client = KafkaClient(hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}")
    kafka_topic = kafka_client.topics[str.encode(app_config['events']['topic'])]
    producer = kafka_topic.get_sync_producer()
except Exception as e:
    logger.error(f"Failed to initialize Kafka client: {str(e)}")
    raise e

def send_to_kafka(event_type, payload):
    msg = {
        "type": event_type,
        "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "payload": payload
    }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

def borrow_book(body):
    trace_id = str(uuid.uuid4())
    logger.info(f"Received event borrow_book request with a trace id of {trace_id}")
    body['trace_id'] = trace_id
    send_to_kafka("borrow_book", body)
    logger.info(f"Pushed borrow_book event to Kafka (Id: {trace_id})")
    return NoContent, 201

def return_book(body):
    trace_id = str(uuid.uuid4())
    logger.info(f"Received event return_book request with a trace id of {trace_id}")
    body['trace_id'] = trace_id
    send_to_kafka("return_book", body)
    logger.info(f"Pushed return_book event to Kafka (Id: {trace_id})")
    return NoContent, 201

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8080)
