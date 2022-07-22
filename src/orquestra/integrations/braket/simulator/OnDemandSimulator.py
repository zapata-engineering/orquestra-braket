################################################################################
# © Copyright 2021-2022 Zapata Computing Inc.
################################################################################

import boto3
from braket.aws import AwsDevice
from braket.aws.aws_session import AwsSession

from ._base import BraketBasedSimulator


class BraketOnDemandSimulator(BraketBasedSimulator):
    supports_batching = False

    def __init__(self, simulator: str, boto_session, noise_model=None):

        aws_session = AwsSession(boto_session)

        simulators = AwsDevice.get_devices(types=["SIMULATOR"], aws_session=aws_session)
        if simulator not in [braket_simulator.name for braket_simulator in simulators]:
            raise ValueError("The simulator provided is not a Braket Simulator")

        if noise_model is None:
            simulator = AwsDevice(_get_simulator_arn(simulator, aws_session))
        else:
            simulator = AwsDevice(_get_simulator_arn("dm1", aws_session))

        super().__init__(simulator, noise_model)


def _get_simulator_arn(name, aws_session):
    simulator_properties = AwsDevice.get_devices(names=[name], aws_session=aws_session)[
        0
    ]

    return simulator_properties.arn
