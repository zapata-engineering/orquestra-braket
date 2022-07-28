################################################################################
# © Copyright 2021-2022 Zapata Computing Inc.
################################################################################

from typing import Any, Optional, Sequence, Tuple, Union

from braket.aws import AwsDevice
from braket.aws.aws_session import AwsSession
from orquestra.quantum.circuits import Circuit
from orquestra.quantum.measurements import Measurements

from orquestra.integrations.braket.conversions import export_to_braket
from orquestra.integrations.braket.simulator._base import _get_arn


class BraketBackend:
    supports_batching = False

    def __init__(
        self,
        boto_session: Any,
        QPU_name: str,
    ):

        aws_session = AwsSession(boto_session)

        QPUs = AwsDevice.get_devices(types=["QPU"], aws_session=aws_session)
        if QPU_name not in [braket_QPU.name for braket_QPU in QPUs]:
            raise ValueError(
                "The device provided is not supported by Braket"
                "Please visit https://aws.amazon.com/braket/quantum-computers/"
                "to find list of supported devices"
            )

        self.QPU = AwsDevice(_get_arn(QPU_name, aws_session))

    def run_circuit_and_measure(
        self,
        circuit: Circuit,
        n_samples: int,
        s3_destination_folder: Optional[Union[str, Tuple]] = None,
    ) -> Measurements:

        braket_circuit = export_to_braket(circuit)

        QPU_task = self.QPU.run(
            braket_circuit, s3_destination_folder=s3_destination_folder, shots=n_samples
        )

        return QPU_task

    def run_circuit_batch_and_measure(
        self,
        circuitset: Sequence[Circuit],
        n_samples: int,
        s3_destination_folder: Optional[Union[str, Tuple]] = None,
    ):

        braket_circuits = [export_to_braket(circuit) for circuit in circuitset]

        QPU_task = self.QPU.run_batch(
            braket_circuits, s3_destination_folder, shots=n_samples
        )

        return QPU_task
