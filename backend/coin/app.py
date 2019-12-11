import argparse

import rq
from flask import Flask, jsonify, request

from coin import tasks
from coin.blockchain import Blockchain
from coin.config import Config
from coin.domain import Wallet
from coin.miner import Miner
from coin.node import Node
from coin.transactionbuilder import NewTransactionViewModel
from worker import conn

app = Flask(__name__)

app.redis = conn
app.task_queue = rq.Queue(connection=app.redis)


@app.route('/blockchain/transactions/', methods=['POST'])
def new_transaction():
    values = request.json
    required = ['transaction']
    if values is None or not all(k in values for k in required):
        return f'One or more missing values: {required}', 400
    try:
        tx = NewTransactionViewModel.from_json_request(values['transaction']).build()
    except Exception as e:
        return str(e), 400
    is_added = blockchain.add_new_transaction(tx)
    if is_added:
        tasks.launch_task(tasks.mine_and_consensus, 'mine blockchain', peer=f'http://{Config.SERVER_HOST}:{port}')
        response = {'message': 'Transaction will be added to Block '}
        return jsonify(response), 201
    else:
        response = {'message': 'Invalid Transaction!'}
        return jsonify(response), 406


@app.route('/blockchain/transactions/', methods=['GET'])
def get_transactions():
    # Get transactions from transactions pool
    transactions = blockchain.unconfirmed_transactions
    response = {'transactions': transactions}
    return jsonify(response), 200


@app.route('/blockchain/blocks/tail/', methods=['GET'])
def part_chain():
    return jsonify(blockchain.part_chain()), 200


@app.route('/blockchain/blocks/', methods=['GET'])
def full_chain():
    return jsonify(blockchain.full_chain), 200


@app.route('/node/peers/', methods=['GET'])
def get_nodes():
    nodes = list(node.peers)
    response = {'nodes': nodes}
    return jsonify(response), 200


@app.route('/node/peers/', methods=['POST'])
def register_node():
    values = request.form
    url = values.get('url')
    node.connect_to_peer(url)
    response = {
        'message': 'New node added',
        'length': blockchain.length
    }
    return jsonify(response), 201


@app.route('/node/consensus/', methods=['GET'])
def consensus():
    replaced = node.consensus()
    if replaced:
        response = {
            'message': 'Our chain was replaced',
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
        }
    return jsonify(response), 200


@app.route('/miner/mine/', methods=['GET'])
def mine():
    newblock = miner.mine(myWallet.identity, myWallet.identity)
    if newblock:
        tasks.launch_task(tasks.consensus_requests, 'synchronize blockchain', peers=node.peers)
        return jsonify(newblock.to_json()), 200
    return "Error occurred during mining", 400


@app.route('/wallet/<address>/utxos/')
def get_utxos(address):
    return jsonify(blockchain.get_unspent_transactions_for_address(address)), 200


@app.route('/wallet/<address>/balance/')
def get_balance(address):
    return jsonify({'balance': blockchain.get_balance_for_address(address)}), 200


@app.route('/wallet/new/')
def generate_wallet():
    return jsonify(Wallet.generate().to_json()), 200


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', type=int, help='Port number e.g. 3000')
    parser.add_argument('--peers', type=str, nargs='*', help='Peers e.g http://localhost:5000/')
    parser.add_argument('--use_test_miner', action='store_true')
    args = parser.parse_args()

    port = str(args.port)
    peers = set(args.peers) if args.peers else set()
    use_test_miner = args.use_test_miner

    myWallet = Wallet.from_json(Config.TEST_WALLET_1) if use_test_miner else Wallet.generate()
    print(myWallet.identity)
    print(myWallet.identity_private)
    blockchain = Blockchain()
    node = Node(port, blockchain, peers)
    miner = Miner(blockchain)

    app.blockchain = blockchain
    app.node = node
    app.miner = miner
    app.wallet = myWallet
    app.run(host=Config.SERVER_HOST, port=port)
