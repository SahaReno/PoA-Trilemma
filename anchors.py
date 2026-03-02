# anchors.py
"""
Transaction Anchor generation and Merkle AnchorChain utilities.

- create_transaction_anchor(payload, sender, receiver, sk)
- build_anchorchain_root(list_of_TAhex)
- verify_TA_record(...)
"""

from typing import Tuple, List
from dataclasses import asdict
import base64
import nacl.signing
import nacl.encoding
from utils import sha384_bytes, sha384_hex, TARecord, now_ts, debug

# ---- Key helpers (using PyNaCl) ----
def generate_ed25519_keypair() -> Tuple[str, str]:
    sk = nacl.signing.SigningKey.generate()
    pk = sk.verify_key
    return sk.encode(encoder=nacl.encoding.HexEncoder).decode(), pk.encode(encoder=nacl.encoding.HexEncoder).decode()

def sign_ed25519_hex(sk_hex: str, msg: bytes) -> str:
    sk = nacl.signing.SigningKey(sk_hex, encoder=nacl.encoding.HexEncoder)
    sig = sk.sign(msg).signature
    return base64.b64encode(sig).decode()

def verify_ed25519_hex(pk_hex: str, msg: bytes, signature_b64: str) -> bool:
    vk = nacl.signing.VerifyKey(pk_hex, encoder=nacl.encoding.HexEncoder)
    try:
        sig = base64.b64decode(signature_b64)
        vk.verify(msg, sig)
        return True
    except Exception as e:
        debug("verify failed:", e)
        return False

# ---- Anchor generation ----
def create_transaction_anchor(payload: bytes, sender: str, receiver: str, sk_hex: str, ref_block_hash: str, payload_pointer: str) -> TARecord:
    """
    Compute SHA-384 over payload|sender|receiver|timestamp, sign with Ed25519.
    Returns TARecord dataclass.
    """
    ts = now_ts()
    blob = payload + b"|" + sender.encode() + b"|" + receiver.encode() + b"|" + str(ts).encode()
    anchor_digest = sha384_hex(blob)  # hex string of 48 bytes
    signature_b64 = sign_ed25519_hex(sk_hex, anchor_digest.encode())
    # produce TARecord
    pub_hex = nacl.signing.SigningKey(sk_hex, encoder=nacl.encoding.HexEncoder).verify_key.encode(encoder=nacl.encoding.HexEncoder).decode()
    ta = TARecord(
        anchor_hash_hex=anchor_digest,
        signer_pub_hex=pub_hex,
        signature_b64=signature_b64,
        ref_block_hash=ref_block_hash,
        payload_pointer=payload_pointer,
        ts=ts
    )
    return ta

# ---- Merkle AnchorChain (simple) ----
def merkle_parent(h1: bytes, h2: bytes) -> bytes:
    return sha384_bytes(h1 + h2)

def merkle_root(leaves_hex: List[str]) -> str:
    """
    Compute merkle root using SHA-384 combining hex leaves.
    Leaves should be hex strings (anchor_hex).
    """
    if not leaves_hex:
        return sha384_hex(b"")
    nodes: List[bytes] = [bytes.fromhex(x) for x in leaves_hex]
    while len(nodes) > 1:
        next_nodes = []
        for i in range(0, len(nodes), 2):
            if i+1 < len(nodes):
                next_nodes.append(merkle_parent(nodes[i], nodes[i+1]))
            else:
                # duplicate last for odd count
                next_nodes.append(merkle_parent(nodes[i], nodes[i]))
        nodes = next_nodes
    return nodes[0].hex()
