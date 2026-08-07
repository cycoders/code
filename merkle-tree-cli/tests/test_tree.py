import pytest
from merkle_tree_cli.tree import hash_leaf, hash_node

def test_leaf_hash():
    assert len(hash_leaf(b'test')) == 32

def test_node_hash():
    h = hash_node(b'a'*32, b'b'*32)
    assert len(h) == 32