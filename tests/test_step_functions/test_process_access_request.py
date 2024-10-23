from json import load
from logging import getLogger
from time import sleep

import boto3
from pytest_bdd import given, parsers, scenarios, then, when
from requests import Response

from ..helpers.aws.dynamodb import (
    DYNAMODB_TABLE_NAME,
    TTL,
    StoreAccessRequest,
    put_item,
    serialize_dict,
)

logger = getLogger(__name__)
scenarios(
    "./features/process_access_request/1_valid_access_request.feature",
)


@given(
    parsers.parse("a create access request is created using {json_file}"),
    target_fixture="input_body",
)
def dynamo_db_record_is_created(
    input_body: dict, json_file: str, _yield_generate_delete_dynamo_db_record: str
):
    reference_code = _yield_generate_delete_dynamo_db_record

    logger.info(f"Creating dynamo db record with reference code {reference_code}")
    with open(
        f"test_step_functions/features/process_access_request/data/{json_file}",
        encoding="utf-8",
    ) as f:
        data = load(f)

    # Extract proxy NHS number
    proxy_details = next(
        item for item in data["item"] if item["linkId"] == "proxy_details"
    )
    proxy_nhs_number = next(
        answer["valueString"]
        for item in proxy_details["item"]
        if item["linkId"] == "nhs_number"
        for answer in item["answer"]
    )

    # Extract patient NHS number
    patient_details = next(
        item for item in data["item"] if item["linkId"] == "patient_details"
    )
    patient_nhs_number = next(
        answer["valueString"]
        for item in patient_details["item"]
        if item["linkId"] == "nhs_number"
        for answer in item["answer"]
    )

    request = StoreAccessRequest(
        ReferenceCode=reference_code,
        ProxyNHSNumber=proxy_nhs_number,
        PatientNHSNumber=patient_nhs_number,
        QuestionnaireData=data,
        ApplicationStatus="ACCESS_REQUEST_CREATED",
        TTL=TTL,
    )

    # Store record in Dynamo DB.
    # Implementing here rather than using the library
    # As the logging methods are different and raise errors at runtime
    logger.info(f"Working with dynamo db table : {DYNAMODB_TABLE_NAME}")
    put_item(serialize_dict(request.to_dict()))

    # Preserve the reference code for later use
    input_body["detail"]["referenceCode"] = reference_code

    return input_body


@then(
    parsers.parse(
        "the validate-relationships-state-machine step function {has_been_run}"
    ),
    target_fixture="api_response",
)
def request_step_function_has_been_run(api_response: Response, has_been_run: str):
    # For step functions there are limited options on how list executed operations
    # For normal step functions see - client.describe_execution()
    # - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/stepfunctions/client/describe_execution.html
    # For express functions its not possible, hence using X-Ray
    # Using X-Ray to list executed services using the xray trace id
    # The trace id is provided from the execution request
    client = boto3.client("xray")
    traceid = api_response.body["execution"]["traceHeader"]
    traceid = traceid[traceid.index("=") + 1 : traceid.index(";")]
    logger.info(f"Searching for trace {traceid}")
    result = client.get_trace_graph(TraceIds=[traceid])
    status_code = result["ResponseMetadata"]["HTTPStatusCode"]
    logger.info(f"Retrieved trace information - {status_code}")

    expected = has_been_run == "has been run"
    token = False
    validation = False
    # X-Ray does not clarify if the step function was invokved
    # However, we can check if the relvant lambdas were invoked
    # So, checking the first xxx_verify_parameters
    # and the last xxx_process_validation_result have been run
    for service in result["Services"]:
        if service["Name"].endswith("verify_parameters"):
            token = True
        if service["Name"].endswith("process_validation_result"):
            validation = True

    assert (
        token == expected and validation == expected
    ), f"Expected {expected} but got {token} and {validation}"

    return api_response


@then(
    parsers.parse("the dynamodb record will have a status of {status}"),
    target_fixture="input_body",
)
def dynamodb_record_will_have_expected_status(status: str, input_body: dict):

    # Using the reference code from the request to a do a lookup
    reference_code = input_body["detail"]["referenceCode"]
    client = boto3.client("dynamodb", region_name="eu-west-2")
    key = {"ReferenceCode": {"S": str(reference_code)}}
    rtn = client.get_item(TableName=DYNAMODB_TABLE_NAME, Key=key)
    logger.info(f"Item retrieved from DynamoDB: {reference_code}")

    # Confirm the status matches expected value
    # ["S"] is needed as DynamoDB transforms the stored data
    assert rtn["Item"]["ApplicationStatus"]["S"] == status
    return input_body


@then(
    parsers.parse("the step function will succeed"),
    target_fixture="api_response",
)
def request_step_function_operation_succeeded(api_response: Response):
    status = api_response.body["execution"]["status"]
    logger.info(f"Execution status: {status}")
    assert status == "SUCCEEDED"
    return api_response


@then(
    parsers.parse('the step function will fail with cause "{expected_cause}"'),
    target_fixture="api_response",
)
def request_step_function_operation_failed(expected_cause: str, api_response: Response):
    status = api_response.body["execution"]["status"]
    cause = api_response.body["execution"]["cause"]
    logger.info(f"Execution status: {status}")
    logger.info(f"Execution status: {cause}")
    assert status == "FAILED"
    assert cause == expected_cause
    return api_response


@when(
    parsers.parse("the test will wait for step function to complete"),
    target_fixture="api_response",
)
def wait_for_step_function_to_complete(api_response: Response):
    # Check if the step-function status is 'RUNNING'
    # Sleep until it becomes something else
    # Does not indicate success
    status = "RUNNING"
    while status == "RUNNING":
        arn = api_response.body["executionArn"]
        logger.info(f"Requesting information on execution arn : {arn}")
        client = boto3.client("stepfunctions", region_name="eu-west-2")
        details = client.describe_execution(executionArn=arn)
        status = details["status"]
        if status == "RUNNING":
            logger.info(f"Step function execution {arn} is still running, sleeping...")
            sleep(5)

    logger.info(f"Execution result: {details}")
    api_response.body["execution"] = details
    logger.info("Step function is finished running.")
    return api_response
