import pytest
from x509_chain_checker.validator import Validator
from x509_chain_checker.root_stores import find_anchors


def test_good_chain(good_chain, root_cert):
    validator = Validator("server")
    roots = [root_cert]
    report = validator.validate(good_chain, roots)
    assert report.overall_status == "valid"
    assert len(report.chain) == 3
    assert all(c.status == "valid" for c in report.chain)


def test_build_chain(good_chain, leaf_cert):
    validator = Validator()
    pool = good_chain[1:]  # inter + root
    built = validator.build_chain(leaf_cert, pool)
    assert len(built) == 3
    assert built[0].subject_cn == "leaf.example.com"  # Approx


def test_expired_leaf(expired_leaf, inter_cert, root_cert):
    validator = Validator()
    chain = [expired_leaf, inter_cert, root_cert]
    report = validator.validate(chain, [root_cert])
    assert report.overall_status == "invalid"
    assert "expired" in [iss.value for c in report.chain for iss in c.issues]


def test_wrong_purpose(leaf_cert, inter_cert, root_cert):
    validator = Validator("client")
    chain = [leaf_cert, inter_cert, root_cert]
    report = validator.validate(chain, [root_cert])
    assert "wrong_purpose" in [iss.value for c in report.chain for iss in c.issues]


def test_self_signed_not_root(root_cert):
    # Leaf self-signed
    leaf_self = root_cert  # Reuse
    validator = Validator()
    report = validator.validate([leaf_self], [])
    assert "self_signed_not_root" in [iss.value for c in report.chain for iss in c.issues]