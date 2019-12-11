import datetime
from functools import reduce
from typing import Union, List

from coin.config import Config
from coin.database import Database
from coin.domain import Transaction, Block, InputInfo


class Blockchain:

    def __init__(self, database=None):
        self.database = database or Database()
        if len(self.chain) == 0:
            self.create_genesis_block()

    @property
    def difficulty(self) -> int:
        return 2

    @property
    def last_block(self) -> Union[Block, None]:
        if len(self.chain) > 0:
            return self.chain[-1]
        return None

    @property
    def chain(self) -> List[Block]:
        return self.database.get_blocks()

    @property
    def length(self) -> int:
        return len(self.chain)

    @chain.setter
    def chain(self, value: List[Block]):
        self.database.replace_blocks(value)

    @property
    def confirmed_transactions(self) -> List[Transaction]:
        return self.database.get_transactions()

    @property
    def unconfirmed_transactions(self) -> List[Transaction]:
        return self.database.get_unconfirmed_transactions()

    @property
    def full_chain(self) -> dict:
        return {
            'chain': [x.to_json() for x in self.chain],
            'length': len(self.chain)
        }

    def part_chain(self, max_size=10):
        chain = [x.to_json() for x in self.chain[-max_size:]]
        return {
            'chain': chain,
            'length': len(chain)
        }

    @property
    def genesis(self) -> Block:
        genesis_block = Block.from_json(Config.GENESIS_BLOCK)
        genesis_block.hash = genesis_block.compute_hash()
        return genesis_block

    def create_genesis_block(self):
        self.database.add_block(self.genesis)

    def add_new_transaction(self, transaction: Transaction) -> bool:
        if transaction.check():
            self.database.add_unconfirmed_transaction(transaction)
            return True
        return False

    def add_block(self, block: Block, proof: str) -> Union[Block, None]:
        if self.check_block(block, proof):
            block.hash = proof
            self.database.add_block(block)
            self.database.remove_transactions_from_unconfirmed_list(block.transactions)
            return block
        return None

    def check_block(self, block: Block, proof: str) -> bool:
        previous_hash = self.last_block.hash if self.last_block else None
        if previous_hash and previous_hash != block.previous_hash:
            print("Hashes don't match")
            return False
        if not self.is_valid_proof(block, proof):
            print("Proof is not valid")
            return False
        # check transactions
        if not all([self.check_transaction(tx) for tx in block.transactions]):
            print("Transactions matter")
            return False

        # Check if there is only 1 fee transaction and 1 reward transaction
        tx_rewards = [x for x in block.transactions if x.type == Transaction.REWARD]
        tx_fees = [x for x in block.transactions if x.type == Transaction.FEE]
        if len(tx_fees) > 1:
            print(f"Invalid fee transaction count: Expected '1' Got {len(tx_fees)}")
            return False
        if len(tx_rewards) > 1:
            print(f"Invalid fee transaction count: Expected '1' Got {len(tx_rewards)}")
            return False
        return True

    @staticmethod
    def datetime_now() -> str:
        return datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")

    def is_valid_proof(self, block: Block, block_hash: str) -> bool:
        return block_hash.startswith('0' * self.difficulty) and block_hash == block.compute_hash()

    def replace_chain(self, new_chain):
        self.chain = new_chain

    def valid_chain(self, chain: List[dict]) -> bool:
        # check if a blockchain is valid
        first_block = Block.from_json(chain[0])
        if first_block.hash != self.genesis.compute_hash():
            return False

        current_index = 1
        while current_index < len(chain):
            current_block = Block.from_json(chain[current_index])
            if current_block.compute_hash() != current_block.hash:
                return False

            # check if newBlock's previous_hash field is same as currentBlock's hash
            if current_index + 1 < len(chain):
                new_block = Block.from_json(chain[current_index + 1])
                if current_block.compute_hash() != new_block.previous_hash:
                    print("Uneven hashes")
                    return False

            # validate each transaction
            for transaction in current_block.transactions:
                if transaction.type == Transaction.REGULAR:
                    if not transaction.check():
                        print("Bad transaction")
                        return False
            if not self.is_valid_proof(current_block, current_block.hash):
                print("Is not valid proof")
                return False
            current_index += 1
        return True

    @property
    def all_inputs(self) -> List[InputInfo]:
        return reduce(lambda x, y: x + y, map(lambda x: x.inputs, self.confirmed_transactions))

    def check_transaction(self, tx: Transaction) -> bool:
        if not tx.check():
            print("Yup")
            return False

        # verify if the transaction isn't already in the blockchain
        if any([tx.hash == x.hash or tx.id == x.id for x in self.confirmed_transactions]):
            raise Exception(f"Transaction '{tx.hash}'already in the blockchain")

        # verify all inputs exists in database
        for input_ in tx.inputs:
            if not any([x.hash == input_.tx_hash and input_.index in range(len(x.outputs)) and x.outputs[
                input_.index].amount == input_.amount for x in
                        self.confirmed_transactions]):
                print("Input references transaction that is not in database")
                return False

        # verify all inputs are unspent
        for input_ in tx.inputs:
            if any([x.index == input_.index and x.tx_hash == input_.tx_hash for x in self.all_inputs]):
                print(f"Not all inputs are unspent for transaction `{tx.hash}`")
                return False
        return True

    def get_unspent_transactions_for_address(self, address):
        outputs: List[InputInfo] = []
        inputs: List[InputInfo] = []

        def prepare(transactions: List[Transaction]):
            for tx in transactions:
                for idx, output in enumerate(tx.outputs):
                    if output.address == address:
                        outputs.append(InputInfo(tx.hash, idx, output.amount, address, None))
                for idx, input_ in enumerate(tx.inputs):
                    if address == input_.address:
                        inputs.append(input_)

        prepare(self.confirmed_transactions)
        prepare(self.unconfirmed_transactions)

        unspent = []
        for output in outputs:
            if not any([x.tx_hash == output.tx_hash and x.index == output.index for x in inputs]):
                unspent.append(output.to_json())
        return unspent

    def get_balance_for_address(self, address) -> int:
        utxos = self.get_unspent_transactions_for_address(address)
        return sum([x['amount'] for x in utxos])
