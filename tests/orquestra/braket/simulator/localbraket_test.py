################################################################################
# © Copyright 2021-2022 Zapata Computing Inc.
################################################################################
import numpy as np
import pytest
from braket.circuits.noise import Noise
from orquestra.quantum.api.backend_test import (
    QuantumSimulatorGatesTest,
    QuantumSimulatorTests,
)
from orquestra.quantum.circuits import CNOT, Circuit, H, X
from orquestra.quantum.operators import PauliTerm

from orquestra.integrations.braket.simulator import BraketLocalSimulator


@pytest.fixture(
    params=[
        {
            "noise_model": None,
        },
        {
            "noise_model": Noise.Depolarizing(probability=0.0),
        },
    ]
)
def backend(request):
    return BraketLocalSimulator(**request.param)


@pytest.fixture()
def wf_simulator():
    return BraketLocalSimulator()


@pytest.fixture()
def noisy_simulator():
    noise_model = Noise.Depolarizing(probability=0.0002)
    return BraketLocalSimulator(noise_model=noise_model)


@pytest.mark.local
class TestBraketLocalSimulator(QuantumSimulatorTests):
    def test_setup_basic_simulators(self, wf_simulator):
        assert isinstance(wf_simulator, BraketLocalSimulator)
        # assert wf_simulator.noise_model is None

    def test_run_circuit_and_measure(self):
        # Given
        circuit = Circuit([X(0), CNOT(1, 2)])
        simulator = BraketLocalSimulator()
        measurements = simulator.run_circuit_and_measure(circuit, n_samples=100)
        assert len(measurements.bitstrings) == 100

        for measurement in measurements.bitstrings:
            assert measurement == (1, 0, 0)

    def test_measuring_inactive_qubits(self):
        # Given
        circuit = Circuit([X(0), CNOT(1, 2)], n_qubits=4)
        simulator = BraketLocalSimulator()
        measurements = simulator.run_circuit_and_measure(circuit, n_samples=100)
        assert len(measurements.bitstrings) == 100

        for measurement in measurements.bitstrings:
            assert measurement == (1, 0, 0, 0)

    def test_run_circuitset_and_measure(self):
        # Given
        simulator = BraketLocalSimulator()
        circuit = Circuit([X(0), CNOT(1, 2)])
        n_circuits = 5
        n_samples = 100
        # When
        measurements_set = simulator.run_circuitset_and_measure(
            [circuit] * n_circuits, n_samples=[100] * n_circuits
        )
        # Then
        assert len(measurements_set) == n_circuits
        for measurements in measurements_set:
            assert len(measurements.bitstrings) == n_samples
            for measurement in measurements.bitstrings:
                assert measurement == (1, 0, 0)

    def test_get_wavefunction(self):
        # Given
        simulator = BraketLocalSimulator()
        circuit = Circuit([H(0), CNOT(0, 1), CNOT(1, 2)])

        # When
        wavefunction = simulator.get_wavefunction(circuit)
        # Then
        assert isinstance(wavefunction.amplitudes, np.ndarray)
        assert len(wavefunction.amplitudes) == 8
        assert np.isclose(
            wavefunction.amplitudes[0], (1 / np.sqrt(2) + 0j), atol=10e-15
        )
        assert np.isclose(
            wavefunction.amplitudes[7], (1 / np.sqrt(2) + 0j), atol=10e-15
        )

    def test_get_exact_expectation_values(self):
        # Given
        simulator = BraketLocalSimulator()
        circuit = Circuit([H(0), CNOT(0, 1), CNOT(1, 2)])
        qubit_operator = (
            PauliTerm.identity() * 2
            - PauliTerm({0: "Z", 1: "Z"})
            + PauliTerm({0: "X", 2: "X"})
        )
        target_values = np.array([2.0, -1.0, 0.0])

        # When

        expectation_values = simulator.get_exact_expectation_values(
            circuit, qubit_operator
        )
        # Then
        np.testing.assert_array_almost_equal(expectation_values.values, target_values)

    def test_get_noisy_exact_expectation_values(self):
        # Given
        noise = 0.0002
        noise_model = Noise.Depolarizing(probability=noise)
        simulator = BraketLocalSimulator(noise_model=noise_model)
        circuit = Circuit([H(0), CNOT(0, 1), CNOT(1, 2)])
        qubit_operator = PauliTerm({0: "Z", 1: "Z"}, -1) + PauliTerm({0: "X", 2: "X"})
        target_values = np.array([-0.9986673775881747, 0.0])

        expectation_values = simulator.get_exact_noisy_expectation_values(
            circuit, qubit_operator
        )
        np.testing.assert_almost_equal(
            expectation_values.values[0], target_values[0], 2
        )
        np.testing.assert_almost_equal(expectation_values.values[1], target_values[1])

    def test_run_circuit_and_measure_seed(self):
        # Given
        circuit = Circuit([X(0), CNOT(1, 2)])
        simulator1 = BraketLocalSimulator()
        simulator2 = BraketLocalSimulator()

        # When
        measurements1 = simulator1.run_circuit_and_measure(circuit, n_samples=1000)
        measurements2 = simulator2.run_circuit_and_measure(circuit, n_samples=1000)

        # Then
        for (meas1, meas2) in zip(measurements1.bitstrings, measurements2.bitstrings):
            assert meas1 == meas2

    def test_get_wavefunction_seed(self):
        # Given
        circuit = Circuit([H(0), CNOT(0, 1), CNOT(1, 2)])
        simulator1 = BraketLocalSimulator()
        simulator2 = BraketLocalSimulator()

        # When
        wavefunction1 = simulator1.get_wavefunction(circuit)
        wavefunction2 = simulator2.get_wavefunction(circuit)

        # Then
        for (ampl1, ampl2) in zip(wavefunction1.amplitudes, wavefunction2.amplitudes):
            assert ampl1 == ampl2

    def test_get_wavefunction_uses_provided_initial_state(self, wf_simulator):
        pytest.xfail("Braket simulator only accepts zero state as initial state")


@pytest.mark.local
class TestBraketLocalSimulatorGates(QuantumSimulatorGatesTest):
    atol_wavefunction = 1e-8
    gates_to_exclude = ["RH"]
