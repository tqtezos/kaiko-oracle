import json
from pytezos import pytezos, Key

class OracleServer:
    def __init__(self, tezos_key, oracle_contract_address, environment):
        self.oracle_contract_address = oracle_contract_address
        self.pytezos_instance = pytezos.using(shell=environment, key=tezos_key)

    def oracle_contract(self):
        return self.pytezos_instance.contract(self.oracle_contract_address)

    def update_value(self, data):
        storage = self.oracle_contract().storage()
        
        # If no data is returned from api, reinsert previous storage
        update_val = data if data[1] is not None else storage[:2]  

        operation_group = self.oracle_contract().update_value(update_val).operation_group
        operation_res = operation_group.autofill().sign().inject()
    
        return (operation_res, storage)
