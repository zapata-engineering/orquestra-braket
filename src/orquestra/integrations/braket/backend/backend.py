################################################################################
# © Copyright 2021-2022 Zapata Computing Inc.
################################################################################

from typing import Any, Optional, Sequence, Tuple, Union

from braket.aws import AwsDevice
from braket.aws.aws_session import AwsSession
from orquestra.quantum.circuits import Circuit
from orquestra.quantum.measurements import Measurements

from orquestra.integrations.braket.conversions import export_to_braket
from orquestra.integrations.braket.simulator._utils import _get_arn


class BraketBackend:
    supports_batching = False

    def __init__(
        self,
        boto_session: Any,
        QPU_name: str,
    ):

        """
        Initiates the QPU provided by Braket.

        Args:
            boto_session: boto session created using boto3.Session
            QPU_name: name of the QPU as a string


        Example:
        >>> from boto3 import Session
        >>> from orquestra.intergrations.braket.backend import BraketBackend
        >>> boto_sess = Session(profile_name, region_name="us-east-1")
        >>> backend = BraketBackend(boto_sess, "IonQ Device")

        """

        aws_session = AwsSession(boto_session)

        QPUs_provided = get_QPU_names(aws_session)
        if QPU_name not in QPUs_provided:
            raise ValueError(
                "The device provided is not supported by Braket"
                "Please visit https://aws.amazon.com/braket/quantum-computers/"
                "to find list of supported devices"
            )

        self.QPU = AwsDevice(_get_arn(QPU_name, aws_session))

    def run_and_measure(
        self,
        circuit: Circuit,
        n_samples: int,
        s3_destination_folder: Optional[Union[str, Tuple]] = None,
        poll_timeout_seconds: int = 432000,
        poll_interval_seconds: int = 1,
    ) -> Measurements:
        """
        This function will submit a single circuit to the
        Braket QPUs and returns the task.

        Args:
            circuit: The circuits to execute.
            n_samples: The number of samples to for the circuit.
            s3_destination_folder: The S3 location to save the task's
            results to. The name of the bucket can be supplied as a
            string. The bucket name and the folder can be supplied
            as a tuple. If nothing was provided, the results will be
            stored in the default Braket bucket.
            poll_timeout_seconds: number of seconds to wait before timeout
            poll_interval_seconds: interval between poll


        Returns:
            AWSQuantumTask: A class method to access the task
        """

        braket_circuit = export_to_braket(circuit)

        QPU_task = self.QPU.run(
            braket_circuit,
            s3_destination_folder=s3_destination_folder,
            shots=n_samples,
            poll_timeout_seconds=poll_timeout_seconds,
            poll_interval_seconds=poll_interval_seconds,
        )

        return QPU_task

    def run_batch_and_measure(
        self,
        circuitset: Sequence[Circuit],
        n_samples: int,
        s3_destination_folder: Optional[Union[str, Tuple]] = None,
        poll_timeout_seconds: int = 432000,
        poll_interval_seconds: int = 1,
    ):

        """
        This function will submit multiple circuits to the
        Braket QPUs and returns the task.

        Args:
            circuitset: The circuits to execute.
            n_samples: The number of samples to for all the circuits.
            s3_destination_folder: The S3 location to save the task's
            results to. The name of the bucket can be supplied as a
            string. The bucket name and the folder can be supplied
            as a tuple. If nothing was provided, the results will be
            stored in the default Braket bucket.
            poll_timeout_seconds: number of seconds to wait before timeout
            poll_interval_seconds: interval between poll


        Returns:
            AWSQuantumTaskBatch: A class method to access the task
        """

        braket_circuits = [export_to_braket(circuit) for circuit in circuitset]

        QPU_task = self.QPU.run_batch(
            braket_circuits,
            s3_destination_folder,
            shots=n_samples,
            poll_timeout_seconds=poll_interval_seconds,
            poll_interval_seconds=poll_interval_seconds,
        )

        return QPU_task


def get_QPU_names(aws_session):
    """This function retrives the names of the QPUs
    that are available on Braket

    Args:
        aws_session : AwsSession created using boto3.Session:

    Returns:
        List : list of names for QPUs provided by Braket
    """
    QPUs = AwsDevice.get_devices(types=["QPU"], aws_session=aws_session)
    return [braket_QPU.name for braket_QPU in QPUs]
