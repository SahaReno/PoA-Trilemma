# mempool.py
"""
Mempool and pending queue management.
Provides:
- Mempool class (insert TARecord)
- Query length Q(t)
- Signed Merkle root for mempool (for voting proofs)
"""

from typing import List, Tuple
import heapq
import time
from anchors import merkle_root
from utils import TARecord, debug

class Mempool:
    def __init__(self):
        self._txs: List[TARecord] = []
        # Optionally implement priority queue by fee/time
        self._by_anchor = {}

    def add(self, ta: TARecord):
        self._txs.append(ta)
        self._by_anchor[ta.anchor_hash_hex] = ta

    def snapshot_anchors(self) -> List[str]:
        return [t.anchor_hash_hex for t in self._txs]

    def merkle_root_hex(self) -> str:
        return merkle_root(self.snapshot_anchors())

    def pending_count(self) -> int:
        return len(self._txs)

    def clear_n_first(self, n: int):
        # remove first n txs (simulate inclusion)
        removed = self._txs[:n]
        self._txs = self._txs[n:]
        for r in removed:
            self._by_anchor.pop(r.anchor_hash_hex, None)
        return removed
