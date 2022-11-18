import os

import pytest
from boto3 import Session  # type: ignore
from braket.circuits import Noise
from braket.devices import LocalSimulator
from orquestra.quantum.api.circuit_runner_contracts import CIRCUIT_RUNNER_CONTRACTS

from orquestra.integrations.braket.runner import (
    BraketRunner,
    aws_runner,
    braket_local_runner,
)


@pytest.fixture()
def boto_session():
    return Session(region_name=os.environ.get("AWS_DEFAULT_REGION"))


@pytest.mark.local
@pytest.mark.parametrize("contract", CIRCUIT_RUNNER_CONTRACTS)
@pytest.mark.parametrize(
    "runner",
    [
        BraketRunner(device=LocalSimulator("braket_sv")),
        BraketRunner(device=LocalSimulator("braket_dm")),
        BraketRunner(
            device=LocalSimulator("braket_dm"),
            noise_model=Noise.Depolarizing(probability=0.5),
        ),
        braket_local_runner(),
        braket_local_runner(noise_model=Noise.Depolarizing(probability=0.1)),
    ],
)
def test_local_braket_runner_fulfills_circuit_runner_contracts(contract, runner):
    assert contract(runner)


@pytest.mark.cloud
@pytest.mark.parametrize("contract", CIRCUIT_RUNNER_CONTRACTS)
@pytest.mark.parametrize(
    "runner_params",
    [
        {"name": "SV1"},
        {"name": "TN1"},
        {"name": "dm1"},
        {"name": "dm1", "noise_model": Noise.Depolarizing(probability=0.4)},
    ],
)
def test_aws_runner_fulfills_circuit_runner_contracts(
    contract, runner_params, boto_session
):
    runner = aws_runner(**runner_params, boto_session=boto_session)
    assert contract(runner)


@pytest.mark.local
def test_sv_braket_local_runner_cannot_be_initialized_with_noise_model():
    with pytest.raises(ValueError):
        braket_local_runner(
            backend="braket_sv", noise_model=Noise.Depolarizing(probability=0.2)
        )


@pytest.mark.local
@pytest.mark.parametrize(
    "runner, expected_simulator_name",
    [
        (braket_local_runner(), "StateVectorSimulator"),
        (
            braket_local_runner(noise_model=Noise.Depolarizing(probability=0.2)),
            "DensityMatrixSimulator",
        ),
        (braket_local_runner("braket_dm"), "DensityMatrixSimulator"),
    ],
)
def test_braket_local_runner_chooses_correct_backend_based_on_input(
    runner, expected_simulator_name
):
    assert isinstance(runner.device, LocalSimulator)
    assert runner.device.name == expected_simulator_name
