import binascii
import datetime
import json
from hashlib import sha256
from typing import Union
from urllib.parse import urlparse

import Crypto
import requests
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5


class Transaction:
    def __init__(self, sender, recipient, value, signature=None):
        self.sender = sender
        self.recipient = recipient
        self.value = value
        self.signature = signature

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
    def __init__(self, index, transactions, timestamp, previous_hash, hash=None, nonce=None):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = hash

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
    nodes = set()

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

    def register_node(self, node_url):
        # Checking node_url has valid format
        parsed_url = urlparse(node_url)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            # Accepts an URL without scheme like '192.168.0.5:5000'.
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError('Invalid URL')

    def consensus(self):
        neighbours = self.nodes

        new_chain = None
        # We're only looking for chains longer than ours
        max_length = len(self.chain)
        # Grab and verify the chains from all the nodes in our network
        for node in neighbours:
            response = requests.get('http://' + node + '/fullchain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                # Check if the length is longer and the chain is valid
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain
        # Replace our chain if longer chain is found
        if new_chain:
            self.chain = json.loads(new_chain)
            return True
        return False

    def valid_chain(self, chain):
        # check if a blockchain is valid
        current_index = 0
        chain = json.loads(chain)
        while current_index < len(chain):
            block = json.loads(chain[current_index])
            current_block = Block(block['index'],
                                  block['transactions'],
                                  block['timestamp'],
                                  block['previous_hash'],
                                  block['hash'],
                                  block['nonce'])
            if current_index + 1 < len(chain):
                if current_block.compute_hash() != json.loads(chain[current_index + 1])['previous_hash']:
                    return False
            if isinstance(current_block.transactions, list):
                for transaction in current_block.transactions:
                    transaction = json.loads(transaction)
                    # skip Block reward because it does not have signature
                    if transaction['sender'] == 'Block_Reward':
                        continue
                    current_transaction = Transaction(transaction['sender'],
                                                      transaction['recipient'],
                                                      transaction['value'],
                                                      transaction['signature'])
                    # validate digital signature of each transaction
                    if not current_transaction.verify_transaction_signature():
                        return False
                    if not self.is_valid_proof(current_block, block['hash']):
                        return False
            current_index += 1
        return True
