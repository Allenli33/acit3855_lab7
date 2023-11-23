import connexion
from connexion import NoContent
import yaml
import logging.config
import logging
import requests
import json
import datetime
import os.path
from apscheduler.schedulers.background import BackgroundScheduler
from flask_cors import CORS, cross_origin
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

# Stub out a method called populate_stats() in app.py
def populate_stats():
    logger.info("Start Periodic Processing")

    # Read in the current statistics from the JSON file
    filename = app_config['datastore']['filename']
    if not os.path.isfile(filename):
        current_stats = {
            "num_bb_received": 0,
            "num_rb_received": 0,
            "avg_borrow_duration": 0.0,
            "avg_return_duration": 0.0,
            "max_return_late_fee": 0.0,
            "last_updated": "2000-01-01T00:00:00Z"
        }
    # Write the default values to the JSON file

    else:
        with open(filename, 'r') as f:
            current_stats = json.load(f)

    #last_updated = current_stats['last_updated']

    # Fetch new events

    current_timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    last_updated = current_stats['last_updated']

    borrow_events_response = requests.get(
        f"{app_config['eventstore']['url']}/records/borrow?timestamp={last_updated}&end_timestamp={current_timestamp}")
    return_events_response = requests.get(
        f"{app_config['eventstore']['url']}/records/return?timestamp={last_updated}&end_timestamp={current_timestamp}")

    if borrow_events_response.status_code != 200:
        logger.error(
            f"Error fetching borrow events: {borrow_events_response.status_code}")
        borrow_events = []
    else:
        borrow_events = borrow_events_response.json()
        logger.info(f"Received {len(borrow_events)} new borrow events.")

    if return_events_response.status_code != 200:
        logger.error(
            f"Error fetching return events: {return_events_response.status_code}")
        return_events = []
    else:
        return_events = return_events_response.json()
        logger.info(f"Received {len(return_events)} new return events.")

    # Update stats
    current_stats["num_bb_received"] += len(borrow_events)
    current_stats["num_rb_received"] += len(return_events)

    total_borrow_duration = sum(event['borrow_duration']
                                for event in borrow_events)
    total_return_duration = sum(event['return_duration']
                                for event in return_events)

    if borrow_events:
        current_stats['avg_borrow_duration'] = int(
            total_borrow_duration / len(borrow_events))

    if return_events:
        current_stats['avg_return_duration'] = int(
            total_return_duration / len(return_events))
        current_stats['max_return_late_fee'] = max(
            event['late_fee'] for event in return_events)

    current_stats["last_updated"] = current_timestamp

    # Save updated stats
    with open(filename, 'w') as f:
        json.dump(current_stats, f, indent=4)

    logger.debug(f"Updated stats: {current_stats}")
    logger.info("End Periodic Processing.")


# Schedule it to be called periodically based on your ‘periodic_sec’ interval from your configuration file
def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats,
                  'interval',
                  seconds=app_config['scheduler']['period_sec'])
    sched.start()


def get_stats():
    """ Gets event statistics """
    logger.info("GET /events/stats request started")

    # Read in the current statistics from the JSON file
    filename = app_config['datastore']['filename']

    if not os.path.isfile(filename):
        logger.error("Statistics do not exist")
        return {"message": "Statistics do not exist"}, 404
    else:
        with open(filename, 'r') as f:
            current_stats = json.load(f)

    # Assuming the structure in the file matches the structure of the response,
    # there's no conversion required. Otherwise, you'd do the conversion here.

    logger.debug(f"Statistics: {current_stats}")
    logger.info("GET /events/stats request completed")
    return current_stats, 200


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", base_path="/processing", strict_validation=True, validate_responses=True)
if "TARGET_ENV" not in os.environ or os.environ["TARGET_ENV"] != "test":
    CORS(app.app)
    app.app.config['CORS_HEADERS'] = 'Content-Type'

if __name__ == "__main__":
    # run our standalone gevent server
    init_scheduler()
    app.run(port=8100)  # Change the port to 8100
