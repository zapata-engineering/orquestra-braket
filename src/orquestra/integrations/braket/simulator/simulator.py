################################################################################
# © Copyright 2021-2022 Zapata Computing Inc.
################################################################################

from typing import Dict, List, Optional, Sequence, Union

import numpy as np
from orquestra.quantum.api.backend import QuantumSimulator, StateVector
from orquestra.quantum.circuits import Circuit
from orquestra.quantum.measurements import (
    ExpectationValues,
    Measurements,
    expectation_values_to_real,
)
from orquestra.quantum.openfermion import SymbolicOperator, get_sparse_operator

from ..conversions import export_to_braket


class BraketSimulator(QuantumSimulator):
    def __init__(self, simulator, noise_model=None):

        """initializes the parameters for the system or simulator
        Args:
            simulator: Braket simulator that is defined by the user
            noise_model: optional argument to define the noise model
        """

        super().__init__()

        self.simulator = simulator

        self.noise_model = noise_model

    def run_circuit_and_measure(self, circuit: Circuit, n_samples: int) -> Measurements:

        """Run a circuit and measure a certain number of bitstrings.
        Args:
            circuit: the circuit to prepare the state.
            n_samples: number of bitstrings to measure. If None, `self.n_samples`
                is used.
        Returns:
            A list of bitstrings.
        """
        super().run_circuit_and_measure(circuit, n_samples)

        braket_circuit = export_to_braket(circuit)

        result_object = self.simulator.run(braket_circuit, shots=n_samples).result()

        return _get_measurement_from_braket_result_object(result_object)

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


def _get_measurement_from_braket_result_object(result_object) -> Measurements:
    """Extract measurement bitstrings from braket result object.
    Args:
        result_object: object returned by braket simulator's run or run_batch.
    Return:
        Measurements.
    """
    samples = [
        tuple(key for key in numpy_bitstring)
        for numpy_bitstring in result_object.measurements
    ]

    return Measurements(samples)
