import pytest
from lease_guard.lease import LeaseClient, Lease

def test_acquire_and_validate():
    c = LeaseClient()
    l = c.acquire("k1", ttl=10)
    assert c.validate(l)

def test_double_release():
    c = LeaseClient()
    l = c.acquire("k2")
    l.release()
    with pytest.raises(RuntimeError):
        l.release()

def test_fencing_token_unique():
    c = LeaseClient()
    l1 = c.acquire("k3")
    l2 = c.acquire("k3")
    assert l1.token != l2.token