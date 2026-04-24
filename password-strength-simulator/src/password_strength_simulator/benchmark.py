import time
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor
import math
import os

from typing import Callable, Any

import bcrypt
import argon2
from passlib.hash import pbkdf2_sha256, scrypt

import hashlib

from .hardware import ALGO_BASE_COST, ALGO_COST_TYPE


TARGET_BENCH_TIME = 1.0  # seconds per benchmark


def hash_benchmark_worker(
    algo: str, cost: int, pw: bytes, salt: bytes, bench_time: float
) -> int:
    count = 0
    start = time.perf_counter()
    while time.perf_counter() - start < bench_time:
        _hash_once(algo, cost, pw, salt)
        count += 1
    return count


def _hash_once(algo: str, cost: int, pw: bytes, salt: bytes) -> bytes:
    if algo == "md5":
        return hashlib.md5(pw + salt).digest()
    elif algo == "sha1":
        return hashlib.sha1(pw + salt).digest()
    elif algo == "pbkdf2-sha256":
        return pbkdf2_sha256.hash(pw.decode(), salt=salt.decode(), rounds=cost).encode()
    elif algo == "bcrypt":
        return bcrypt.hashpw(pw, bcrypt.gensalt(rounds=cost))
    elif algo == "scrypt":
        return scrypt.hash(pw.decode(), salt=salt.decode(), N=cost).encode()
    elif algo == "argon2":
        ph = argon2.PasswordHasher(time_cost=cost, memory_cost=65536, parallelism=1)
        return ph.hash(pw.decode()).encode()
    raise ValueError(f"Unsupported algo for bench: {algo}")


def benchmark_algo(
    algo: str,
    cost: int,
    duration: float = TARGET_BENCH_TIME,
    num_processes: int = None,
) -> float:
    """Benchmark H/s on this machine (multi-process). Returns log10(H/s)."""
    if num_processes is None:
        num_processes = mp.cpu_count()

    pw = b"testpassword123!"
    salt = os.urandom(16)

    # Pre-test single to check
    try:
        _hash_once(algo, cost, pw, salt)
    except Exception as e:
        raise RuntimeError(f"Benchmark failed for {algo}: {e}")

    with ProcessPoolExecutor(max_workers=num_processes) as executor:
        futures = [
            executor.submit(hash_benchmark_worker, algo, cost, pw, salt, duration / 2)
            for _ in range(num_processes)
        ]
        counts = [f.result() for f in futures]

    total_hashes = sum(counts)
    total_time = duration
    hps = total_hashes / total_time
    return math.log10(hps)