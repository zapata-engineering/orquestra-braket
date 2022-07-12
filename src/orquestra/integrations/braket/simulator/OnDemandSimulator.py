################################################################################
# © Copyright 2021-2022 Zapata Computing Inc.
################################################################################

from braket.aws import AwsDevice

from .simulator import BraketSimulator


class BraketOnDemandSimulator(BraketSimulator):
    supports_batching = False

    def __init__(self, simulator: str, noise_model=None):

        simulators = AwsDevice.get_devices(types=["SIMULATOR"])
        if simulator not in [braket_simulator.name for braket_simulator in simulators]:
            raise ValueError("The simulator provided is not a Braket Simulator")

        if noise_model is None:
            simulator = AwsDevice(get_simulator_arn(simulator))
        else:
            simulator = AwsDevice(get_simulator_arn("dm1"))

        super().__init__(simulator, noise_model)


def get_simulator_arn(name):
    simulator_properties = AwsDevice.get_devices(names=[name])[0]

    return simulator_properties.arn
