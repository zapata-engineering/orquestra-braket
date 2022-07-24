# orquestra-braket

## What is it?

`orquestra-braket` is a [Zapata](https://www.zapatacomputing.com) library holding modules for integrating [Amazon Braket supported devices](https://docs.aws.amazon.com/braket/latest/developerguide/braket-devices.html) with [Orquestra](https://www.zapatacomputing.com/orquestra/). This version supports Braket's `LocalSimlator()` and on-demand simulators.

## Installation

Even though it's intended to be used with Orquestra, `orquestra-braket` can be also used as a Python module.
To install it, make to install `orquestra-quantum` first. Then you just need to run `pip install .` from the main directory.

## Overview

`orquestra-braket` is a Python module that exposes Braket's local and on-demand simulators as an [`orquestra`](https://github.com/zapatacomputing/orquestra-quantum/blob/main/src/orquestra/quantum/api/backend.py) `QuantumSimulator`. They can be imported with:

```
from orquestra.integrations.braket.simulator import BraketLocalSimulator
from orquestra.integrations.braket.simulator import BraketOnDemandSimulator
```

In addition, it interfaces with the noise models and provides converters that allow switching between `braket` circuits and those of `orquestra`.

The module can be used directly in Python or in an [Orquestra](https://www.orquestra.io) workflow.
For more details, see the [Orquestra Core docs](https://zapatacomputing.github.io/orquestra-core/index.html).

For more information regarding Orquestra and resources, please refer to the [Orquestra documentation](https://www.orquestra.io/docs).

## On Demand Simulator

In order to use Braket's `on-demand simulator`, a `boto.Session` must be created using AWS credentials. See [Boto Session](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/core/session.html) for information on creating creating a session. It highly recommended that credentials are configured in the local [AWS CLI profile](https://docs.aws.amazon.com/braket/latest/developerguide/braket-using-boto3-profiles-step-2.html). Following is an example of working with `BraketOnDemandSimulator` using credentials stored in AWS CLI profile:

```
from orquestra.integrations.braket.simulator import BraketOnDemandSimulator

from braket.aws import AwsSession, AwsDevice
from boto3 import Session

# Insert CLI profile name here
boto_session = Session(profile_name=`profile`, region_name='us-east-1')
simulator_name = "SV1"
noise_model = None
simulator = BraketOnDemandSimulator(simulator_name, boto_session, noise_model)

```

The outcome of the `BraketOnDemandSimulator` will not be saved in the S3.

## Development and contribution

You can find the development guidelines in the [`orquestra-core` repository](https://github.com/zapatacomputing/orquestra-core/blob/main/CONTRIBUTING.md).
