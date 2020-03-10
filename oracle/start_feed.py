from apscheduler.schedulers.background import BackgroundScheduler
# from flask import Flask
import atexit, base64, os, tempfile

from .oracle import OracleServer
from . import api

oracle_address = os.environ.get('ORACLE_ADDRESS', "KT1SerVULB4f8o1awYu3fsKvfcLjTyj9qSd1")
key = os.environ.get('TEZOS_USER_KEY', "edsk3gUfUPyBSfrS9CCgmCiQsTCHGkviBDusMxDJstFtojtc1zcpsh")
env = os.environ.get('ENV', "http://localhost:18731")
instrument = os.environ.get("INSTRUMENT", "xtz-btc")


tezos_user_key = key
# with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as key_file:
#     key_file.write(base64.standard_b64decode(key))
#     key_file.close()
#     tezos_user_key = Key.from_faucet(key_file.name)
#     os.remove(key_file.name)


class Feed:
    def __init__(self, tezos_key, contract_address, instrument, env):
        self.tezos_key = tezos_key
        self.contract_address = contract_address
        self.instrument = instrument
        self.env = env

    def update_oracle(self):
        data = api.fetch_and_parse_price_data(self.instrument)
        print(self.instrument, data)
        result_str = str(
            OracleServer(
                tezos_key=self.tezos_key, 
                oracle_contract_address=self.contract_address, 
                environment=self.env
            ).update_value(data)
        )
        print(f"\n{result_str}\n")
        return result_str

    def start_feed(self):
        oracle_update_scheduler = BackgroundScheduler()
        oracle_update_scheduler.add_job(func=self.update_oracle, trigger="interval", seconds=60)
        oracle_update_scheduler.start()
        atexit.register(lambda: oracle_update_scheduler.shutdown())

# app = Flask(__name__)

# @app.route('/')
# def index():
#     return Feed()update_oracle(), 200

# "http://localhost:18731" "babylonnet"

Feed(key, oracle_address, instrument, env).start_feed()