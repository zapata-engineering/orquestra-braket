# orquestra-braket

## What is it?

`orquestra-braket` is a [Zapata](https://www.zapatacomputing.com) library holding modules for integrating [Amazon Braket supported devices](https://docs.aws.amazon.com/braket/latest/developerguide/braket-devices.html) with [Orquestra](https://www.zapatacomputing.com/orquestra/). This version only supports Braket's `LocalSimlator()`.

## Installation

Even though it's intended to be used with Orquestra, `orquestra-braket` can be also used as a Python module.
To install it, make to install `orquestra-quantum` first. Then you just need to run `pip install .` from the main directory.

## Overview

`orquestra-braket` is a Python module that exposes Braket's local simulators as an [`orquestra`](https://github.com/zapatacomputing/orquestra-quantum/blob/main/src/orquestra/quantum/api/backend.py) `QuantumSimulator`. It can be imported with:

```
from orquestra.itegrations.braket.simulator import BraketLocalSimulator
```

In addition, it interfaces with the noise models and provides converters that allow switching between `braket` circuits and those of `orquestra`.

The module can be used directly in Python or in an [Orquestra](https://www.orquestra.io) workflow.
For more details, see the [Orquestra Core docs](https://zapatacomputing.github.io/orquestra-core/index.html).

For more information regarding Orquestra and resources, please refer to the [Orquestra documentation](https://www.orquestra.io/docs).

## Development and contribution

You can find the development guidelines in the [`orquestra-quantum` repository](https://github.com/zapatacomputing/orquestra-quantum).
