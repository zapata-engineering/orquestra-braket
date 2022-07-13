################################################################################
# © Copyright 2021-2022 Zapata Computing Inc.
################################################################################

from braket.devices import LocalSimulator

from ._simulator import BraketSimulator


class BraketLocalSimulator(BraketSimulator):
    """Simulator using Braket's LocalSimulator.
    Args:
        noise_model: an optional noise model to pass in for noisy simulations

    Attributes:
        simulator: Braket simulator this class uses.
        noise_model: an optional noise model to pass in for noisy simulations

    """

    supports_batching = False

    def __init__(self, noise_model=None):

        if noise_model is None:
            simulator = LocalSimulator(backend="braket_sv")
        else:
            simulator = LocalSimulator(backend="braket_dm")

        super().__init__(simulator, noise_model)
