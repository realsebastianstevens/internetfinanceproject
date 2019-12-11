import binascii
import json
import re
import uuid
from typing import Tuple

import Crypto
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

VALID_URL_RE = re.compile(
    r'^(?:http|ftp)s?://'  # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)


def random_id() -> str:
    return uuid.uuid4().hex


def sign_hash(secret: RSA.RsaKey, hash_: SHA256) -> str:
    signer = PKCS1_v1_5.new(secret)
    return binascii.hexlify(signer.sign(hash_)).decode('utf8')


def crypto_hash(dict_object: dict) -> SHA256.SHA256Hash:
    h = SHA256.new()
    h.update(json.dumps(dict_object).encode('utf8'))
    return h


def hash_str(string: str) -> SHA256.SHA256Hash:
    h = SHA256.new()
    h.update(string.encode('utf8'))
    return h


def verify_hash(public_key: str, h: SHA256.SHA256Hash, calculated_signature: bytes):
    public_key = RSA.import_key(binascii.unhexlify(public_key))
    verifier = PKCS1_v1_5.new(public_key)
    return verifier.verify(h, binascii.unhexlify(calculated_signature))


def verify(public_key: str, dict_object: dict, calculated_signature: bytes):
    public_key = RSA.import_key(binascii.unhexlify(public_key))
    verifier = PKCS1_v1_5.new(public_key)
    h = crypto_hash(dict_object)
    return verifier.verify(h, binascii.unhexlify(calculated_signature))


def generate_public_private_key_pair() -> Tuple[RSA.RsaKey, RSA.RsaKey]:
    random = Crypto.Random.new().read
    private = RSA.generate(1024, random)
    public = private.publickey()
    return public, private


def is_url_valid(url) -> bool:
    return re.match(VALID_URL_RE, url) is not None


def bin2hex(bin_str: str) -> bytes:
    return binascii.hexlify(bin_str)


def hex2bin(hex_str: bytes) -> str:
    return binascii.unhexlify(hex_str)


def import_rsa_key(bin_str: str) -> RSA.RsaKey:
    return RSA.import_key(binascii.unhexlify(bin_str.encode()))


# def dictionaries_equal(a: dict, b: dict) -> bool:
#     if not (len(a.keys()) == len(b.keys()) == len(set(a.keys()).intersection(set(b.keys())))):
#        return False
#     for k in a.keys():
#         aa = a[k]
#         bb = b[k]
#         if type(aa) != type(bb):
#             return False
#         if isinstance(aa, dict) or isinstance(aa, OrderedDict):
#             if not dictionaries_equal(aa, bb):
#                 return False
#         # if isinstance(aa, Iterable):


