from typing import List, Optional, Tuple, Type, Union

from boto3 import Session  # type: ignore
from braket.aws import AwsDevice, AwsDeviceType, AwsSession
from braket.circuits import Noise
from braket.devices import Device, LocalSimulator
from orquestra.quantum.api.circuit_runner import BaseCircuitRunner
from orquestra.quantum.circuits import Circuit
from orquestra.quantum.measurements import Measurements

from orquestra.integrations.braket._utils import _get_arn
from orquestra.integrations.braket.conversions import export_to_braket


class BraketRunner(BaseCircuitRunner):
    def __init__(
        self,
        device: Device,
        noise_model: Optional[Type[Noise]] = None,
        s3_destination_folder: Optional[Union[str, Tuple]] = None,
    ):
        """
        Initiates a runner for Braket supported runners

        Args:
            device: AWS runner object i.e LocalSimulator()
            noise_model: an optional noise model to pass in for noisy simulations
            s3_destination_folder: The S3 location to save the task's
            results to. The name of the bucket can be supplied as a
            string. The bucket name and the folder can be supplied
            as a tuple. If nothing was provided, the results will be
            stored in the default Braket bucket.
        """
        super().__init__()
        self.device = device
        self.noise_model = noise_model
        self.s3_destination_folder = s3_destination_folder

    def _run_and_measure(self, circuit: Circuit, n_samples: int) -> Measurements:
        """
        Runs the circuits and measures the outcome

        Args:
            circuit : the circuit to prepare the state
            n_samples: number of samples to for the circuit

        Returns:
            Measurement
        """
        braket_circuit = export_to_braket(circuit)
        if self.noise_model is not None:
            braket_circuit.apply_gate_noise(self.noise_model)

        if self.s3_destination_folder is not None:
            return self.device.run(
                braket_circuit, self.s3_destination_folder, shots=n_samples
            )

        result = self.device.run(braket_circuit, shots=n_samples).result()
        return Measurements.from_counts(result.measurement_counts)


def braket_local_runner(
    backend: Optional[str] = None, noise_model: Optional[Type[Noise]] = None
) -> BraketRunner:
    """
    Create a braket runner for Braket local simulator

    Args:
        backend: name of the Braket local simulator
        noise_model: optional noise model for the simulator

    Returns:
        BraketRunner
    """
    if backend is None:
        backend = "braket_dm" if noise_model is not None else "braket_sv"
    if backend != "braket_dm" and noise_model is not None:
        raise ValueError(
            "Noisy simulations are supported only for density matrix backend"
        )
    device = LocalSimulator(backend=backend)
    return BraketRunner(device, noise_model)


def aws_runner(
    boto_session: Session,
    name: str = "SV1",
    noise_model: Type[Noise] = None,
    s3_destination_folder: Optional[Union[str, Tuple]] = None,
) -> BraketRunner:
    """
    Create a braket runner for Braket on-demand simulators and QPU


    Args:
        boto_session: boto session created by boto3.Session
        name: name of the QPU or on-demand simulator
        noise_model: optional argument to define the noise model.
        s3_destination_folder: The S3 location to save the task's
        results to. The name of the bucket can be supplied as a
        string. The bucket name and the folder can be supplied
        as a tuple. If nothing was provided, the results will be
        stored in the default Braket bucket.

    Returns:
        BraketRunner for on-demand simulator or QPU
    """
    aws_session = AwsSession(boto_session)
    arn = _get_arn(name, aws_session)
    device = AwsDevice(arn, aws_session)

    if noise_model is not None and device.type != AwsDeviceType.SIMULATOR:
        raise ValueError(f"Simulator {name} cannot use noise model.")

    if device.type == AwsDeviceType.QPU and s3_destination_folder is None:
        raise ValueError("S3 destination folder is required for QPU tasks")

    return BraketRunner(device, noise_model, s3_destination_folder)


def get_QPU_names(boto_session: Session) -> List[str]:
    """This function retrives the names of the QPUs
    that are available on Braket
    Args:
        aws_session : Session created using boto3.Session:
    Returns:
        List : list of names for QPUs provided by Braket
    """
    aws_session = AwsSession(boto_session)
    QPUs = AwsDevice.get_devices(types=["QPU"], aws_session=aws_session)
    return [braket_QPU.name for braket_QPU in QPUs]
