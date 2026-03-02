# poa_consensus.py
"""
Simplified Proof-of-Access consensus module.
Implements proposer selection (VRF), VDF delay, block creation and validation.
Also includes chain-quality metric Q(alpha) over sliding windows.
"""

from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, field
import time
import random
from vdf_vrf import simple_vrf, simple_vdf_eval, simple_vdf_verify
from anchors import merkle_root
from utils import sha384_hex, now_ts, debug
from mempool import Mempool

@dataclass
class BlockHeader:
    prev_hash: str
    merkle_root: str
    timestamp: int
    Lt_mb: float
    rho_hex: str
    tau_int: int
    vdf_proof_hex: str
    nonce: int = 0

@dataclass
class Block:
    header: BlockHeader
    tx_anchors: List[str] = field(default_factory=list)
    miner_id: str = ""

    def hash_hex(self) -> str:
        payload = (self.header.prev_hash + self.header.merkle_root + str(self.header.timestamp) + str(self.header.nonce)).encode()
        return sha384_hex(payload)

class PoANode:
    def __init__(self, node_id: str, stake: float = 1.0):
        self.node_id = node_id
        self.sk = secrets.token_bytes(32)
        self.stake = stake

    def propose_block(self, prev_hash: str, mempool: Mempool, Lt_mb: float) -> Block:
        # VRF
        rho, proof_vrf = simple_vrf(self.sk, (prev_hash + str(now_ts())).encode())
        tau, proof_vdf = simple_vdf_eval(rho, delay_seconds=0.05)
        anchor_list = mempool.snapshot_anchors()
        merkle = merkle_root(anchor_list[:int(max(1, min(len(anchor_list), Lt_mb * 1000)))])
        header = BlockHeader(prev_hash=prev_hash, merkle_root=merkle, timestamp=now_ts(), Lt_mb=Lt_mb, rho_hex=rho.hex(), tau_int=tau, vdf_proof_hex=proof_vdf.hex(), nonce=random.getrandbits(32))
        block = Block(header=header, tx_anchors=anchor_list[:int(max(1, min(len(anchor_list), int(Lt_mb * 1000))))], miner_id=self.node_id)
        return block

    def validate_block(self, block: Block, history: List[str]) -> bool:
        # Validate VDF + derive Bold usage (toy)
        try:
            # verify vdf (toy)
            if not simple_vdf_verify(bytes.fromhex(block.header.rho_hex), block.header.tau_int, bytes.fromhex(block.header.vdf_proof_hex)):
                return False
            # recompute merkle root match
            # in real network you'd fetch the anchorchain membership proofs
            return True
        except Exception as e:
            debug("validation error", e)
            return False

# Chain quality metric Q(alpha)
def compute_chain_quality(chain: List[Block], honest_miners: set, window: int = 100) -> float:
    if len(chain) < window:
        window = len(chain)
    if window == 0:
        return 1.0
    min_ratio = 1.0
    for i in range(0, len(chain) - window + 1):
        window_blocks = chain[i:i+window]
        honest_count = sum(1 for b in window_blocks if b.miner_id in honest_miners)
        ratio = honest_count / window
        if ratio < min_ratio:
            min_ratio = ratio
    return min_ratio
