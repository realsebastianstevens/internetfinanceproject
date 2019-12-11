from threading import Timer
from typing import Set

import requests
from flask import url_for

from coin.blockchain import Blockchain
from coin.config import Config
from coin.domain import Block


class Node:
    def __init__(self, port: str, blockchain: Blockchain, peers: Set[str] = None):
        self.port = port
        self.blockchain = blockchain
        self.peers = set()
        self.initial_connect_to_peers(peers)

    def initial_connect_to_peers(self, peers):
        def foo():
            self.connect_to_peers(peers)

        self._t = Timer(3, foo)
        self._t.start()

    def connect_to_peers(self, peers: Set[str]):
        me = 'http://' + Config.SERVER_HOST + ':' + self.port
        for peer in peers:
            if len(self.peers.intersection({peer})) == 0:
                self.peers.add(peer)
                self.send_to_peer(peer, me)

        self.consensus()

    def connect_to_peer(self, peer):
        return self.connect_to_peers({peer})

    def send_to_peer(self, peer, peer_to_send):
        print(peer_to_send)
        r = requests.post(peer + '/node/peers/', data={'url': peer_to_send})
        if r.status_code not in [200, 201]:
            print("Unable to connect to peer")
        else:
            print("Success!")

    def consensus_requests(self):
        for peer in self.peers:
            requests.get(peer + url_for('consensus'))

    def consensus(self):
        neighbours = self.peers
        new_chain = None
        max_length = self.blockchain.length

        # We're only looking for chains longer than ours
        # Grab and verify the chains from all the nodes in our network
        for node in neighbours:
            response = requests.get(node + '/blockchain/blocks/')
            if response.status_code == 200:
                data = response.json()
                length = data['length']
                chain = data['chain']
                # Check if the length is longer and the chain is valid
                if length > max_length:
                    if self.blockchain.valid_chain(chain):
                        max_length = length
                        new_chain = chain
                    else:
                        print(f"Bigger length found {length} but chain not valid")
            else:
                print(response.text, response.url)
        # Replace our chain if longer chain is found
        if new_chain:
            self.blockchain.replace_chain([Block.from_json(block) for block in new_chain])
            return True
        return False
