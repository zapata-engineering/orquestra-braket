################################################################################
# © Copyright 2021-2022 Zapata Computing Inc.
################################################################################

import numpy as np
from braket.devices import LocalSimulator
from orquestra.quantum.api.backend import QuantumSimulator, StateVector
from orquestra.quantum.circuits import Circuit
from orquestra.quantum.measurements import (
    ExpectationValues,
    Measurements,
    expectation_values_to_real,
)
from orquestra.quantum.openfermion import SymbolicOperator, get_sparse_operator

from ..conversions import export_to_braket
from ._base import _run_circuit_and_measure


class BraketLocalSimulator(QuantumSimulator):
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

        super().__init__()

        self.simulator = simulator

        self.noise_model = noise_model

        self.batch_size = 0
        self.number_of_jobs_run = 0
        self.number_of_circuits_run = 0

    def run_circuit_and_measure(self, circuit: Circuit, n_samples: int) -> Measurements:
        if n_samples < 1:
            raise ValueError("Must sample given circuit at least once.")
        self.number_of_circuits_run += 1
        self.number_of_jobs_run += 1

        return _run_circuit_and_measure(self, circuit, n_samples)

    def _get_wavefunction_from_native_circuit(
        self,
        circuit: Circuit,
        initial_state: StateVector,
    ) -> StateVector:
        """Uses the statevector simulator to create wave function

        Args:
            circuit: the circuit to prepare the state
            initial_state: initial state of the system

        Raises:
            ValueError: Braket simulator will raise an error if the initial
            state is not in the zero state

        Returns:
            wave function as a state vector
        """

        braket_circuit = export_to_braket(circuit)

        if initial_state[0] != 1:
            raise ValueError(
                "AWS Braket simulators can be initialized only in the zero states"
            )

        braket_circuit.state_vector()

        result = self.simulator.run(braket_circuit, shots=0).result()

        return np.array(result.values[0], np.complex64)

    def get_exact_noisy_expectation_values(
        self, circuit: Circuit, qubit_operator: SymbolicOperator
    ) -> ExpectationValues:
        """Compute exact expectation values w.r.t. given operator in presence of noise.

        Note that this method can be used only if simulator's noise_model is not set
        to None.

        Args:
            circuit: the circuit to prepare the state
            qubit_operator: the operator to measure
        Returns:
            the expectation values of each term in the operator
        Raises:
            RuntimeError if this simulator's noise_model is None.
        """
        if self.noise_model is None:
            raise RuntimeError(
                "Please provide noise model to get exact noisy expectation values"
            )

        braket_circuit = export_to_braket(circuit)
        values = []

        for pauli_term in qubit_operator:
            sparse_pauli_term_ndarray = get_sparse_operator(
                pauli_term, n_qubits=circuit.n_qubits
            ).toarray()
            if np.size(sparse_pauli_term_ndarray) == 1:
                expectation_value = sparse_pauli_term_ndarray[0][0]
                values.append(expectation_value)

            else:

                braket_circuit.apply_gate_noise(self.noise_model)
                braket_circuit.density_matrix()
                result_object = self.simulator.run(braket_circuit, shots=0).result()

                rho = result_object.values[0]
                expectation_value = np.real(np.trace(rho @ sparse_pauli_term_ndarray))
                values.append(expectation_value)
        return expectation_values_to_real(ExpectationValues(np.asarray(values)))
