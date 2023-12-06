import datetime
import json
import requests
import yaml
import logging
import logging.config
import sqlite3
import os
import connexion
from apscheduler.schedulers.background import BackgroundScheduler
from create_health import Healths
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from flask_cors import CORS, cross_origin
from connexion import NoContent

# Environment setup
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

# Database setup
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

# Check service health
def check_service_health(url):
    ''''checks the health of a given service by making an HTTP GET request to endpoint. It returns "Running" if it gets a 200 response within 5 seconds; otherwise, it returns "Down"'''
    try:
        response = requests.get(url, timeout=5)
        return "Running" if response.status_code == 200 else "Down"
    except requests.RequestException:
        return "Down"

def get_status():
    ''' checks the health status of all the services (receiver, storage, processing, audit) and returns a dictionary containing their statuses and the last updated timestamp'''
    body = {
        "receiver": check_service_health(app_config['receiver_url'] + '/health'),
        "storage": check_service_health(app_config['storage_url'] + '/health'),
        "processing": check_service_health(app_config['processing_url'] + '/health'),
        "audit": check_service_health(app_config['audit_url'] + '/health'),
        "last_updated": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    logger.info(f"Health Check Update: {json.dumps(body)}")
    return body

def get_health():
    '''Retrieve health status from the database'''
    logger.info("Requesting healths has started")
    session = DB_SESSION()
    results = session.query(Healths).order_by(Healths.last_updated.desc()).all()
    session.close()
    if results:
        logger.info("Requesting healths has ended")
        return results[0].to_dict(), 200
    else:
        logger.error("Healths do not exist")
        return get_status(), 404

def create_healths(body):
    '''Writes a new health check record to the database. It constructs a Healths object from the provided status data and saves it to the database.'''
    session = DB_SESSION()
    healths = Healths(body["receiver"], body["storage"], body["processing"], body["audit"], datetime.datetime.strptime(body["last_updated"], "%Y-%m-%dT%H:%M:%SZ"))
    session.add(healths)
    session.commit()
    session.close()
    return NoContent, 201

def populate_healths():
    '''called periodically by the scheduler. It obtains the current status of each service using get_status and stores this information in the database using create_healths.'''
    logger.info("Start Health Check")
    body = get_status()
    create_healths(body)
    logger.info("Health Check Ended")

def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_healths, 'interval', seconds=app_config['scheduler']['period_sec'])
    sched.start()

# Flask application setup
app = connexion.FlaskApp(__name__, specification_dir="")
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("openapi.yml", base_path="/health", strict_validation=True, validate_responses=True)

@app.route('/health', methods=['GET'])
def get_health_status():
    '''calls get_health to retrieve the latest health statuses and returns them in JSON format.'''
    status, code = get_health()
    logger.info("Health status retrieved")
    return json.dumps(status), code

if __name__ == "__main__":
    create_table(app_config["datastore"]["filename"])
    init_scheduler()
    app.run(port=8120, use_reloader=False)
