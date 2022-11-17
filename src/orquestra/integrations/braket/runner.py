from typing import Optional, Type

from boto3 import Session
from braket.aws import AwsSession, AwsDevice, AwsDeviceType
from braket.circuits import Noise
from braket.devices import Device, LocalSimulator
from orquestra.quantum.api.circuit_runner import BaseCircuitRunner
from orquestra.quantum.circuits import Circuit
from orquestra.quantum.measurements import Measurements

from orquestra.integrations.braket.conversions import export_to_braket
from orquestra.integrations.braket._utils import _get_arn


class BraketRunner(BaseCircuitRunner):

    def __init__(self, device: Device, noise_model: Optional[Type[Noise]] = None):
        super().__init__()
        self.device = device
        self.noise_model = noise_model

    def _run_and_measure(self, circuit: Circuit, n_samples: int) -> Measurements:
        braket_circuit = export_to_braket(circuit)
        if self.noise_model is not None:
            braket_circuit.apply_gate_noise(self.noise_model)

        result = self.device.run(braket_circuit, shots=n_samples).result()
        return Measurements.from_counts(result.measurement_counts)


def braket_local_runner(
    backend: Optional[str] = None,
    noise_model: Optional[Type[Noise]] = None
):
    if backend is None:
        backend = "braket_dm" if noise_model is not None else "braket_sv"
    if backend != "braket_dm" and noise_model is not None:
        raise ValueError(
            "Noisy simulations are supported only for density matrix backend"
        )
    device = LocalSimulator(backend=backend)
    return BraketRunner(device, noise_model)


def aws_runner(
    name: str = "SV1",
    noise_model: Type[Noise] = None,
    boto_session: Optional[Session] = None,
):
    aws_session = AwsSession(boto_session)
    arn = _get_arn(name, aws_session)
    device = AwsDevice(arn, aws_session)

    if noise_model is not None and device.type !=  AwsDeviceType.SIMULATOR:
        raise ValueError(
            f"QPU {name} cannot use noise model."
        )

    return BraketRunner(device, noise_model)
