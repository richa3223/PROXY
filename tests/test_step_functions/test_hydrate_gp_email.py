# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long
"""
Step definitions for hydrate GP email
"""

from json import dumps, load, loads
from logging import getLogger

import pytest
from boto3 import client
from pytest_bdd import given, parsers, scenarios, then

from ..helpers.aws.dynamodb import (
    DYNAMODB_TABLE_NAME,
    TTL,
    AccessRequestReadyForAuthorisation,
    deserialize_data,
    put_item,
    serialize_dict,
)
from ..helpers.aws.lambda_functions import (
    get_lambda_environment_variables,
    set_lambda_environment_variables,
)
from ..helpers.environment_variables import AWS_REGION, ENVIRONMENT, WORKSPACE

logger = getLogger(__name__)
scenarios(
    "./features/hydrate_gp_email_template/1_hydrate_email.feature",
)

HYDRATED_EMAIL_TEMPORARY_STORAGE_BUCKET = (
    f"{WORKSPACE}-{ENVIRONMENT}-hydrated-email-temporary-storage-bucket"
)


@given(
    parsers.parse(
        "an access request ready for authorisation record is created using {json_file}"
    ),
    target_fixture="input_body",
)
def dynamo_db_record_is_created(
    input_body: dict, json_file: str, _yield_generate_delete_dynamo_db_record: str
):
    def load_file(json_file: str) -> dict:
        with open(
            f"test_step_functions/features/hydrate_gp_email_template/data/{json_file}",
            encoding="utf-8",
        ) as f:
            data = load(f)
        return data

    reference_code = _yield_generate_delete_dynamo_db_record

    logger.info(f"Creating dynamo db record with reference code {reference_code}")
    data = load_file(json_file)
    patient_pds = load_file("patient_pds_lookup.json")
    proxy_pds = load_file("proxy_pds_lookup.json")

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

    request = AccessRequestReadyForAuthorisation(
        ReferenceCode=reference_code,
        ProxyNHSNumber=proxy_nhs_number,
        PatientNHSNumber=patient_nhs_number,
        QuestionnaireData=data,
        ApplicationStatus="ACCESS_REQUEST_READY_FOR_AUTHORISATION",
        ProxyPDSPatientRecord=dumps(proxy_pds),
        PatientPDSPatientRecord=dumps(patient_pds),
        TTL=TTL,
    )

    # Store record in Dynamo DB.
    logger.info(f"Working with dynamo db table : {DYNAMODB_TABLE_NAME}")
    put_item(serialize_dict(request.to_dict()))

    # Preserve the reference code for later use
    input_body["detail"]["referenceCode"] = reference_code

    return input_body


@then(
    "the dynamodb record is updated to GP_AUTHORISATION_REQUEST_CREATED",
    target_fixture="s3_key",
)
def dynamodb_record_is_updated_to_gp_authorisation_request_created(
    input_body: dict,
) -> str:
    reference_code = input_body["detail"]["referenceCode"]
    dynamodb_client = client("dynamodb", region_name=AWS_REGION)
    key = {"ReferenceCode": {"S": str(reference_code)}}
    rtn = dynamodb_client.get_item(TableName=DYNAMODB_TABLE_NAME, Key=key)
    dynamodb_record = deserialize_data(rtn["Item"])
    logger.info(f"DynamoDB record: {dynamodb_record}")
    assert (
        dynamodb_record["ApplicationStatus"] == "GP_AUTHORISATION_REQUEST_CREATED"
    ), "Application status not updated to GP_AUTHORISATION_REQUEST_CREATED"
    assert (
        len(dynamodb_record["GPEmailAddresses"]) == 1
    ), "Email address not found in dynamodb"
    assert isinstance(dynamodb_record["S3Key"], str), "S3 key not found in dynamodb"
    return dynamodb_record["S3Key"]


@then("the hydrated email template is is saved to s3")
def hydrated_email_template_is_saved_to_s3(input_body: dict, s3_key: str) -> None:
    reference_code = input_body["detail"]["referenceCode"]
    s3_client = client("s3", region_name=AWS_REGION)
    rtn = s3_client.get_object(
        Bucket=HYDRATED_EMAIL_TEMPORARY_STORAGE_BUCKET, Key=s3_key
    )
    logger.info(f"S3 object retrieved: {rtn}")
    assert rtn["ResponseMetadata"]["HTTPStatusCode"] == 200, "S3 object not found"
    json_data = rtn["Body"].read().decode("utf-8")
    assert json_data == dumps(
        {
            "email_subject": "Validate Relationship Service",
            "email_body": f'<!doctype html><html><head> <title>Validated Relationship Service</title> <meta name="description" content="VRS Email Template"></head><body> The reference code {reference_code} and odscode is A20047</body></html>',
        }
    ), "Generated Email not as expected"


@pytest.fixture
def _hide_show_email_template_bucket():
    tmp_bucket_name = "undefined"
    function_name = f"{WORKSPACE}-get_email_template"

    environment_variables = get_lambda_environment_variables(function_name)
    current_bucket_name = environment_variables["EMAIL_TEMPLATE_BUCKET"]
    environment_variables["EMAIL_TEMPLATE_BUCKET"] = tmp_bucket_name
    set_lambda_environment_variables(function_name, environment_variables)

    yield

    environment_variables = get_lambda_environment_variables(function_name)
    environment_variables["EMAIL_TEMPLATE_BUCKET"] = current_bucket_name
    set_lambda_environment_variables(function_name, environment_variables)


@given("the email template does not exist")
def email_template_does_not_exist(_hide_show_email_template_bucket) -> None:
    pass


@then("email hydration will fail")
def email_hydration_fail(api_response) -> None:
    logger.warning(api_response.error)
    logger.warning(api_response.cause)


@given("the ODS code does not exist")
def ods_code_missing(input_body) -> None:
    reference_code = input_body["detail"]["referenceCode"]
    dynamodb_client = client("dynamodb", region_name=AWS_REGION)
    key = {"ReferenceCode": {"S": str(reference_code)}}
    rtn = dynamodb_client.get_item(TableName=DYNAMODB_TABLE_NAME, Key=key)
    dynamodb_record = deserialize_data(rtn["Item"])
    pds_record = loads(dynamodb_record["ProxyPDSPatientRecord"])
    pds_record["generalPractitioner"][0]["identifier"]["value"] = "undefined"
    dynamodb_record["ProxyPDSPatientRecord"] = dumps(pds_record)
    serialized_data = serialize_dict(dynamodb_record)
    rtn = dynamodb_client.put_item(
        TableName=DYNAMODB_TABLE_NAME,
        Item=serialized_data,
    )


@given(parsers.parse("a {field} provided by {source} is {missing}"))
def field_missing(field, source, missing) -> None:
    logger.info(f"{field} {source} {missing}")


@then(parsers.parse("in the hydrated email the {field} will appear as {unknown}"))
def field_replacement(field, unknown) -> None:
    logger.info(f"{field} {unknown}")
