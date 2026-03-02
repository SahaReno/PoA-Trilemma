# simulator.py
"""
A small simulator that ties mempool, nodes, dynamic block sizing, and PoA consensus together.
Run small experiments and calculate Q(alpha).
"""

import random
from typing import List, Tuple
from mempool import Mempool
from poa_consensus import PoANode, compute_chain_quality, Block
from dynamic_block import DynamicBlockController
from anchors import create_transaction_anchor
from utils import random_hex, TARecord, debug
import time

def make_random_ta(sender: str, receiver: str, sk_hex: str, ref_block: str) -> TARecord:
    payload = ("payload-" + random_hex(8)).encode()
    return create_transaction_anchor(payload, sender, receiver, sk_hex, ref_block, payload_pointer="arweave://dummy")

def setup_nodes(n_total: int, n_byzantine: int) -> Tuple[List[PoANode], set]:
    nodes = []
    for i in range(n_total):
        node = PoANode(node_id=f"node-{i}", stake=1.0)
        nodes.append(node)
    honest_ids = set(n.node_id for n in nodes[:n_total - n_byzantine])
    return nodes, honest_ids

def run_simple_simulation(num_epochs: int = 200, n_nodes: int = 50, byzantine: int = 20):
    mempool = Mempool()
    nodes, honest_set = setup_nodes(n_nodes, byzantine)
    db_ctrl = DynamicBlockController()
    chain: List[Block] = []
    # stub keys for TA generation (we use node 0's key)
    sk_hex = nodes[0].sk.hex()

    # warm-up: fill mempool
    for _ in range(2000):
        ta = make_random_ta("alice", "bob", sk_hex, ref_block="genesis")
        mempool.add(ta)

    prev_hash = "genesis"
    for epoch in range(num_epochs):
        # arrivals (random)
        arrivals = random.randint(50, 2000)
        # add them
        for _ in range(arrivals):
            mempool.add(make_random_ta("alice", "bob", sk_hex, ref_block=prev_hash))
        confirmed = random.randint(100, 1000)
        # dynamic block update
        Lt = db_ctrl.update(arrivals=arrivals, confirmed=confirmed, network_capacity=1000)
        # pick proposer by simple weighted stake (random)
        proposer = random.choice(nodes)
        block = proposer.propose_block(prev_hash, mempool, Lt)
        # simple validation by random honest node
        validator = random.choice(nodes)
        valid = validator.validate_block(block, [b.hash_hex() for b in chain])
        if valid:
            chain.append(block)
            # remove included txs from mempool
            mempool.clear_n_first(len(block.tx_anchors))
            prev_hash = block.hash_hex()
        # periodically compute Q
        if (epoch + 1) % 50 == 0:
            q = compute_chain_quality(chain, honest_set, window=100)
            debug(f"epoch {epoch+1} chain len {len(chain)} Q={q:.3f} Lt={Lt:.2f} pending={mempool.pending_count()}")
    return chain

if __name__ == "__main__":
    chain = run_simple_simulation(num_epochs=300, n_nodes=200, byzantine=80)
    print("Simulation finished. chain length:", len(chain))
