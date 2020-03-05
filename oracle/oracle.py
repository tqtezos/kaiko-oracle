from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timezone
from flask import Flask
from pytezos import pytezos, Key
import atexit, base64, os, tempfile

import api

oracle_address = os.environ['ORACLE_ADDRESS']

tezos_user_key = None
with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as key_file:
    key_file.write(base64.standard_b64decode(os.environ['TEZOS_USER_KEY']))
    key_file.close()
    tezos_user_key = Key.from_faucet(key_file.name)
    os.remove(key_file.name)

class OracleServer:
    def __init__(self, tezos_key=tezos_user_key, oracle_contract_address=oracle_address):
        self.oracle_contract_address = oracle_contract_address
        self.pytezos_instance = pytezos.using(key=tezos_key, shell='babylonnet')

    def oracle_contract(self):
        return self.pytezos_instance.contract(self.oracle_contract_address)

    def update_value(self):
        try:
            now_utc = datetime.now(tz=timezone.utc)
            operation_group = self.oracle_contract().update_value(value_timestamp=now_utc, value=self.price()).operation_group
            operation_str = f"<p> Last operation:\n{operation_group.autofill().sign().inject()} </p>"
            storage_str = f"<p> Current storage:\n{self.oracle_contract().storage()} </p>"
            return (operation_str + storage_str)
        except Exception as e:
            exception_doc = f"<p> Exception: {str(e.__doc__)} </p>"
            exception_message = None
            try:
                exception_message = f"<p> {str(e.message)} </p>"
            except:
                exception_message = f"(unknown message: {e.__class__.__name__})"
            return (exception_doc + exception_message)

    def price(self):
        quote_data, expected_none = self.time_series.get_quote_endpoint(self.ticker_symbol)
        if expected_none is None:
            try:
                return int(float(quote_data['05. price']) * 100)
            except KeyError:
                raise f"expected key: '05. price' in {str(quote_data)}"
        else:
            raise f"expected_none not None: {str(expected_none)}"

def update_oracle():
    result_str = str(OracleServer().update_value())
    print('')
    print(result_str)
    print('')
    return result_str

app = Flask(__name__)

@app.route('/')
def index():
    return update_oracle(), 200

oracle_update_scheduler = BackgroundScheduler()
oracle_update_scheduler.add_job(func=update_oracle, trigger="interval", seconds=30)
oracle_update_scheduler.start()
atexit.register(lambda: oracle_update_scheduler.shutdown())

