################################################################################
# © Copyright 2021-2022 Zapata Computing Inc.
################################################################################

import os
from unittest.mock import Mock

import pytest
from boto3 import Session  # type: ignore
from braket.circuits.noise import Noise
from orquestra.quantum.api.circuit_runner_contracts import (
    CIRCUIT_RUNNER_CONTRACTS,
    STRICT_CIRCUIT_RUNNER_CONTRACTS,
)
from orquestra.quantum.api.wavefunction_simulator_contracts import (
    simulator_contracts_for_tolerance,
)
from orquestra.quantum.circuits import CNOT, Circuit, X

from orquestra.integrations.braket.simulator import BraketOnDemandSimulator

boto_session_type = os.environ["SESSION_TYPE"]

if boto_session_type == "mock":
    boto_session = Mock(spec=Session)
else:
    region_name = os.environ["AWS_DEFAULT_REGION"]
    boto_session = Session(region_name=region_name)


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
def runner(request):
    return BraketOnDemandSimulator(**request.param)


@pytest.fixture()
def noisy_simulator():
    noise_model = Noise.Depolarizing(probability=0.0002)
    return BraketOnDemandSimulator("dm1", boto_session, noise_model=noise_model)


@pytest.mark.cloud
class TestBraketOnDemandSimulator:
    def test_run_and_measure(self, runner):
        # Given
        circuit = Circuit([X(0), CNOT(1, 2)])
        measurements = runner.run_and_measure(circuit, n_samples=100)
        assert len(measurements.bitstrings) == 100

        for measurement in measurements.bitstrings:
            assert measurement == (1, 0, 0)

    def test_measuring_inactive_qubits(self, runner):
        # Given
        circuit = Circuit([X(0), CNOT(1, 2)], n_qubits=4)
        measurements = runner.run_and_measure(circuit, n_samples=100)
        assert len(measurements.bitstrings) == 100

        for measurement in measurements.bitstrings:
            assert measurement == (1, 0, 0, 0)

    def test_run_batch_and_measure(self, runner):
        # Given
        circuit = Circuit([X(0), CNOT(1, 2)])
        n_circuits = 5
        n_samples = 100
        # When
        measurements_set = runner.run_batch_and_measure(
            [circuit] * n_circuits, n_samples=[100] * n_circuits
        )
        # Then
        assert len(measurements_set) == n_circuits
        for measurements in measurements_set:
            assert len(measurements.bitstrings) == n_samples
            for measurement in measurements.bitstrings:
                assert measurement == (1, 0, 0)

    def test_get_wavefunction_uses_provided_initial_state(self):
        pytest.xfail("Braket simulator only accepts zero state as initial state")

    def test_get_wavefunction(self):
        pytest.xfail("Braket on demand simulators do not return wavefunction")

    def test_get_exact_expectation_values(self):
        pytest.xfail("Braket on demand simulators do not return wavefunction")

    def test_get_measurement_outcome_distribution_wf_simulators(self):
        pytest.xfail("Braket on demand simulators do not return wavefunction")


@pytest.mark.cloud
@pytest.mark.parametrize("contract", CIRCUIT_RUNNER_CONTRACTS)
def test_braket_local_runner_fulfills_circuit_runner_contracts(runner, contract):
    assert contract(runner)


@pytest.mark.cloud
@pytest.mark.parametrize("contract", STRICT_CIRCUIT_RUNNER_CONTRACTS)
def test_symbolic_simulator_fulfills_strict_circuit_runnner(runner, contract):
    assert contract(runner)
