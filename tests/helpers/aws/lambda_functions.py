"""
Lambda test helper functions
"""

from logging import getLogger
from time import sleep

from boto3 import Session
from botocore.exceptions import ClientError

from ..environment_variables import AWS_REGION

logger = getLogger(__name__)


def get_lambda_environment_variables(function_name):
    """
    Get Lambda environment variables
    """
    session = Session(region_name=AWS_REGION)
    lambda_client = session.client("lambda")
    response = lambda_client.get_function_configuration(FunctionName=function_name)
    environment_variables = response["Environment"]["Variables"]
    return environment_variables


def set_lambda_environment_variables(function_name, variables) -> None:
    """
    Set Lambda environment variables
    """

    session = Session(region_name=AWS_REGION)
    lambda_client = session.client("lambda")

    done = False
    while not done:
        try:
            lambda_client.update_function_configuration(
                FunctionName=function_name, Environment={"Variables": variables}
            )
            done = True
        except ClientError as error:
            if "ResourceConflictException" in str(error):
                logger.info("Waiting for changes to propagate")
                sleep(30)

    ready = False
    while not ready:
        response = lambda_client.get_function_configuration(FunctionName=function_name)
        if response["Environment"]["Variables"] == variables:
            ready = True
            sleep(10)  # Wait for change to propogate - required even after
            # get_function_configuration reports that they have
            logger.info("Waiting for changes to propagate")
        else:
            logger.info("Waiting for changes to propagate")
            sleep(30)
