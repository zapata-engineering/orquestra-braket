import pytest

from orquestra.integrations.braket.simulator import BraketOnDemandSimulator


@pytest.mark.parametrize("sims", ["SV1", "TN1", "dm1"])
def test_ondemand_simulator_types(sims):
    sim = BraketOnDemandSimulator(sims)
