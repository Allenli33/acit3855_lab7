import datetime
import json
import requests
import yaml
import logging
import logging.config
import uuid
import sqlite3
import os
import socket
import time
import connexion
from apscheduler.schedulers.background import BackgroundScheduler
from create_health import Healths
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from flask_cors import CORS, cross_origin
from connexion import NoContent

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"

with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())
    
with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')


sqliteUrl = "sqlite:///%s" % app_config["datastore"]["filename"]
logger.info(sqliteUrl)
DB_ENGINE = create_engine(sqliteUrl)
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)



def create_table(sql_path):
    conn = sqlite3.connect(sql_path)
    c = conn.cursor()

    c.execute('''
            CREATE TABLE IF NOT EXISTS healths
            (id INTEGER PRIMARY KEY ASC,
            receiver VARCHAR(30) NOT NULL,
            storage VARCHAR(30) NOT NULL,
            processing VARCHAR(30) NOT NULL,
            audit VARCHAR(30) NOT NULL,
            last_updated VARCHAR(100) NOT NULL)
    ''')

    conn.commit()
    conn.close()


def get_status(body):
    for sec in range(app_config["scheduler"]["max_tries"]):
        try:
            health_check = requests.get(app_config['receiver_url']+'/health')
            body["receiver"] = "Up"
            break
        except Exception:
            body["receiver"] = "Down"
            time.sleep(app_config["scheduler"]['sleep'])
            continue

    for sec in range(app_config["scheduler"]["max_tries"]):
        try:
            health_check = requests.get(app_config['storage_url']+'/health')
            body["storage"] = "Up"
            break
        except Exception:
            body["storage"] = "Down"
            time.sleep(app_config["scheduler"]['sleep'])
            continue

    for sec in range(app_config["scheduler"]["max_tries"]):
        try:
            health_check = requests.get(app_config['processing_url']+'/health')
            body["processing"] = "Up"
            break
        except Exception:
            body["processing"] = "Down"
            time.sleep(app_config["scheduler"]['sleep'])
            continue

    for sec in range(app_config["scheduler"]["max_tries"]):
        try:
            health_check = requests.get(app_config['audit_url']+'/health')
            body["audit"] = "Up"
            break
        except Exception:
            body["audit"] = "Down"
            time.sleep(app_config["scheduler"]['sleep'])
            continue

    return body


def get_health():
    '''Get all the Stats objects from the database in descending order'''
    logger.info("Requesting healths has started")

    session = DB_SESSION()
    results = session.query(Healths).order_by(
        Healths.last_updated.desc()).all()
    session.close()

    results_list = []

    if results != []:
        for reading in results:
            results_list.append(reading.to_dict())
        logger.debug(results_list)
        logger.info("Requesting healths has ended")
        return results_list[0], 200

    static_list = {
        "receiver": "Down",
        "storage": "Down",
        "processing": "Down",
        "audit": "Down",
        "last_updated": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    }

    static_list = get_status(static_list)

    logger.error("Healths do not exist")
    logger.info("Requesting healths has ended")
    return static_list, 404


def create_healths(body):
    '''write a new Healths object to the database'''

    session = DB_SESSION()

    healths = Healths(body["receiver"],
                      body["storage"],
                      body["processing"],
                      body["audit"],
                      datetime.datetime.strptime(body["last_updated"],
                                                 "%Y-%m-%dT%H:%M:%S"))
    session.add(healths)
    session.commit()
    session.close()

    return NoContent, 201


def populate_healths():
    """ Periodically update healths """
    logger.info("Start Health Check")

    currentStat = get_health()

    body = get_status(currentStat[0])

    body['last_updated'] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    create_healths(body)

    logger.debug("Updated info: " + json.dumps(body))
    logger.info("Health Check is ended")


def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_healths,
                  'interval',
                  seconds=app_config['scheduler']['period_sec'])
    sched.start()


app = connexion.FlaskApp(__name__, specification_dir="")
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("openapi.yml", base_path = "/health", strict_validation=True, validate_responses=True)



if __name__ == "__main__":
    create_table(app_config["datastore"]["filename"])
    init_scheduler()
    app.run(port=8120, use_reloader=False)