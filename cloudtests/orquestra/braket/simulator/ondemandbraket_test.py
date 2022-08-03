################################################################################
# © Copyright 2021-2022 Zapata Computing Inc.
################################################################################

import pytest
from boto3 import Session  # type: ignore
from braket.circuits.noise import Noise
from orquestra.quantum.api.backend_test import QuantumSimulatorTests
from orquestra.quantum.circuits import CNOT, Circuit, X

from orquestra.integrations.braket.simulator import BraketOnDemandSimulator

boto_session = Session(profile_name="AWSBraketFullAccess", region_name="us-east-1")


@pytest.fixture(
    params=[
        {
            "simulator_string": "SV1",
            "boto_session": boto_session,
            "noise_model": None,
        },
        {
            "simulator_string": "TN1",
            "boto_session": boto_session,
            "noise_model": None,
        },
        {
            "simulator_string": "dm1",
            "boto_session": boto_session,
            "noise_model": None,
        },
        {
            "simulator_string": "dm1",
            "boto_session": boto_session,
            "noise_model": Noise.Depolarizing(probability=0.0),
        },
    ]
)
def backend(request):
    return BraketOnDemandSimulator(**request.param)


@pytest.fixture()
def noisy_simulator():
    noise_model = Noise.Depolarizing(probability=0.0002)
    return BraketOnDemandSimulator("dm1", boto_session, noise_model=noise_model)


@pytest.mark.cloud
class TestBraketOnDemandSimulator(QuantumSimulatorTests):
    def test_run_circuit_and_measure(self, backend):
        # Given
        circuit = Circuit([X(0), CNOT(1, 2)])
        measurements = backend.run_circuit_and_measure(circuit, n_samples=100)
        assert len(measurements.bitstrings) == 100

        for measurement in measurements.bitstrings:
            assert measurement == (1, 0, 0)

    def test_measuring_inactive_qubits(self, backend):
        # Given
        circuit = Circuit([X(0), CNOT(1, 2)], n_qubits=4)
        measurements = backend.run_circuit_and_measure(circuit, n_samples=100)
        assert len(measurements.bitstrings) == 100

        for measurement in measurements.bitstrings:
            assert measurement == (1, 0, 0, 0)

    def test_run_circuitset_and_measure(self, backend):
        # Given
        circuit = Circuit([X(0), CNOT(1, 2)])
        n_circuits = 5
        n_samples = 100
        # When
        measurements_set = backend.run_circuitset_and_measure(
            [circuit] * n_circuits, n_samples=[100] * n_circuits
        )
        # Then
        assert len(measurements_set) == n_circuits
        for measurements in measurements_set:
            assert len(measurements.bitstrings) == n_samples
            for measurement in measurements.bitstrings:
                assert measurement == (1, 0, 0)

    def test_run_circuit_and_measure_seed(self, backend):
        # Given
        circuit = Circuit([X(0), CNOT(1, 2)])
        simulator1 = backend
        simulator2 = backend

        # When
        measurements1 = simulator1.run_circuit_and_measure(circuit, n_samples=1000)
        measurements2 = simulator2.run_circuit_and_measure(circuit, n_samples=1000)

        # Then
        for (meas1, meas2) in zip(measurements1.bitstrings, measurements2.bitstrings):
            assert meas1 == meas2

    def test_get_wavefunction_uses_provided_initial_state(self):
        pytest.xfail("Braket simulator only accepts zero state as initial state")

    def test_get_wavefunction(self):
        pytest.xfail("Braket on demand simulators do not return wavefunction")

    def test_get_exact_expectation_values(self):
        pytest.xfail("Braket on demand simulators do not return wavefunction")

    def test_get_measurement_outcome_distribution_wf_simulators(self):
        pytest.xfail("Braket on demand simulators do not return wavefunction")
