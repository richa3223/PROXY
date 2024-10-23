"""This module contains pytest fixtures that can be used across all lambda tests."""

import logging
import os
from dataclasses import dataclass

import pytest
from aws_lambda_powertools.utilities.typing import LambdaContext
from spine_aws_common.log.log_helper import LogHelper
from spine_aws_common.logger import Logger

from lambdas.utils.logging.logger import initialise_logger


@pytest.fixture(name="log_helper")
def log_helper_fixture():
    """Capture the stdout for the tests."""
    logging.disable(logging.CRITICAL)
    log_helper = LogHelper()
    log_helper.set_stdout_capture()
    return log_helper


@pytest.fixture(name="logger")
def logger_fixture():
    """Set up the logger for the tests."""
    path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "utils/logging/config/logbase.cfg"
    )
    logger = Logger(log_base=path)
    yield logger
    logging.disable(logging.NOTSET)


@pytest.fixture(autouse=True)
def initialise_logging(logger):
    """Initialise the logger for the tests."""
    initialise_logger(logger)


@pytest.fixture()
def lambda_context() -> LambdaContext:
    @dataclass
    class LambdaContext:
        """Mock LambdaContext - All dummy values."""

        function_name: str = "function-name"
        memory_limit_in_mb: int = 128
        invoked_function_arn: str = (
            "arn:aws:lambda:eu-west-1:000000000:function:function-name"
        )
        aws_request_id: str = "ffffffff-ffff-ffff-ffff-ffffffffffff"

    return LambdaContext()
