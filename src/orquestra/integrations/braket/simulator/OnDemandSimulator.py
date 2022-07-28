################################################################################
# © Copyright 2021-2022 Zapata Computing Inc.
################################################################################
from typing import Any

from braket.aws import AwsDevice
from braket.aws.aws_session import AwsSession

from ._base import BraketBasedSimulator, _get_arn


class BraketOnDemandSimulator:
    supports_batching = False

    def __init__(
        self,
        boto_session: Any,
        simulator: str = "SV1",
        noise_model=None,
        braket_based_simulator: Any = BraketBasedSimulator,
    ):
        aws_session = AwsSession(boto_session)

        simulators = AwsDevice.get_devices(types=["SIMULATOR"], aws_session=aws_session)
        if simulator not in [braket_simulator.name for braket_simulator in simulators]:
            raise ValueError("The simulator provided is not a Braket Simulator")

        if noise_model is None:
            simulator = AwsDevice(_get_arn(simulator, aws_session))
        else:
            simulator = AwsDevice(_get_arn("dm1", aws_session))

        self.simulator = braket_based_simulator(simulator, noise_model)
        self.run_circuit_and_measure = self.simulator.run_circuit_and_measure
        self.run_circuitset_and_measure = self.simulator.run_circuitset_and_measure
        self.supports_batching = self.simulator.supports_batching
        self.batch_size = self.simulator.batch_size
        self.number_of_jobs_run = self.simulator.number_of_jobs_run
        self.noise_mode = noise_model
        self.number_of_circuits_run = self.simulator.number_of_circuits_run
        self.device_connectivity = self.simulator.device_connectivity
        self.get_measurement_outcome_distribution = (
            self.simulator.get_measurement_outcome_distribution
        )
        self.is_natively_supported = self.simulator.is_natively_supported
