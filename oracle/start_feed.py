from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
import atexit
import os
import datetime
from time import sleep

from .oracle import OracleServer
from . import api

oracle_address = os.environ.get('ORACLE_ADDRESS')
key = os.environ.get('TEZOS_USER_KEY')
env = os.environ.get('ENV')
instrument = os.environ.get("INSTRUMENT")

class Feed:
    def __init__(self, tezos_key, contract_address, instrument, env):
        self.instrument = instrument
        self.oracle = OracleServer(
                tezos_key=tezos_key, 
                oracle_contract_address=contract_address, 
                environment=env
            )

    def update_oracle(self, in_browser=False):
        """Fetch and parse data and update Oracle contract"""
        data = api.fetch_and_parse_price_data(self.instrument)
        result = str(self.oracle.update_value(data))
        result_str = (f"\nFeed: {self.instrument}\nTimestamp: {datetime.datetime.utcnow().isoformat()} \nResult: {result}\n")
        print(result_str)
        return result_str if not in_browser else f"<pre>{result_str}</pre>"

    def start_feed(self):
        oracle_update_scheduler = BackgroundScheduler()
        oracle_update_scheduler.start()
        oracle_update_scheduler.add_job(func=self.update_oracle, trigger="interval", seconds=60)
        atexit.register(lambda: oracle_update_scheduler.shutdown())

feed = Feed(key, oracle_address, instrument, env)

feed.start_feed()

app = Flask(__name__)

@app.route('/')
def index():
    return feed.update_oracle(in_browser=True), 200