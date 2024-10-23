# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long
"""
Step implementations for feature files.
"""
from logging import INFO, basicConfig, getLogger
from time import sleep

import pytest
from boto3 import client
from pytest_bdd import given, scenarios

from ...helpers.environment_variables import AWS_ACCOUNT_ID, AWS_REGION, WORKSPACE

SFN_ROLE_NAME = f"{WORKSPACE}-validate-relationships-iam-for-sfn"
SFN_POLICY_ARN = f"arn:aws:iam::{AWS_ACCOUNT_ID}:policy/{WORKSPACE}-validate-relationships-policy-invoke-lambda"
PDS_ACCESS_TOKEN_LAMBDA_NAME = f"{WORKSPACE}-pds_access_token"
API_GATEWAY_NAME = f"{WORKSPACE}-rest-api"
API_GATEWAY_STAGE_NAME = "default"

sfn = client("stepfunctions", region_name=AWS_REGION)
iam = client("iam", region_name=AWS_REGION)
lambda_client = client("lambda", region_name=AWS_REGION)
api_client = client("apigateway", region_name=AWS_REGION)

logger = getLogger(__name__)
basicConfig(level=INFO)


scenarios("../features/operation_outcome_internal_server_error.feature")


@pytest.fixture(scope="function")
def _restore_sfn_policy():
    """Fixture to restore the SFN policy after the test has run. Even if the test fails."""
    yield
    iam.attach_role_policy(RoleName=SFN_ROLE_NAME, PolicyArn=SFN_POLICY_ARN)


@pytest.fixture(scope="function")
def _restore_pds_api():
    """Fixture to restore the PDS API environment variables after the test has run. Even if the test fails."""
    response = lambda_client.get_function_configuration(
        FunctionName=PDS_ACCESS_TOKEN_LAMBDA_NAME
    )
    environment = response["Environment"]
    yield
    lambda_client.update_function_configuration(
        FunctionName=PDS_ACCESS_TOKEN_LAMBDA_NAME, Environment=environment
    )


@pytest.fixture(scope="function")
def _restore_api_gateway_related_person_response_templates():
    """Fixture to restore the api gateway response templates after the test has run. Even if the test fails."""

    logger.info(
        f"Retriving {API_GATEWAY_NAME} current related person response for later restore."
    )
    apis = api_client.get_rest_apis()
    api = [item for item in apis["items"] if item["name"] == API_GATEWAY_NAME][0]

    resources = api_client.get_resources(restApiId=api["id"])

    resource = [
        item
        for item in resources["items"]
        if (item.get("pathPart") and item["pathPart"] == "RelatedPerson")
    ][0]
    resource_id = resource["id"]

    # Preserve response until function call ends
    response = api_client.get_integration_response(
        restApiId=api["id"],
        resourceId=resource_id,
        httpMethod="GET",
        statusCode="200",
    )

    yield
    api_client.put_integration_response(
        restApiId=api["id"],
        resourceId=resource_id,
        httpMethod="GET",
        statusCode="200",
        responseTemplates=response["responseTemplates"],
    )

    deployment = api_client.create_deployment(
        restApiId=api["id"],
        stageName="default",
        description="Infrastructure tests deployment restored",
    )

    api_client.update_stage(
        restApiId=api["id"],
        stageName=API_GATEWAY_STAGE_NAME,
        patchOperations=[
            {"op": "replace", "path": "/deploymentId", "value": deployment["id"]}
        ],
    )
    sleep(3)  # Sleep a few seconds as the change is not instant
    logger.info("Reverted VRS RelatedPerson endpoint to return normal responses.")


@given("the VRS is in a failure mode")
def set_vrs_to_fail(_restore_sfn_policy):
    wait_for_rule = 60

    try:
        iam_response = iam.detach_role_policy(
            RoleName=SFN_ROLE_NAME, PolicyArn=SFN_POLICY_ARN
        )
        logger.info(
            "SFN Rule removed:%d", iam_response["ResponseMetadata"]["HTTPStatusCode"]
        )
    except iam.exceptions.NoSuchEntityException as error:
        logger.warning(str(error))

    logger.info("Allow a short period of time for changes to take effect.")
    for seconds in range(wait_for_rule, 0, -10):
        logger.info(f"Waiting for {seconds} seconds")
        sleep(10)


@given(
    "the VRS relationship lookup endpoint is in a 408 failure mode",
    target_fixture="lambda_environment",
)
def set_vrs_related_person_endpoint_to_fail(
    _restore_api_gateway_related_person_response_templates,
) -> dict:
    template_408 = {
        "application/json": """
                        #set($context.responseOverride.status = 408)
                        {
                            "Test":"Failure enabled"
                        }
                        """
    }

    apis = api_client.get_rest_apis()
    api = [item for item in apis["items"] if item["name"] == API_GATEWAY_NAME][0]

    resources = api_client.get_resources(restApiId=api["id"])

    resource = [
        item
        for item in resources["items"]
        if (item.get("pathPart") and item["pathPart"] == "RelatedPerson")
    ][0]
    resource_id = resource["id"]

    logger.info(
        f"Attempting to short-circuit {API_GATEWAY_NAME} to return 408 response."
    )
    api_client.put_integration_response(
        restApiId=api["id"],
        resourceId=resource_id,
        httpMethod="GET",
        statusCode="200",  # Overwrite the current 200 method response
        responseTemplates=template_408,
    )

    deployment = api_client.create_deployment(
        restApiId=api["id"],
        stageName="default",
        description="infrastructure failure test",
    )

    api_client.update_stage(
        restApiId=api["id"],
        stageName=API_GATEWAY_STAGE_NAME,
        patchOperations=[
            {"op": "replace", "path": "/deploymentId", "value": deployment["id"]}
        ],
    )
    sleep(3)  # Sleep a few seconds as the change is not instant
    logger.info(f"Successfully applied short-circuit to {API_GATEWAY_NAME}.")


@given("the PDS API is in a failure mode", target_fixture="lambda_environment")
def set_pds_api_to_fail(_restore_pds_api) -> dict:

    # Get existing environment variables
    response = lambda_client.get_function_configuration(
        FunctionName=PDS_ACCESS_TOKEN_LAMBDA_NAME
    )
    environment = response["Environment"]

    updated_environment = environment.copy()
    updated_environment["Variables"]["PDS_AUTH_URL"] = ""

    lambda_client.update_function_configuration(
        FunctionName=PDS_ACCESS_TOKEN_LAMBDA_NAME, Environment=updated_environment
    )

    return environment
