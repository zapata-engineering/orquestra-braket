import pytest
from orquestra.quantum.api.circuit_runner_contracts import CIRCUIT_RUNNER_CONTRACTS
from orquestra.quantum.api.wavefunction_simulator_contracts import simulator_contracts_for_tolerance


from orquestra.integrations.braket.simulator import braket_local_simulator


@pytest.mark.parametrize(
    "contract", simulator_contracts_for_tolerance()
)
def test_braket_local_wf_simulator_fulfills_simulator_contracts(
    contract
):
    simulator = braket_local_simulator()
    assert contract(simulator)


@pytest.mark.parametrize(
    "contract", CIRCUIT_RUNNER_CONTRACTS
)
def test_braket_local_wf_simulator_fulfills_circuit_runner_contracts(
    contract
):
    simulator = braket_local_simulator()
    assert contract(simulator)
