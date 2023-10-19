import connexion
from connexion import NoContent
import requests
import yaml
import logging
import logging.config
import uuid
import datetime
import json
from pykafka import KafkaClient

# load the app config file
with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

# load the log config file
with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

# Create a logger from the basicLogger defined in the configuration file. Make sure to import the logging
# and logging.config modules.
logger = logging.getLogger('basicLogger')


def send_to_kafka(event_type, payload):
    client = KafkaClient(
        hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}")
    topic = client.topics[str.encode(app_config['events']['topic'])]
    producer = topic.get_sync_producer()

    msg = {
        "type": event_type,
        "datetime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "payload": payload
    }
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))


# Function to handle borrowing a book
def borrow_book(body):

    # Generate a unique trace_id
    trace_id = str(uuid.uuid4())

    # Log the receipt of the event request
    logger.info(
        f"Received event borrow_book request with a trace id of {trace_id}")

    # save the newely generated trace_id to the body
    body['trace_id'] = trace_id

    # get the request data
    send_to_kafka("borrow_book", body)

    # Log the return of the event response
    # Log the successful event push
    logger.info(f"Pushed borrow_book event to Kafka (Id: {trace_id})")

    # return a 201 status code
    return NoContent, 201

# Function to handle returning a book


def return_book(body):

    # Generate a unique trace_id
    trace_id = str(uuid.uuid4())

    # Log the receipt of the event request
    logger.info(
        f"Received event return_book request with a trace id of {trace_id}")

    # save the newely generated trace_id to the body
    body['trace_id'] = trace_id

    # Create a structured request_data sentence for returning
    send_to_kafka("return_book", body)

    # Log the return of the event response with the trace_id
    # Log the successful event push

    logger.info(f"Pushed return_book event to Kafka (Id: {trace_id})")
    # return a 201 status code
    return NoContent, 201


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8080)
