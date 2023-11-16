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
import time
import os

# Check environment and set configuration file paths
if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"

# Load application configuration
with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())

# External Logging Configuration
with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

# Create a logger from the basicLogger defined in the configuration file
logger = logging.getLogger('basicLogger')
logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)

# Initialize KafkaClient at startup
def get_kafka_client():
    retry_count = 0
    max_retries = app_config['kafka']['max_retries']
    sleep_time = app_config['kafka']['retry_delay_sec']

    while retry_count < max_retries:
        try:
            logger.info(f"Trying to connect to Kafka, attempt {retry_count+1}")
            client = KafkaClient(hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}")
            kafka_topic = client.topics[str.encode(app_config['events']['topic'])]
            producer = kafka_topic.get_sync_producer()
            logger.info("Connected to Kafka successfully")
            return client, producer
            
        except Exception as e:
            logger.error(f"Connection to Kafka failed: {str(e)}")
            time.sleep(sleep_time)
            retry_count += 1
    raise Exception("Failed to connect to Kafka after retries")

client, producer = get_kafka_client()
    
def send_to_kafka(event_type, payload):
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
