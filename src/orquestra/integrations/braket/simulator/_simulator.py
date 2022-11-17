from typing import Optional

import numpy as np
from braket.devices import Device, LocalSimulator
from orquestra.quantum.circuits import Circuit
from orquestra.quantum.operators import PauliRepresentation, get_expectation_value
from orquestra.quantum.typing import StateVector
from orquestra.quantum.wavefunction import Wavefunction

from orquestra.integrations.braket.conversions import export_to_braket
from orquestra.integrations.braket.runner import BraketRunner


class _BraketWavefunctionSimulator(BraketRunner):

    def __init__(self, device: Device):
        super().__init__(device)

    def get_wavefunction(
        self, circuit: Circuit, initial_state: Optional[StateVector] = None
    ) -> Wavefunction:
        # TODO: raise ValueError if initial state is not [00000>
        braket_circuit = export_to_braket(circuit)
        braket_circuit.state_vector()

        result = self.device.run(braket_circuit, shots=0).result()
        self._n_jobs_executed += 1
        self._n_circuits_executed += 1
        return Wavefunction(np.array(result.values[0], np.complex64))

    def get_exact_expectation_values(
        self, circuit: Circuit, operator: PauliRepresentation
    ) -> float:
        wavefunction = self.get_wavefunction(circuit)
        return get_expectation_value(operator, wavefunction).real


def braket_local_simulator():
    return _BraketWavefunctionSimulator(LocalSimulator())
