################################################################################
# © Copyright 2021-2022 Zapata Computing Inc.
################################################################################

from braket.devices import LocalSimulator

from .simulator import BraketSimulator


class BraketLocalSimulator(BraketSimulator):
    supports_batching = False

    def __init__(self, noise_model=None):
        super().__init__()

        if noise_model is None:
            simulator = LocalSimulator(backend="braket_sv")
        else:
            simulator = LocalSimulator(backend="braket_dm")

        super().__init__(simulator, noise_model)
