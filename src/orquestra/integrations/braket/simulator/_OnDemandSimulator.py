################################################################################
# © Copyright 2021-2022 Zapata Computing Inc.
################################################################################

from boto3 import Session  # type: ignore
from braket.aws import AwsDevice
from braket.aws.aws_session import AwsSession
from orquestra.quantum.api import BaseCircuitRunner
from orquestra.quantum.circuits import Circuit
from orquestra.quantum.distributions import MeasurementOutcomeDistribution
from orquestra.quantum.measurements import Measurements

from orquestra.integrations.braket.conversions import export_to_braket

from ._utils import _get_arn


class BraketOnDemandSimulator(BaseCircuitRunner):
    supports_batching = False

    def __init__(
        self,
        boto_session: Session,
        simulator_string: str = "SV1",
        noise_model=None,
    ):
        """
        This function initiates the BraketOnDemandSimulator

        Args:
            boto_session: boto session created by boto3.Session
            simulator: Name of the simulator as a tring. Defaults to "SV1".
            noise_model :optional argument to define the noise model.

        Raises:
            ValueError: Raises an error if the name of the simulator
            fails to match the simulators provided by Braket
        """
        aws_session = AwsSession(boto_session)

        simulators_supported = get_on_demand_simulator_names(aws_session)
        if simulator_string not in simulators_supported:
            raise ValueError(
                "The simulator provided is not a Braket Simulator"
                "Please visit https://aws.amazon.com/braket/quantum-computers/"
                "to find the available simulator names"
            )

        if noise_model is None:
            simulator = AwsDevice(_get_arn(simulator_string, aws_session))
        else:
            simulator = AwsDevice(_get_arn("dm1", aws_session))

        self.simulator = simulator
        self.noise_mode = noise_model

        self.supports_batching = False

        self.device_connectivity = None
        self.is_natively_supported = None

        self.batch_size = 0
        self._n_circuits_executed = 0
        self._n_jobs_executed = 0

    def _run_and_measure(self, circuit: Circuit, n_samples: int) -> Measurements:

        """Run a circuit and measure a certain number of bitstrings.
        Args:
            circuit: the circuit to prepare the state.
            n_samples: number of bitstrings to measure. If None, `self.n_samples`
                is used.
        Returns:
            A list of bitstrings.
        """

        braket_circuit = export_to_braket(circuit)

        result_object = self.simulator.run(braket_circuit, shots=n_samples).result()

        return _get_measurement_from_braket_result_object(result_object)


def get_on_demand_simulator_names(aws_session):
    """This function retrives the names of the simulators
    that are available on Braket

    Args:
        aws_session : AwsSession created using boto3.Session:

    Returns:
        List : list of names for on-demand simulators provided by Braket
    """
    simulators = AwsDevice.get_devices(types=["SIMULATOR"], aws_session=aws_session)
    return [braket_simulator.name for braket_simulator in simulators]


def _get_measurement_from_braket_result_object(result_object) -> Measurements:
    """Extract measurement bitstrings from braket result object.
    Args:
        result_object: object returned by braket simulator's run or run_batch.
    Return:
        Measurements.
    """
    samples = [
        tuple(key for key in numpy_bitstring)
        for numpy_bitstring in result_object.measurements
    ]

    return Measurements(samples)
