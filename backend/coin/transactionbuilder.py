from typing import Type, TypeVar, List

from coin import util
from coin.config import Config
from coin.domain import Transaction, InputInfo, OutputInfo

T = TypeVar('T')


class NewTransactionViewModel:

    def __init__(self, utxos: List[InputInfo], amount: int, output_address: str, change_address: str):
        self.utxos = utxos
        self.amount = amount
        self.outputs: List[OutputInfo] = [
            OutputInfo(amount, output_address)
        ]

        # compute change
        total_utxo_amount = sum([x.amount for x in self.utxos])
        change = total_utxo_amount - self.amount - Config.FEE_PER_TRANSACTION
        if change > 0:
            self.outputs.append(OutputInfo(change, change_address))
        else:
            raise Exception("The sender does not have enough to pay for the transaction")

    @classmethod
    def from_json_request(cls: Type[T], data) -> T:
        utxos = [InputInfo.from_json(x) for x in data['utxos']]
        amount = int(data['amount'])
        output_address = data['output_address']
        change_address = data['change_address']
        return NewTransactionViewModel(utxos, amount, output_address, change_address)

    def build(self) -> Transaction:
        tx = Transaction(util.random_id(), Transaction.REGULAR, hash_=None, inputs=self.utxos, outputs=self.outputs)
        tx.hash = tx.compute_hash()
        return tx


class TransactionBuilder:
    def __init__(self, list_of_utxo: List[InputInfo] = None, output_address=None, total_amount=None,
                 change_address=None,
                 fee_amount=None,
                 secret_key=None):
        self.list_of_utxo = list_of_utxo
        self.output_address = output_address
        self.total_amount = total_amount
        self.change_address = change_address
        self.fee_amount = fee_amount
        self.secret_key = secret_key
        self.type = Transaction.REGULAR

    def process_utxo(self, utxo: InputInfo) -> InputInfo:
        utxo_hash = util.crypto_hash({
            'transaction': utxo.tx_hash,
            'index': utxo.index,
            'address': utxo.address
        })
        utxo.signature = util.sign_hash(self.secret_key, utxo_hash)
        return utxo

    def build(self):
        if self.list_of_utxo is None:
            raise Exception("It's necessary to inform a list of unspent output transactions")
        if self.output_address is None:
            raise Exception("It's necessary to inform the destination address")
        if self.total_amount is None:
            raise Exception("It's necessary to inform the transaction value")

        total_utxo_amount = sum([x.amount for x in self.list_of_utxo])
        change = total_utxo_amount - self.total_amount - self.fee_amount

        inputs = [self.process_utxo(x) for x in self.list_of_utxo]
        outputs = [
            OutputInfo(self.total_amount, self.output_address)
        ]
        if change >= 0:
            outputs.append(OutputInfo(change, self.change_address))
        else:
            raise Exception("The sender does not have enough to pay for the transaction")

        return {
            'inputs': inputs,
            'outputs': outputs,
            'id': util.random_id(),
            'type': self.type,
            'hash': None
        }
