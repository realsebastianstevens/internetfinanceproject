import datetime
import json
from hashlib import sha256
from typing import Union

class Transaction:
    def __init__(self, sender, recipient, value):
        self.sender = sender
        self.recipient = recipient
        self.value = value
        self.signature = None

    def to_dict(self):
        return {
            'sender': self.sender,
            'recipient': self.recipient,
            'value': self.value
        }

    def to_json(self):
        return json.dumps(self.__dict__, sort_keys=False)

    def add_signature(self, signature):
        self.signature = signature

    def verify_transaction_signature(self):
        if self.signature:
            public_key = RSA.import_key(binascii.unhexlify(self.sender))
            verifier = PKCS1_v1_5.new(public_key)
            h = SHA.new(str(self.to_dict()).encode('utf8'))
            return verifier.verify(h, binascii.unhexlify(self.signature))
        return False


class Wallet:
    def __init__(self):
        random = Crypto.Random.new().read
        self._private_key = RSA.generate(1024, random)
        self._public_key = self._private_key.publickey()

    @property
    def identity(self):
        prvtkey = binascii.hexlify(self._private_key.export_key(format='DER'))
        pubkey = binascii.hexlify(self._public_key.exportKey(format='DER'))
        return pubkey.decode('ascii')

    @property
    def identity_private(self):
        prvtkey = binascii.hexlify(self._private_key.export_key(format='DER'))
        return prvtkey.decode('ascii')

    def sign_transaction(self, transaction):
        signer = PKCS1_v1_5.new(self._private_key)
        h = SHA.new(str(transaction.to_dict()).encode('utf8'))
        return binascii.hexlify(signer.sign(h)).decode('ascii')


class Block:
    def __init__(self, index, transactions, timestamp, previous_hash, nonce=None):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = None

    def to_dict(self):
        return {
            'index': self.index,
            'transactions': self.transactions,
            'timestamp': self.timestamp,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce
        }

    def to_json(self):
        return json.dumps(self.__dict__)

    def compute_hash(self) -> str:
        return sha256(str(self.to_dict()).encode()).hexdigest()


class Blockchain:
    difficulty = 2

    def __init__(self):
        self.unconfirmed_transactions = []
        self.chain = []
        self.create_genesis_block()

    @property
    def last_block(self) -> Union[dict, None]:
        if len(self.chain) > 0:
            return json.loads(self.chain[-1])
        return None

    def create_genesis_block(self):
        block_reward = Transaction('Block_Reward', '', '5.0').to_json()
        genesis_block = Block(0, block_reward,
                              Blockchain.datetime_now(),
                              None, None
                              )
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block.to_json())

    def add_new_transaction(self, transaction: Transaction) -> bool:
        if transaction.verify_transaction_signature():
            self.unconfirmed_transactions.append(transaction.to_json())
            return True
        return False

    def add_block(self, block: Block, proof: str) -> bool:
        previous_hash = self.last_block['hash'] if self.last_block else None
        if previous_hash and previous_hash != block.previous_hash:
            return False
        if not Blockchain.is_valid_proof(block, proof):
            return False
        block.hash = proof
        self.chain.append(block.to_json())
        return True

    def mine(self, wallet: Wallet):
        block_reward = Transaction("Block_Reward", wallet.identity, "5.0").to_json()

        self.unconfirmed_transactions.insert(0, block_reward)
        if not self.unconfirmed_transactions:
            return False

        new_block = Block(self.last_block['index'] + 1,
                          transactions=self.unconfirmed_transactions,
                          timestamp=Blockchain.datetime_now(),
                          previous_hash=self.last_block['hash'])
        proof = Blockchain.proof_of_work(new_block)
        if self.add_block(new_block, proof):
            self.unconfirmed_transactions = []
            return new_block
        return False

    @staticmethod
    def datetime_now() -> str:
        return datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")

    @staticmethod
    def is_valid_proof(block: Block, block_hash: str) -> bool:
        return block_hash.startswith('0' * Blockchain.difficulty) and block_hash == block.compute_hash()

    @staticmethod
    def proof_of_work(block: Block):
        block.nonce = 0
        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0' * Blockchain.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()
        return computed_hash
