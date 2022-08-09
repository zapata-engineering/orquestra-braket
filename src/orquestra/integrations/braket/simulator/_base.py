################################################################################
# © Copyright 2021-2022 Zapata Computing Inc.
################################################################################

from typing import List, Sequence

import numpy as np
from braket.aws import AwsDevice
from orquestra.quantum.circuits import Circuit
from orquestra.quantum.measurements import Measurements
from orquestra.quantum.openfermion import get_sparse_operator

from ..conversions import export_to_braket


def _run_circuit_and_measure(self, circuit: Circuit, n_samples: int) -> Measurements:

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


def _run_circuitset_and_measure(
    self, circuits: Sequence[Circuit], n_samples: Sequence[int]
) -> List[Measurements]:
    """Run a set of circuits and measure a certain number of bitstrings.

    It may be useful to override this method for backends that support
    batching.

    Args:
        circuits: The circuits to execute.
        n_samples: The number of samples to collect for each circuit.
    """
    measurement_set: List[Measurements]

    if not self.supports_batching:
        measurement_set = []
        for circuit, n_samples_for_circuit in zip(circuits, n_samples):
            measurement_set.append(
                self.run_circuit_and_measure(circuit, n_samples=n_samples_for_circuit)
            )

        return measurement_set
    else:
        self.number_of_circuits_run += len(circuits)
        if isinstance(self.batch_size, int):
            self.number_of_jobs_run += int(np.ceil(len(circuits) / self.batch_size))

        # This value is only returned so that mypy doesn't complain.
        # You can remove this workaround when we reimplement counter increments in
        # a more type-elegant way.
        measurement_set = []
        return measurement_set


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


def _get_arn(name: str, aws_session):
    """
    This function extracts the Amazon Resources Name (arn) of the simulator or hardware
    See https://docs.aws.amazon.com/braket/latest/developerguide/braket-devices.html
    to find lists of resources that are available.

    Args:
        name : name of the device or simulator
        aws_session : AwsSession created using boto3.Session

    Returns:
        arn : string with arn

    Examples:
        >>> from boto3 import Session
        >>> from braket.aws.aws_session import AwsSession
        >>> boto_sess = Session(profile_name, region)
        >>> aws_session = AwsSession(boto_sess)
        >>> name = "SV1"
        >>> _get_arn(name, boto_sess)
    """

    simulator_properties = AwsDevice.get_devices(names=[name], aws_session=aws_session)[
        0
    ]

    return simulator_properties.arn
