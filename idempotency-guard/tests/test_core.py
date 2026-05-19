import pytest
from idempotency_guard.core import IdempotencyGuard

def test_new_key_is_not_duplicate():
    guard = IdempotencyGuard()
    assert guard.is_duplicate("new-key") is False

def test_duplicate_within_window():
    guard = IdempotencyGuard()
    guard.store("dup-key", {"ok": True})
    assert guard.is_duplicate("dup-key") is True

def test_ttl_expiration():
    guard = IdempotencyGuard(default_ttl=0)
    guard.store("exp-key", {"ok": True})
    assert guard.is_duplicate("exp-key", window=0) is False