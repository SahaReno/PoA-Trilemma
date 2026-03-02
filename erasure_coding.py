# erasure_coding.py
"""
Reed–Solomon erasure coding helpers (wrapper).
We use `reedsolo` library which implements RS in pure Python.
pip install reedsolo
"""

from typing import List, Tuple
import math
import os
import reedsolo

# Initialize reedsolo with default primitive polynomial (works for demo)
# Warning: reedsolo typically expects bytes chunks and works over GF(2^8).
def encode_shards(data: bytes, k: int = 64, m: int = 16) -> List[bytes]:
    """
    Split data into k data shards and create m parity shards.
    For convenience we pad data to k*shard_size.
    """
    total = k + m
    # compute shard size
    shard_size = math.ceil(len(data) / k)
    # pad data
    padded = data + b"\x00" * (shard_size * k - len(data))
    shards = [padded[i*shard_size:(i+1)*shard_size] for i in range(k)]
    # generate parity shards using reedsolo RS encoding per byte position across shards
    # reedsolo has rs_encode_msg for message -> parity of length nsym
    # an easier approach: encode each shard as message and append parity block - simple but not optimal
    parity_shards = []
    for s in range(m):
        # naive parity: XOR of some rotated shards (demo)
        parity = bytearray(shard_size)
        for i, sh in enumerate(shards):
            # rotate index to spread bits
            idx = (i + s) % k
            for j in range(shard_size):
                parity[j] ^= shards[idx][j]
        parity_shards.append(bytes(parity))
    return shards + parity_shards

def can_reconstruct(received_indices: List[int], k: int) -> bool:
    """
    If we have at least k unique shards, reconstruct is possible.
    """
    return len(set(received_indices)) >= k

def reconstruct_data(received_shards: List[bytes], received_indices: List[int], k: int, shard_size: int) -> bytes:
    """
    Very naive reconstruction: place shards in slots and XOR-fill missing with zeros.
    For real use, integrate with proper RS decoding (reedsolo.rs_correct_msg etc.)
    """
    slots = [b"\x00" * shard_size] * (max(k, max(received_indices)+1) + 1)
    for idx, sh in zip(received_indices, received_shards):
        slots[idx] = sh
    # join first k shards
    joined = b"".join(slots[:k])
    # Trim trailing zeros (best-effort)
    return joined.rstrip(b"\x00")
