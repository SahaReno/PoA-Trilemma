# dynamic_block.py
"""
Dynamic block sizing mechanism with EMA and simple Lyapunov drift bound
as described in the manuscript.
Exposes DynamicBlockController class.
"""

from typing import Optional
from utils import EPOCH_SECONDS, MAX_BLOCK_MB, MIN_BLOCK_MB
import math
import logging

logger = logging.getLogger("dynamic_block")
logger.setLevel(logging.INFO)

class DynamicBlockController:
    def __init__(self, beta: float = 0.3, decay: float = 0.9, tau_fraction: float = 0.8):
        self.beta = beta
        self.decay = decay
        self.tau_fraction = tau_fraction
        self.Lt = 1.0  # MB
        self.A_bar = 0.0
        self.mu = 1000.0  # default service rate (tx/s) - user sets
        self.state = "Steady"

    def set_service_rate(self, mu: float):
        self.mu = float(mu)

    def update(self, arrivals: float, confirmed: float, network_capacity: float):
        """
        arrivals: number of tx arrived in epoch
        confirmed: number of tx confirmed in epoch
        network_capacity: theoretical capacity (in txs) for threshold tau computation
        """
        # update EMA
        if self.A_bar == 0:
            self.A_bar = arrivals
        else:
            self.A_bar = self.beta * arrivals + (1 - self.beta) * self.A_bar

        tau = self.tau_fraction * network_capacity

        # compute proposed Lt+1
        if self.A_bar > self.mu and self.Lt < MAX_BLOCK_MB:
            proposed = min(self.Lt * (1 + (self.A_bar / max(self.mu, 1e-9))), MAX_BLOCK_MB)
        else:
            proposed = max(self.Lt * self.decay, MIN_BLOCK_MB)

        # state transitions
        ratio = arrivals / max(confirmed, 1.0)
        if ratio > tau and self.Lt < MAX_BLOCK_MB:
            self.state = "Growth"
        elif ratio <= 0.5 and self.Lt > MIN_BLOCK_MB:
            self.state = "Contraction"
        else:
            self.state = "Steady"

        self.Lt = proposed
        return self.Lt

    def lyapunov_bound(self, Q_t: float, expected_arrival_var: float = 1.0, expected_service_var: float = 1.0):
        """
        Compute a conservative bound on Lyapunov drift as in the manuscript:
        E[L(t+1)-L(t)] <= E[Q(t)(A(t)-S(t))] + E[A^2 + S^2]
        Here we return the RHS given current estimates.
        """
        S_t = (self.Lt * 1e6) / 48.0 / EPOCH_SECONDS  # crude mapping: block MB -> txs/sec
        drift = Q_t * (self.A_bar - S_t) + (expected_arrival_var + expected_service_var)
        return drift
