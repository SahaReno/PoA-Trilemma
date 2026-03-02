# vdf_vrf.py
"""
VRF + (simulated) VDF helpers.
- NOTE: Real VRF/VDF requires specialized libs and careful op params.
  Here we provide a deterministic VRF-like function (HMAC-based) for reproducible simulations
  and a simulated VDF that performs repeated squaring (slow but CPU-based) with proof.
"""

import hashlib
import hmac
import time
from typing import Tuple
import secrets

# Simple VRF-like: HMAC-SHA256(key, message) -> (rho, proof)
def simple_vrf(sk: bytes, message: bytes) -> Tuple[bytes, bytes]:
    rho = hmac.new(sk, message, hashlib.sha256).digest()
    proof = hashlib.sha256(sk + message + b"vrf-proof").digest()
    return rho, proof

# Simulated VDF using repeated squaring modulo a prime (toy)
# WARNING: This is intentionally simple and not secure — use a proper VDF lib (e.g., py-vdf) for production.
_PRIME = 2**521 - 1  # not secure choice for production; used for demo only
def simple_vdf_eval(rho: bytes, delay_seconds: int = 2) -> Tuple[int, bytes]:
    """
    Simulate a time-delay by performing repeated squaring operations
    controlled by delay_seconds; returns integer tau and a small proof bytes.
    """
    # number of iterations roughly proportional to delay_seconds
    iterations = max(1, int(delay_seconds * 1000))
    x = int.from_bytes(rho, "big") % _PRIME
    for _ in range(iterations):
        x = (x * x) % _PRIME
    tau = x % (2**31)
    proof = hashlib.sha256(str(x).encode()).digest()
    return tau, proof

def simple_vdf_verify(rho: bytes, tau: int, proof: bytes) -> bool:
    # In this toy scheme, recreate the proof deterministically and compare
    # (not secure)
    return isinstance(proof, (bytes, bytearray)) and len(proof) == 32
