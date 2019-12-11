from typing import Union, List

from coin.domain import Wallet, Block, Transaction


class Database:

    def __init__(self):
        self.unconfirmed_transactions = []
        self.blocks = []
        self.wallets = []

    def add_wallet(self, wallet: Wallet):
        pass

    def get_wallet_by_id(self, wallet_id) -> Union[Wallet, None]:
        pass

    def get_blocks(self) -> List[Block]:
        return self.blocks

    def replace_blocks(self, new_blocks):
        self.blocks = new_blocks

    def add_block(self, block: Block):
        self.blocks.append(block)

    def get_transactions(self) -> List[Transaction]:
        transactions = []
        for block in self.blocks:
            transactions += block.transactions
        return transactions

    def add_unconfirmed_transaction(self, transaction: Transaction):
        self.unconfirmed_transactions.append(transaction)

    def get_unconfirmed_transactions(self) -> List[Transaction]:
        return self.unconfirmed_transactions

    def remove_transactions_from_unconfirmed_list(self, transactions: List[Transaction]):
        for tx in transactions:
            if tx.type == tx.REGULAR:
                self.unconfirmed_transactions.remove(tx)
