class Config:
    # The mining reward could decrease over time like bitcoin
    MINING_REWARD = 5_000_000_000

    # Usually it's a fee over transaction size (not quantity)
    FEE_PER_TRANSACTION = 1

    # Usually the limit is determined by block size (not quantity)
    TRANSACTIONS_PER_BLOCK = 2

    TEST_MINER_1 = {'id': '912c953c25ce493dad7ace6fec066e28',
                    'public_key': '30819f300d06092a864886f70d010101050003818d0030818902818100b348736807b33cb9c56337db8d2f87be052970eb27178b69512f5cd7a38d0bc9bfc1b92dbc51b2f551b68c9deb51cf12336438fd444ba9d61aa1b07340db32b745c71d25dc9deaed7934c2045f97cdc998af11d42d033fdbff79065b01305e2c15331e9f40942246217fc2c230739faca85ad2ff29d9c3e037fa64c194a3ac590203010001',
                    'private_key': '3082025b02010002818100b348736807b33cb9c56337db8d2f87be052970eb27178b69512f5cd7a38d0bc9bfc1b92dbc51b2f551b68c9deb51cf12336438fd444ba9d61aa1b07340db32b745c71d25dc9deaed7934c2045f97cdc998af11d42d033fdbff79065b01305e2c15331e9f40942246217fc2c230739faca85ad2ff29d9c3e037fa64c194a3ac5902030100010281802437cd34a56594ad74ce4bf0fb0f308d772e7d84cbd36a52fed7221ae00bf4e72f695bd6fcf5c640dfde907eb094c8cfc4f908b8456d41a4a2a1aa6b461d621ba47d2213786f5526e18717e083a0cafd244c4ddf20acc4550e4c9889e86ba094973da3dd367ccf7112bc551a6f563c20ffd84ad36209a1f83378408eff9af799024100cb7cb3547c4b2dbe68d3d29cbf57ab1342dd5442889575ac4d4bd7058cff3d84c039ee5c0dc3362095d752ed5f5af256cdafda7eb4d18fcb5e8e6ac3b6f66a6d024100e18cb72b7b6faa020bce61145ae54fd09df9111a22808baf951027a84565dddf4dbcbb74c27e0ca4a850db70eb084f4cab87d07df72764742fdfd184333d561d02400728f21e6ce93048dce3672bc0c7d2eb30951d1be236701789f8bb2e24d1ee563775525fc6d431995fec5daca08850b2a13628d80080c7307eb9402476d1a0d902407f79b84cab07015f06ad2dd1034e773dc10af3cf81908562472d4a3ca07c6259c2e5d84cb55fe865677bcb8a964bac05f92c5979d8263b702f5ea05bc759f3410240068f66c5df9190664450840c549e9adf6169e87cf336d77e95e1c372df1a7189bfb0bb038f402df7631cf291b6c2cdc59b9277def9538e07ba3087c985054fe2'}

    GENESIS_BLOCK = {
        'index': 0,
        'previous_hash': 0,
        'nonce': 0,
        'timestamp': 1575888715.074447,
        'hash': '22ad7015332d64bf0b4508c05d4d0079ad0d0ad01c2ff0843bba0a579d7a976e',
        'transactions': [
            {
                'id': 'a2d285a55bc6458a9eed8c2b4a8cdcfe',
                'type': 'regular',
                'inputs': [],
                'outputs': [
                    {
                        'address': TEST_MINER_1['public_key'],
                        'amount': 50
                    }
                ],
                'hash': 'f0c5ec50513fe3c2862d8ae35894ba3f8829a0b9ffce326e3ea1d52d982389d3',
            }
        ]
    }

    SERVER_HOST = '127.0.0.1'
    REDIS_URL_BASE = 'redis://localhost:'
    REDIS_PORT = 6380

    @staticmethod
    def redis_url():
        return Config.REDIS_URL_BASE + str(Config.REDIS_PORT)
