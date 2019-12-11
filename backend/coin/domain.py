import binascii
from collections import OrderedDict
from typing import List
from typing import TypeVar, Type, Optional

import Crypto
from Crypto.PublicKey import RSA

from coin import util
from coin.config import Config

T = TypeVar('T')


class InputInfo:
    def __init__(self, tx_hash, index, amount, address, signature=None):
        self.tx_hash = tx_hash
        self.index = index  # index of the transaction taken from a previous unspent transaction output
        self.amount = amount  # amount of satoshis
        self.address = address  # from address
        # transaction input hash: sha256 (tx_hash + index + amount + address)
        # signed with owner's address secret key (128 bytes)
        self.signature = signature

    @classmethod
    def from_json(cls: Type[T], data) -> T:
        return InputInfo(data['transaction'], data['index'], data['amount'], data['address'], data['signature'])

    def to_json(self):
        return OrderedDict({
            'index': self.index,
            'transaction': self.tx_hash,
            'address': self.address,
            'amount': self.amount
        })

    def check(self) -> bool:
        return util.verify(self.address, self.to_json(), self.signature)


class OutputInfo:
    def __init__(self, amount, address):
        self.amount = amount  # amount of satoshis
        self.address = address  # to address

    @classmethod
    def from_json(cls: Type[T], data) -> T:
        return OutputInfo(data['amount'], data['address'])

    def to_json(self) -> dict:
        return OrderedDict({
            'amount': self.amount,
            'address': self.address
        })


class Transaction:
    REGULAR = 'regular'
    REWARD = 'reward'
    FEE = 'fee'
    """
    Transaction structure:
    { 
        "id": "84286bba8d...7477efdae1", // random id (64 bytes)
        "hash": "f697d4ae63...c1e85f0ac3", // hash taken from the contents of the transaction: sha256 (id + data) (64 bytes)
        "type": "regular", // transaction type (regular, fee, reward)
        "inputs": [
            {
                "transaction": "9e765ad30c...e908b32f0c", // transaction hash taken from a previous unspent transaction output (64 bytes)
                "index": "0", // index of the transaction taken from a previous unspent transaction output
                "amount": 5000000000, // amount of satoshis
                "address": "dda3ce5aa5...b409bf3fdc", // from address (64 bytes)
                "signature": "27d911cac0...6486adbf05" // transaction input hash: sha256 (transaction + index + amount + address) signed with owner address's secret key (128 bytes)
            }
        ],
        "outputs": [
            {
                "amount": 10000, // amount of satoshis
                "address": "4f8293356d...b53e8c5b25" // to address (64 bytes)
            },
            {
                "amount": 4999989999, // amount of satoshis
                "address": "dda3ce5aa5...b409bf3fdc" // change address (64 bytes)
            }
        ]
    }
    """

    def __init__(self, id_, type_=None, hash_=None, inputs: List[InputInfo] = None,
                 outputs: List[OutputInfo] = None):
        self.inputs = inputs
        self.outputs = outputs
        self.type = type_
        self.id = id_
        self.hash = hash_

    def to_dict(self):
        return {
            'inputs': [x.to_json() for x in self.inputs],
            'outputs': [x.to_json() for x in self.outputs],
        }

    def to_json(self) -> dict:
        return {
            'id': self.id,
            'type': self.type,
            'inputs': [x.to_json() for x in self.inputs],
            'outputs': [x.to_json() for x in self.outputs],
            'hash': self.hash,
        }

    def to_json_no_hash(self) -> dict:
        val = self.to_json()
        val.pop('hash')
        return val

    @classmethod
    def from_json(cls: Type[T], data, compute_hash=False) -> T:
        tx = Transaction(id_=data['id'], hash_=data['hash'], type_=data['type'],
                         inputs=[InputInfo.from_json(x) for x in data['inputs']],
                         outputs=[OutputInfo.from_json(x) for x in data['outputs']])
        if compute_hash:
            tx.hash = tx.compute_hash()
        return tx

    def add_signature(self, signature):
        self.hash = signature

    def check(self) -> bool:
        if self.hash != self.compute_hash():
            print("Uneven tx hashes", self.type)
            return False
        if not all([x.check() for x in self.inputs]):
            print("jdfdsf")
            return False

        # for regular type
        if self.type == Transaction.REGULAR:
            inputs_sum = sum([x.amount for x in self.inputs])
            outputs_sum = sum([x.amount for x in self.outputs])

            if inputs_sum < outputs_sum:
                return False

            # if enough fee
            if not (inputs_sum - outputs_sum >= Config.FEE_PER_TRANSACTION):
                print("Fee not enough")
                return False

            # make sure there's no negative output
            if any([x.amount < 0 for x in self.outputs]):
                return False
        return True

    def compute_hash(self) -> str:
        return util.crypto_hash(self.to_json_no_hash()).hexdigest()


class Wallet:
    def __init__(self, id_: str, _public_key: bytes, _private_key: bytes = None):
        self.id = id_
        self._public_key = _public_key
        self._private_key = _private_key

    @property
    def identity(self) -> bytes:
        return self._public_key

    @property
    def identity_private(self) -> Optional[bytes]:
        return self._private_key

    @staticmethod
    def from_json(data):
        id_ = data['id']
        public_key = data['public_key']
        private_key = data.get('private_key')
        return Wallet(id_, public_key, private_key)

    @staticmethod
    def generate():
        random = Crypto.Random.new().read
        private_key = RSA.generate(1024, random)
        public_key = private_key.publickey()
        private_key = binascii.hexlify(private_key.export_key(format='DER')).decode('utf8')
        public_key = binascii.hexlify(public_key.exportKey(format='DER')).decode('utf8')
        return Wallet(util.random_id(), public_key, private_key)

    def to_json(self) -> dict:
        return {
            'id': self.id,
            'public_key': self.identity,
            'private_key': self.identity_private
        }

    def sign_transaction(self, transaction: Transaction) -> Transaction:
        signer = util.import_rsa_key(self.identity_private)
        for input_ in transaction.inputs:
            h = util.hash_str(input_.tx_hash + str(input_.index) + str(input_.amount) + input_.address)
            input_.signature = util.sign_hash(signer, h)
        transaction.hash = util.crypto_hash(transaction.to_json_no_hash()).hexdigest()
        return transaction


class Block:
    def __init__(self, index, transactions: List[Transaction], timestamp, previous_hash, hash_: str = None, nonce=None):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = hash_

    def to_json_no_hash(self):
        val = self.to_json()
        val.pop('hash')
        return val

    def to_json(self) -> dict:
        return OrderedDict({
            'index': self.index,
            'transactions': [x.to_json() for x in self.transactions],
            'timestamp': self.timestamp,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce,
            'hash': self.hash
        })

    @classmethod
    def from_json(cls: Type[T], data: dict) -> T:
        return Block(data['index'], [Transaction.from_json(x) for x in data['transactions']],
                     data['timestamp'], data['previous_hash'], data.get('hash'), data['nonce'])

    def compute_hash(self) -> str:
        return util.crypto_hash(self.to_json_no_hash()).hexdigest()
