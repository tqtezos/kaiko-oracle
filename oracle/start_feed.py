from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
import atexit
import os
import datetime
import json
from time import sleep

from oracle.oracle import OracleServer
from oracle import api

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

    def update_oracle(self):
        """Fetch and parse data and update Oracle contract"""
        try:
            data = api.fetch_and_parse_price_data(self.instrument)
            result = self.oracle.update_value(data)
            return result
        except Exception as e:
            exception_doc = f"Exception: {str(e.__doc__)}"
            exception_message = None
            try:
                exception_message = f"{str(e.message)}"
            except:
                exception_message = f"(unknown message: {e.__class__.__name__})"
            return (exception_doc + exception_message)

    def pretty_print_result(self, operation_res, storage="", in_browser=False):
        op_str = f"Last operation: {json.dumps(operation_res, indent=4)}\n\nPrevious storage: {storage}\n"
        result_str = (f"\nFeed: {self.instrument}\nTimestamp: {datetime.datetime.utcnow().isoformat()} \nResult: {op_str}\n")
        print(result_str)
    
        return result_str if not in_browser else f"<pre>{result_str}</pre>"

    def start_feed(self):
        oracle_update_scheduler = BackgroundScheduler()
        oracle_update_scheduler.start()
        oracle_update_scheduler.add_job(func=self.update_oracle, trigger="interval", seconds=10)
        atexit.register(lambda: oracle_update_scheduler.shutdown())

feed = Feed(key, oracle_address, instrument, env)

# feed.start_feed()

# app = Flask(__name__)

# @app.route('/')
# def index():
#     return feed.pretty_print_result(*feed.update_oracle(), in_browser=True), 200