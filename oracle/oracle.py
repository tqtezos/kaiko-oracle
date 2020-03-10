from pytezos import pytezos, Key

class OracleServer:
    def __init__(self, tezos_key, oracle_contract_address, environment):
        self.oracle_contract_address = oracle_contract_address
        self.pytezos_instance = pytezos.using(shell=environment, key=tezos_key)

    def oracle_contract(self):
        return self.pytezos_instance.contract(self.oracle_contract_address)

    def update_value(self, data):
        try:
            operation_group = self.oracle_contract().update_value(data).operation_group
            operation_str = operation_group.autofill().sign().inject()
            storage_str = self.oracle_contract().storage()
            return f"Last operation: {operation_str}\n\nPrevious storage: {storage_str}\n"
        except Exception as e:
            exception_doc = f"Exception: {str(e.__doc__)}"
            exception_message = None
            try:
                exception_message = f"{str(e.message)}"
            except:
                exception_message = f"(unknown message: {e.__class__.__name__})"
            return (exception_doc + exception_message)
