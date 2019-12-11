import datetime
from functools import reduce, partial
from typing import List, Union

from coin import util
from coin.blockchain import Blockchain
from coin.config import Config
from coin.domain import Transaction, InputInfo, Block

"""
The Miner gets the list of pending transactions and create a new block containing the transactions.
By configuration, every block has at most 2 transactions in it.

Assembling a new block:
    1.  From the list of unconfirmed transaction, select candidate transactions that are not already in the 
        blockchain or not already selected.
    2.  Get the first two transaction from the candidate list of transactions
    3.  Add a new transaction containing the fee value to the miner's address, 1 satoshi per transactions;
    4.  Add a reward transaction containing 50 coins to the miner's address.
    5.  Prove work of this block.
"""


class Miner:
    def __init__(self, blockchain: Blockchain):
        self.blockchain = blockchain

    def proof_of_work(self, block: Block):
        block.nonce = 0
        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0' * self.blockchain.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()
        return computed_hash

    def mine(self, reward_address, fee_address) -> Union[Block, None]:
        new_block = self.generate_block(reward_address, fee_address)
        if new_block:
            proof = self.proof_of_work(new_block)
            return self.blockchain.add_block(new_block, proof)
        else:
            print("No block generated")
        return None

    def generate_block(self, reward_address, fee_address) -> Block:
        previous_hash = self.blockchain.last_block.hash
        index = self.blockchain.last_block.index
        candidate_transactions = self.blockchain.unconfirmed_transactions
        selected = []
        rejected = []

        # ===========================================
        def transactions_to_inputs(transactions) -> List[InputInfo]:
            def mapper(x: Transaction) -> List[InputInfo]:
                return x.inputs

            def reducer(x: List[InputInfo], y: List[InputInfo]) -> List[InputInfo]:
                return x + y

            return reduce(reducer, map(mapper, transactions), [])

        def input_equals(a: InputInfo, b: InputInfo):
            return a.tx_hash == b.tx_hash and a.index == b.index

        def find_input_in_transaction_list(transactions, input_info):
            inputs = transactions_to_inputs(transactions)
            return any([input_equals(x, input_info) for x in inputs])

        def transaction_input_found_anywhere(transaction):
            # Check if transaction is attempting to reuse inputs (double spending)
            is_already_spent = partial(find_input_in_transaction_list, selected)
            if any([is_already_spent(x) for x in transaction.inputs]):
                print("Transactions has some inputs already spent")
                return False

            # Check if transaction already mined
            is_in_blockchain = partial(find_input_in_transaction_list, self.blockchain.confirmed_transactions)
            if any([is_in_blockchain(x) for x in transaction.inputs]):
                print("Transactions has some inputs already in blockchain")
                return False

        # ==================================================

        for tx in candidate_transactions:
            all_positive_utxos = all([output.amount >= 0 for output in tx.outputs])
            if not transaction_input_found_anywhere(tx):
                if tx.type == Transaction.REGULAR and all_positive_utxos:
                    selected.append(tx)
                # if negative output found
                elif tx.type == Transaction.REWARD:
                    selected.append(tx)
                elif all_positive_utxos:
                    rejected.append(tx)
            else:
                rejected.append(tx)
        print(f"Rejected: {len(rejected)} txs {[x.id for x in rejected]}")
        transactions_to_mine = selected[:Config.TRANSACTIONS_PER_BLOCK]
        # Add fee transaction (1 satoshi per transaction)
        if len(transactions_to_mine) > 0:
            fee_tx = Transaction.from_json({
                'id': util.random_id(),
                'hash': None,
                'type': Transaction.FEE,
                'inputs': [],
                'outputs': [
                    {
                        'amount': Config.FEE_PER_TRANSACTION * len(transactions_to_mine),  # satoshis format,
                        'address': fee_address
                        # INFO  Usually here is a locking script ( to check who and when this transaction can be used)
                    }
                ]
            }, True)
            transactions_to_mine.append(fee_tx)
        else:
            print("No transaction to mine")

        # Add reward transaction of 50 coins
        if reward_address is not None:
            reward_tx = Transaction.from_json({
                'id': util.random_id(),
                'hash': None,
                'type': Transaction.REWARD,
                'inputs': [],
                'outputs': [
                    {
                        'amount': Config.MINING_REWARD,
                        'address': reward_address
                        # INFO  Usually here is a locking script ( to check who and when this transaction can be used)
                    }
                ]
            }, True)
            transactions_to_mine.append(reward_tx)

        return Block(index, transactions_to_mine, datetime.datetime.now().timestamp(), previous_hash)
