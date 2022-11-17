################################################################################
# © Copyright 2021-2022 Zapata Computing Inc.
################################################################################


from braket.aws import AwsDevice


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
