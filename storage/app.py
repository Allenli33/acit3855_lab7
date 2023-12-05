import connexion
from connexion import NoContent
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from borrow_book import BorrowRecord  # Import BorrowBook class
from return_book import ReturnRecord  # Import ReturnBook class
import yaml
import logging.config
import logging
import datetime
from flask import request
import json
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread
from sqlalchemy import and_
import time
import os

# Check environment and set configuration file paths
if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    APP_CONF_FILE = "/config/app_conf.yml"
    LOG_CONF_FILE = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    APP_CONF_FILE = "app_conf.yml"
    LOG_CONF_FILE = "log_conf.yml"

# Load application configuration
with open(APP_CONF_FILE, 'r', encoding='utf-8') as f:
    app_config = yaml.safe_load(f.read())

# External Logging Configuration
with open(LOG_CONF_FILE, 'r', encoding='utf-8') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')
logger.info("App Conf File: %s", APP_CONF_FILE)
logger.info("Log Conf File: %s", LOG_CONF_FILE)

# Access specific configuration settings
db_user = app_config['datastore']['user']
db_password = app_config['datastore']['password']
db_hostname = app_config['datastore']['hostname']
db_port = app_config['datastore']['port']
db_name = app_config['datastore']['db']

# Create database connection

DB_ENGINE = create_engine(
    f'mysql+pymysql://{db_user}:{db_password}@{db_hostname}:{db_port}/{db_name}')
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)
#hostname= "allenliacit3855.eastus.cloudapp.azure.com"
#port= 3306
logger.info(f"Connecting to DB. Hostname:{db_hostname}, Port:{db_port}.")


def process_messages():
    """Process event messages."""
    max_retries = app_config['kafka']['max_retries']
    retry_delay_sec = app_config['kafka']['retry_delay_sec']
    retry_count = 0
    while retry_count < max_retries:
        try:
            logger.info(f"Trying to connect to Kafka, attempt {retry_count+1}")
            hostname = f"{app_config['events']['hostname']}:{app_config['events']['port']}"
            client = KafkaClient(hosts=hostname)
            topic = client.topics[str.encode(app_config["events"]["topic"])]
            consumer = topic.get_simple_consumer(
                consumer_group=b'event_group',
                reset_offset_on_start=False,
                auto_offset_reset=OffsetType.LATEST
            )
            logger.info("Successfully connected to Kafka")
            break
        except Exception as e:
            logger.error(f"Connection to Kafka failed on attempt {retry_count+1}: {e}")
            retry_count += 1
            if retry_count < max_retries:
                time.sleep(retry_delay_sec)
            else:
                logger.error("Maximum retry attempts reached, could not connect to Kafka")
               


    # This is blocking - it will wait for a new message
    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        logger.info("Message: %s" % msg)
        payload = msg["payload"]
        msg_type = msg["type"]
        session = DB_SESSION()

        if msg["type"] == "borrow_book":
            # Store the borrow_book event (i.e., the payload) to the DB
            # Your DB code here
            # TODO: create a database session
            br = BorrowRecord(
                user_id=payload['user_id'],
                book_id=payload['book_id'],
                borrow_date=payload['borrow_date'],
                borrower_name=payload['borrower_name'],
                borrow_duration=payload['borrow_duration'],
                late_fee=payload['late_fee'],
                trace_id=payload['trace_id']
            )
            session.add(br)
            logger.info(
                "Stored event borrow_book request with a trace id of %s", payload['trace_id'])
           #logger.debug("Stored event borrow_book request with a trace id of %s", payload['trace_id'])

        elif msg["type"] == "return_book":
            # Store the return_book event (i.e., the payload) to the DB
            # Your DB code here
            rr = ReturnRecord(
                user_id=payload['user_id'],
                book_id=payload['book_id'],
                return_date=payload['return_date'],
                returner_name=payload['returner_name'],
                return_duration=payload['return_duration'],
                late_fee=payload['late_fee'],
                trace_id=payload['trace_id']
            )
            session.add(rr)
            logger.info(
                "Stored event return_book request with a trace id of %s", payload['trace_id'])
            #logger.debug("Stored event return_book request with a trace id of %s", payload['trace_id'])

        # Commit the new message as being read
        session.commit()
        session.close()
        consumer.commit_offsets()



def get_borrow_records_by_timestamp(timestamp, end_timestamp):
    """ Gets borrow records created on or after the given timestamp """
    session = DB_SESSION()
    logger.info("testing for assignment3")

    try:
        timestamp_datetime = datetime.datetime.strptime(
            timestamp, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        return {"message": "Invalid timestamp format. Please use the format 'YYYY-MM-DDTHH:MM:SSZ'"}, 400
    
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%SZ")

    borrow_records = session.query(BorrowRecord).filter(
        and_(BorrowRecord.date_created >= timestamp_datetime, BorrowRecord.date_created < end_timestamp_datetime))

    results_list = []

    for record in borrow_records:
        results_list.append(record.to_dict())

    session.close()

    logger.info("Query for borrow records after %s returns %d results",
                timestamp, len(results_list))

    return results_list, 200


def get_return_records_by_timestamp(timestamp, end_timestamp):
    """ Gets return records created on or after the given timestamp """
    session = DB_SESSION()

    try:
        timestamp_datetime = datetime.datetime.strptime(
            timestamp, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        return {"message": "Invalid timestamp format. Please use the format 'YYYY-MM-DDTHH:MM:SSZ'"}, 400
    
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%SZ")
    
    return_records = session.query(ReturnRecord).filter(
        and_(ReturnRecord.date_created >= timestamp_datetime, ReturnRecord.date_created < end_timestamp_datetime))

    results_list = []

    for record in return_records:
        results_list.append(record.to_dict())

    session.close()

    logger.info("Query for return records after %s returns %d results",
                timestamp, len(results_list))

    return results_list, 200


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", base_path="/storage", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()
    app.run(port=8090)
