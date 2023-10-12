import pytest
from orquestra.quantum.api.circuit_runner_contracts import CIRCUIT_RUNNER_CONTRACTS
from orquestra.quantum.api.wavefunction_simulator_contracts import (
    simulator_contracts_for_tolerance,
    simulator_contracts_with_nontrivial_initial_state,
    simulator_gate_compatibility_contracts,
)

from orquestra.integrations.braket.simulator import braket_local_simulator


@pytest.mark.local
@pytest.mark.parametrize(
    "contract", simulator_contracts_with_nontrivial_initial_state()
)
def test_braket_local_wf_simulator_raises_error(contract):
    simulator = braket_local_simulator()
    with pytest.raises(ValueError):
        contract(simulator)


@pytest.mark.local
@pytest.mark.parametrize("contract", simulator_contracts_for_tolerance())
def test_braket_local_wf_simulator_fulfills_simulator_contracts(contract):
    simulator = braket_local_simulator()
    assert contract(simulator)


@pytest.mark.local
@pytest.mark.parametrize("contract", CIRCUIT_RUNNER_CONTRACTS)
def test_braket_local_wf_simulator_fulfills_circuit_runner_contracts(contract):
    simulator = braket_local_simulator()
    assert contract(simulator)


@pytest.mark.local
# Braket doesn't support the RH gate, so we're excluding it from the test set.
@pytest.mark.parametrize(
    "contract", simulator_gate_compatibility_contracts(gates_to_exclude=["RH"])
)
def test_braket_simulator_uses_correct_gate_definitionscontract(contract):
    simulator = braket_local_simulator()
    assert contract(simulator)
