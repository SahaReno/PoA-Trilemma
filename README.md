# PoA-Trilemma

This repository provides reference Python modules implementing the main algorithms and building blocks used in the manuscript:
**Formal Validation of the Proof-of-Access Architectures for Overcoming the Blockchain Trilemma**.
(See manuscript uploaded to this conversation.)

## Contents
- `utils.py` — helper utilities and datatypes
- `anchors.py` — Transaction Anchor (TA) generation and Merkle AnchorChain utilities
- `mempool.py` — mempool and pending queue functions
- `dynamic_block.py` — dynamic block sizing controller with EMA and Lyapunov drift estimator
- `vdf_vrf.py` — VRF + (simulated) VDF helpers (toy implementations)
- `erasure_coding.py` — Reed–Solomon wrapper and fragmentation helpers (demo)
- `poa_consensus.py` — simplified PoA proposer/validator logic and chain-quality metric
- `simulator.py` — a small simulator to exercise the system and compute Q(alpha)
- `requirements.txt` — recommended packages

## Requirements
Python 3.9+ recommended.

Install dependencies:
```bash
pip install -r requirements.txt
