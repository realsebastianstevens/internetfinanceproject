from coin.util import *

if __name__ == '__main__':
    from coin.domain import Wallet

    text = 'hello'
    hashed = hash_str(text)

    w = Wallet.generate()
    key = import_rsa_key(w.identity_private)
    signature = sign_hash(key, hashed)
    print(signature)

    pub = import_rsa_key(w.identity)
    print(verify_hash(w.identity, hashed, signature.encode()))
