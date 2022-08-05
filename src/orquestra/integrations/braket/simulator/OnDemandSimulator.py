################################################################################
# © Copyright 2021-2022 Zapata Computing Inc.
################################################################################

from boto3 import Session  # type: ignore
from braket.aws import AwsDevice
from braket.aws.aws_session import AwsSession
from orquestra.quantum.api.backend import QuantumSimulator
from orquestra.quantum.circuits import Circuit
from orquestra.quantum.distributions import MeasurementOutcomeDistribution
from orquestra.quantum.measurements import Measurements

from ._base import _get_arn, _run_circuit_and_measure


class BraketOnDemandSimulator:
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
        self.number_of_jobs_run = 0
        self.number_of_circuits_run = 0

    def run_circuit_and_measure(self, circuit: Circuit, n_samples: int) -> Measurements:

        """Run a circuit and measure a certain number of bitstrings.
        Args:
            circuit: the circuit to prepare the state.
            n_samples: number of bitstrings to measure. If None, `self.n_samples`
                is used.
        Returns:
            A list of bitstrings.
        """

        if n_samples < 1:
            raise ValueError("Must sample given circuit at least once.")
        self.number_of_circuits_run += 1
        self.number_of_jobs_run += 1

        return _run_circuit_and_measure(self, circuit, n_samples)

    def run_circuitset_and_measure(self, circuits, n_samples):
        return QuantumSimulator.run_circuitset_and_measure(self, circuits, n_samples)

    def get_measurement_outcome_distribution(
        self, circuit: Circuit, n_samples: int
    ) -> MeasurementOutcomeDistribution:
        """Calculates a measurement outcome distribution.
        Args:
            circuit: quantum circuit to be executed.
            n_samples: number of samples to collect
        Returns:
            Probability distribution of getting specific bistrings.
        """
        # Get the expectation values
        measurements = self.run_circuit_and_measure(circuit, n_samples)
        return measurements.get_distribution()


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
