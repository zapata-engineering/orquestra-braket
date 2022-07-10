################################################################################
# © Copyright 2021-2022 Zapata Computing Inc.
################################################################################

from typing import Callable, Dict

from braket.circuits import Circuit as BraketCircuit
from braket.circuits.gate import Gate as BraketGate
from braket.circuits.instruction import Instruction
from orquestra.quantum.circuits import Circuit, I


def export_to_braket(circuit: Circuit) -> BraketCircuit:
    """Converts the circuit to a Braket Circuit object.

    Args:
      circuit : the circuit to convert

    Returns:
      BraketCircuit
    """

    for i in range(circuit.n_qubits):
        circuit += I(i)

    gates = [_to_braket_gate(operation) for operation in circuit.operations]
    return BraketCircuit(gates)


def _to_braket_gate(operation):

    if operation.gate.name in NON_PARAMETERIZED_BRAKET_GATES.keys():
        return Instruction(
            NON_PARAMETERIZED_BRAKET_GATES[operation.gate.name](),
            [qubit for qubit in operation.qubit_indices],
        )
    elif operation.gate.name in PARAMETERIZED_BRAKET_GATES.keys():
        return Instruction(
            PARAMETERIZED_BRAKET_GATES[operation.gate.name](operation.params[0]),
            [qubit for qubit in operation.qubit_indices],
        )
    else:
        raise RuntimeError(
            "Gate: {} is not supported in Braket Circuits".format(operation.gate.name)
        )


NON_PARAMETERIZED_BRAKET_GATES: Dict[str, Callable] = {
    "I": BraketGate.I,
    "X": BraketGate.X,
    "Y": BraketGate.Y,
    "Z": BraketGate.Z,
    "H": BraketGate.H,
    "S": BraketGate.S,
    "T": BraketGate.T,
    "CZ": BraketGate.CZ,
    "CNOT": BraketGate.CNot,
    "ISWAP": BraketGate.ISwap,
    "SWAP": BraketGate.Swap,
}

PARAMETERIZED_BRAKET_GATES: Dict[str, Callable] = {
    "XX": BraketGate.XX,
    "XY": BraketGate.XY,
    "YY": BraketGate.YY,
    "ZZ": BraketGate.ZZ,
    "PHASE": BraketGate.PhaseShift,
    "RX": BraketGate.Rx,
    "RY": BraketGate.Ry,
    "RZ": BraketGate.Rz,
    "CPHASE": BraketGate.CPhaseShift,
}
