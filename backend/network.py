import Crypto
import Crypto.Random
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA
import binascii
import json
import requests
from domain import Blockchain as Bl5
from flask import Flask, jsonify, request
from urllib.parse import urlparse
import sys
from hashlib import sha256

app = Flask(__name__)

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
class Blockchain(Bl5):

    difficulty = 2
    nodes = set()

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


@app.route('/new_transaction', methods=['POST'])
def new_transaction():
    values = request.form
    required = ['recipient_address', 'amount']
    # Check that the required fields are in the POST data
    if not all(k in values for k in required):
        return 'Missing values', 400
    transaction = Transaction(myWallet.identity,
    values['recipient_address'], values['amount'])
    transaction.add_signature(myWallet.sign_transaction(transaction))
    transaction_result = blockchain.add_new_transaction(transaction)
    if transaction_result:
        response = {'message': 'Transaction will be added to Block '}
        return jsonify(response), 201
    else:
        response = {'message': 'Invalid Transaction!'}
        return jsonify(response), 406

@app.route('/get_transactions', methods=['GET'])
def get_transactions():
    # Get transactions from transactions pool
    transactions = blockchain.unconfirmed_transactions
    response = {'transactions': transactions}
    return jsonify(response), 200

@app.route('/chain', methods=['GET'])
def part_chain():
    response = {
    'chain': blockchain.chain[-10:],
    'length': len(blockchain.chain),
    }
    return jsonify(response), 200

@app.route('/fullchain', methods=['GET'])
def full_chain():
    response = {
    'chain': json.dumps(blockchain.chain),
    'length': len(blockchain.chain),
    }
    return jsonify(response), 200

@app.route('/get_nodes', methods=['GET'])
def get_nodes():
    nodes = list(blockchain.nodes)
    response = {'nodes': nodes}
    return jsonify(response), 200

@app.route('/register_node', methods=['POST'])
def register_node():
    values = request.form
    node = values.get('node')
    com_port = values.get('com_port')
    # handle type B request
    if com_port is not None:
        blockchain.register_node(request.remote_addr + ":" + com_port)
        return "ok", 200
    # handle type A request
    if node is None and com_port is None:
        return "Error: Please supply a valid nodes", 400
    blockchain.register_node(node)
    # retrieve nodes list
    node_list = requests.get('http://' + node + '/get_nodes')
    if node_list.status_code == 200:
        node_list = node_list.json()['nodes']
        for node in node_list:
            blockchain.register_node(node)
    for new_nodes in blockchain.nodes:
        # sending type B request
        requests.post('http://' + new_nodes + '/register_node',
                      data={'com_port': str(port)})
    # check if our chain is authoritative from other nodes
    replaced = blockchain.consensus()
    if replaced:
        response = {
        'message': 'Longer authoritative chain found from peers, replacing ours',
        'total_nodes': [node for node in blockchain.nodes]
        }
    else:
        response = {
        'message': 'New nodes have been added, but our chain is authoritative',
        'total_nodes': [node for node in blockchain.nodes]
        }
    return jsonify(response), 201

@app.route('/consensus', methods=['GET'])
def consensus():
    replaced = blockchain.consensus()
    if replaced:
        response = {
            'message': 'Our chain was replaced',
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
        }
    return jsonify(response), 200

@app.route('/mine', methods=['GET'])
def mine():
    newblock = blockchain.mine(myWallet)
    for node in blockchain.nodes:
        requests.get('http://' + node + '/consensus')
        response = {
        'index': newblock.index,
        'transactions': newblock.transactions,
        'timestamp': newblock.timestamp,
        'nonce': newblock.nonce,
        'hash': newblock.hash,
        'previous_hash': newblock.previous_hash
        }
    return jsonify(response), 200

if __name__ == '__main__':

    if len(sys.argv) < 2:
        print("Port number missing")
        sys.exit(1)

    port = int(sys.argv[1])
    myWallet = Wallet()
    print(myWallet.identity)
    blockchain = Blockchain()
    app.run(host='127.0.0.1', port=port)