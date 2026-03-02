# utils.py
"""
Common utilities used by the Blockweave modules.
- crypto wrappers (SHA-384)
- helper dataclasses / types
- config constants
"""

from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional, List
import hashlib
import time
import os
import json
import secrets
import base64

# --------------------
# Config / constants
# --------------------
EPOCH_SECONDS = 600  # 10 minutes as paper
MAX_BLOCK_MB = 200
MIN_BLOCK_MB = 1
ANCHOR_BYTES = 48  # sha384 -> 48 bytes

# --------------------
# Basic helpers
# --------------------
def sha384_bytes(data: bytes) -> bytes:
    """Return raw bytes of SHA-384 digest."""
    h = hashlib.sha384()
    h.update(data)
    return h.digest()

def sha384_hex(data: bytes) -> str:
    return sha384_bytes(data).hex()

def now_ts() -> int:
    return int(time.time())

def random_hex(nbytes: int = 16) -> str:
    return secrets.token_hex(nbytes)

@dataclass
class TARecord:
    """Transaction Anchor record."""
    anchor_hash_hex: str
    signer_pub_hex: str
    signature_b64: str
    ref_block_hash: str
    payload_pointer: str  # URI to Arweave or local storage
    ts: int

    def to_json(self) -> str:
        return json.dumps(asdict(self), sort_keys=True)

# Simple file storage helper for small experiments
def atomic_write(path: str, data: bytes):
    tmp = path + ".tmp"
    with open(tmp, "wb") as f:
        f.write(data)
    os.replace(tmp, path)

# Pretty print for debugging
def debug(*args, **kwargs):
    print("[DEBUG]", *args, **kwargs)
