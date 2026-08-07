from hashlib import sha256

def hash_leaf(data: bytes) -> bytes:
    return sha256(data).digest()

def hash_node(left: bytes, right: bytes) -> bytes:
    return sha256(left + right).digest()