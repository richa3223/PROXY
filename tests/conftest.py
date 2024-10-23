"""
Helper fixtures used by both End to End API tests and component tests.

Based on https://stackoverflow.com/a/42156088
"""

import os
import re
import uuid
from json import dumps, loads
from logging import getLogger
from time import sleep
from urllib.parse import unquote

import boto3
import delayed_assert
import pytest
import requests
import yaml
import yaql
from openapi_core import Config, OpenAPI
from openapi_core.contrib.requests import (
    RequestsOpenAPIRequest,
    RequestsOpenAPIResponse,
)
from openapi_core.deserializing.media_types.util import json_loads
from openapi_core.templating.responses.exceptions import ResponseNotFound
from openapi_core.validation.response.exceptions import DataValidationError, InvalidData
from pytest_bdd import given, parsers, then, when
from requests import Response

from .helpers import Helpers, apigee_authentication
from .helpers.api import call_api, clear_optional_parameters
from .helpers.aws.dynamodb import DYNAMODB_TABLE_NAME
from .helpers.environment_variables import AWS_ACCOUNT_ID, AWS_REGION, WORKSPACE

# See NPA-2477 - Migrate poetry from lambdas and tests to single root level config
# pylint: disable=import-error
# pylint: disable=wrong-import-position

logger = getLogger(__name__)


class StepFunctionApiResponse:
    """
    Converts state machine dict response into api_response
    with optional fields to handle Step Function failure
    response.
    """

    status_code = None
    body = None
    error = None
    cause = None

    def __init__(self, state_machine, state_machine_response: dict):

        if "status" in state_machine_response.keys():
            if state_machine_response["status"] == "FAILED":
                self.error = state_machine_response["error"]
                self.cause = state_machine_response["cause"]

        if "output" in state_machine_response.keys():
            response_output = loads(state_machine_response["output"])
            logger.info(f"Step function output {state_machine}: {response_output}")
            self.status_code = response_output["statusCode"]

            self.body = response_output["body"]

    def json(self):
        """
        converts body to json
        """
        return self.body


def pytest_bdd_before_scenario():
    """
    Clear out optional parameters used in API requests
    """
    clear_optional_parameters()


def pytest_bdd_after_scenario():
    """
    Output delayed assertions at end of scenario
    """
    delayed_assert.assert_expectations()


@pytest.fixture(autouse=True)
def delay_pds_tests(request):
    """Delay PDS tests"""
    node = request.node
    if node.get_closest_marker("pds_api_call"):
        sleep(0.5)


@pytest.fixture
def helpers():
    """
    Pytest fixture wrapper for helper class
    """
    return Helpers


@pytest.fixture
def yaql_engine() -> yaql.factory.YaqlFactory:
    """Pytest fixture wrapper for"""
    return yaql.factory.YaqlFactory().create()


@pytest.fixture
def openapi() -> OpenAPI:
    """
    Returns the OpenAPI-Core object used to check
    exchanges with the API
    """

    def validate_token(value):
        """
        Deals with the `token` format extension
        in the API spec.
        """
        if value is not None:
            return True

        return False

    extra_format_validators = {
        "token": validate_token,
    }

    def fhir_json_deserializer(message, charset=""):
        """
        Ensure that the `application/fihr+json` mime
        type returns valid input for openapi-core
        """
        assert isinstance(message, bytes)
        return json_loads(message)

    extra_media_type_deserializers = {
        "application/fhir+json": fhir_json_deserializer,
    }

    config = Config(
        extra_format_validators=extra_format_validators,
        extra_media_type_deserializers=extra_media_type_deserializers,
    )

    branch = os.environ.get("API_SPEC_BRANCH", "master")

    schema_url = (
        "https://raw.githubusercontent.com/NHSDigital/"
        "validated-relationships-service-api/"
        f"{branch}/"
        "specification/validated-relationships-service-api.yaml"
    )
    raw_schema = requests.get(schema_url, timeout=10)
    raw_schema.raise_for_status()
    yaml_schema = yaml.safe_load(raw_schema.content)
    # See NPA-2478 - the `internal-dev` server is not included in the
    # published spec. We need to decide whether we want to add it or not.
    yaml_schema["servers"].append(
        {
            "url": (
                "https://internal-dev.api.service.nhs.uk/"
                "validated-relationships/FHIR/R4"
            )
        }
    )

    return OpenAPI.from_dict(yaml_schema, config=config)


@pytest.fixture(scope="function")
def _yield_generate_delete_dynamo_db_record():
    """Fixture to delete a dynamo db record."""
    reference_code = "test_" + str(uuid.uuid4())

    yield reference_code

    # Yield - Teardown Pattern - https://docs.pytest.org/en/stable/how-to/fixtures.html#yield-fixtures-recommended
    # Will cleanup the created record if the fixture is used
    client = boto3.client("dynamodb", region_name="eu-west-2")
    key = {"ReferenceCode": {"S": str(reference_code)}}
    rtn = client.delete_item(TableName=DYNAMODB_TABLE_NAME, Key=key)
    logger.info(f"AWS response to delete : {rtn}")
    logger.info(f"Item deleted from DynamoDB: {reference_code}")


# pylint: disable=line-too-long
# pylint: disable=missing-function-docstring
@given(
    parsers.parse("the client is authenticated with {identifier}"),
    target_fixture="headers",
)
def is_authenticated_with(
    _test_app_credentials, _jwt_keys, _keycloak_client_credentials, identifier
):
    if re.match("https://fhir.nhs.uk/Id/nhs-number", unquote(identifier)):
        identifier = unquote(identifier).split("|")[1]
    token_response = apigee_authentication.authenticate_client(
        _test_app_credentials,
        apigee_authentication.APIGEE_ENVIRONMENT,
        _jwt_keys,
        _keycloak_client_credentials,
        identifier,
    ).token_response
    assert "access_token" in token_response
    token = token_response["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    return headers


@given(
    parsers.parse("the X-Request-ID and X-Correlation-ID headers are set to UUIDs"),
    target_fixture="headers",
)
def set_spec_headers(headers):
    headers["X-Request-ID"] = str(uuid.uuid4())
    headers["X-Correlation-ID"] = str(uuid.uuid4())
    logger.info(f"Headers set to: {headers}")
    return headers


@then(parsers.parse("the Relationship Validation Service will return {status_code:d}"))
def check_response_status(api_response, status_code):
    delayed_assert.expect(
        api_response.status_code == status_code,
        (f"Expected {status_code} got {api_response.status_code}"),
    )


@then(parsers.parse("the step function will return {status_code:d}"))
def check_step_function_response_status(api_response, status_code):
    delayed_assert.expect(
        api_response.status_code == status_code,
        (f"Expected {status_code} got {api_response.status_code}"),
    )


@then(parsers.parse("the diagnostics {diagnostics} is present in the response"))
def check_response_diagnostics(api_response, diagnostics):
    response_body = api_response.json()
    actual_diagnostics = None
    try:
        actual_diagnostics = response_body["issue"][0]["diagnostics"]
    except KeyError as error:
        delayed_assert.expect(
            False, (f"{str(error)} not found in response {response_body}")
        )
    delayed_assert.expect(
        actual_diagnostics == diagnostics,
        f"The actual 'diagnostics' value: '{str(actual_diagnostics)}' did not match the expected 'diagnostics' value: {diagnostics}",
    )


@then(
    parsers.parse(
        "the system, version, severity and resourceType are correct in the response"
    )
)
def check_response_system_and_version(api_response):
    response_body = api_response.json()
    expected_url = (
        "https://fhir.nhs.uk/R4/CodeSystem/ValidatedRelationships-ErrorOrWarningCode"
    )
    expected_version = "1"
    expected_severity = "error"
    expected_resource_type = "OperationOutcome"

    actual_url = None
    actual_version = None
    actual_severity = None
    actual_resource_type = None

    try:
        actual_version = response_body["issue"][0]["details"]["coding"][0]["version"]
        actual_url = response_body["issue"][0]["details"]["coding"][0]["system"]
        actual_severity = response_body["issue"][0]["severity"]
    except KeyError as error:
        delayed_assert.expect(
            False, (f"{str(error)} not found in response {response_body}")
        )

    try:
        actual_resource_type = response_body["resourceType"]
    except KeyError as error:
        delayed_assert.expect(
            False, (f"{str(error)} not found in response {response_body}")
        )

    delayed_assert.expect(
        actual_url == expected_url,
        f"The actual 'system' value: '{str(actual_url)}' did not match the expected 'system' value: '{expected_url}'",
    )
    delayed_assert.expect(
        actual_version == expected_version,
        f"The actual 'version' value: '{str(actual_version)}' did not match the expected 'version' value: '{expected_version}'",
    )
    delayed_assert.expect(
        actual_severity == expected_severity,
        f"The actual 'severity' value: '{str(actual_severity)}' did not match the expected 'severity' value: '{expected_severity}'",
    )
    delayed_assert.expect(
        actual_resource_type == expected_resource_type,
        f"The actual 'resourceType' value: '{str(actual_resource_type)}' did not match the expected 'resourceType' value: '{expected_resource_type}'",
    )


@then(parsers.parse("the error code {error_code} is present in the response"))
def check_response_error_code(api_response, error_code):
    response_body = api_response.json()
    actual_error_code = None
    try:
        actual_error_code = response_body["issue"][0]["details"]["coding"][0]["code"]
    except KeyError as error:
        delayed_assert.expect(
            False, (f"{str(error)} not found in response {response_body}")
        )

    delayed_assert.expect(
        actual_error_code == error_code,
        f"The actual 'code' value: '{str(actual_error_code)}' did not match the expected 'code' value: '{error_code}'",
    )


@then(parsers.parse("the code {code} is present in the response"))
def check_response_code(api_response, code):
    response_body = api_response.json()
    actual_code = None
    try:
        actual_code = response_body["issue"][0]["code"]
    except KeyError as error:
        delayed_assert.expect(
            False, (f"{str(error)} not found in response {response_body}")
        )

    delayed_assert.expect(
        actual_code == code,
        f"The actual 'code' value: '{str(actual_code)}' did not match the expected 'code' value: '{code}'",
    )


@then(parsers.parse("the display {display} is present in the response"))
def check_response_display(api_response, display):
    response_body = api_response.json()
    actual_display = None
    try:
        actual_display = response_body["issue"][0]["details"]["coding"][0]["display"]
    except KeyError as error:
        delayed_assert.expect(
            False, (f"{str(error)} not found in response {response_body}")
        )
    delayed_assert.expect(
        actual_display == display,
        f"The actual 'display' value: '{str(actual_display)}' did not match the expected 'display' value: '{display}'",
    )


@when(
    parsers.parse("an identifier {identifier} is used to call {path}"),
    target_fixture="api_response",
)
def call_api_with_identifier(
    nhsd_apim_proxy_url, headers, path, identifier
) -> Response:
    if identifier == "empty value":
        parameters = {"identifier": ""}
    elif identifier == "missing key":
        parameters = {}
    else:
        parameters = {"identifier": unquote(identifier)}

    return call_api(nhsd_apim_proxy_url, unquote(path), headers, parameters)


@given(
    parsers.parse("a state machine input JSON:\n{input_json}"),
    target_fixture="input_body",
)
def a_state_machine_input_json(input_json: str) -> dict:
    input_body = loads(input_json)
    return input_body


@given(
    parsers.parse("the key {key} is set to {value}"),
    target_fixture="input_body",
)
def set_key_value(helpers, key: str, value: str, input_body: dict) -> dict:
    return helpers.parameterise_key_values(key, value, input_body)


@when(
    parsers.parse("the step function {state_machine} is called"),
    target_fixture="api_response",
)
def the_step_function_is_called(
    state_machine, input_body: dict
) -> StepFunctionApiResponse:
    logger.info(f"Input body -  {input_body}")
    json_string = dumps(input_body)
    logger.info(f"Input json body -  {json_string}")
    client = boto3.client("stepfunctions")
    state_machine_arn = (
        f"arn:aws:states:{AWS_REGION}:{AWS_ACCOUNT_ID}"
        f":stateMachine:{WORKSPACE}-{state_machine}"
    )
    logger.info(f"Invoking {state_machine} step function: {json_string}")
    state_machine_response = client.start_sync_execution(
        stateMachineArn=state_machine_arn, input=json_string
    )
    logger.info(f"Response received from {state_machine}: {state_machine_response}")
    api_response = StepFunctionApiResponse(state_machine, state_machine_response)
    return api_response


@when(
    parsers.parse("the standard step function {state_machine} is called"),
    target_fixture="api_response",
)
def the_standard_step_function_is_called(
    state_machine: str, input_body: dict
) -> StepFunctionApiResponse:
    # Standard step functions cannot be invoked with
    # the call client.start_sync_execution()
    # So, this method mimics the_step_function_is_called method
    # In addition, the returned response differs
    logger.info(f"Input body -  {input_body}")
    json_string = dumps(input_body)
    logger.info(f"Input json body -  {json_string}")
    client = boto3.client("stepfunctions")
    state_machine_arn = (
        f"arn:aws:states:{AWS_REGION}:{AWS_ACCOUNT_ID}"
        f":stateMachine:{WORKSPACE.lower()}-{state_machine}"
    )
    logger.info(f"Invoking {state_machine} step function: {json_string}")
    runname = f"Test-{str(uuid.uuid4())}"
    state_machine_response = client.start_execution(
        stateMachineArn=state_machine_arn, input=json_string, name=runname
    )
    logger.info(f"Response received from {state_machine}: {state_machine_response}")
    # Rewrap the result to mimic other step functions
    # AWS start date is not seraliseable
    # And we do not need the value
    state_machine_response["startDate"] = ""
    resp = {
        "output": dumps(
            {
                "statusCode": state_machine_response["ResponseMetadata"][
                    "HTTPStatusCode"
                ],
                "body": state_machine_response,
            }
        )
    }

    logger.info(f"mocked resp {resp}")
    api_response = StepFunctionApiResponse(state_machine, resp)
    return api_response


@then("the response will be JSON")
def check_response_content(api_response: Response):
    assert api_response.json(), (
        "The api response body format returned was not in a JSON format."
        f"Here is the response body content: '{api_response.json()}'"
    )


@then(parsers.parse("the link to self matches the request URL"))
def link_to_self_matches_request_url(api_response):
    response_body = api_response.json()
    expected_url = api_response.request.url
    check_self_url(expected_url, response_body)


@then(parsers.parse("the link to self matches originalRequestUrl"))
def link_to_self_matches_original_request_url(input_body: dict, api_response):
    response_body = api_response.json()
    expected_url = input_body["originalRequestUrl"]
    check_self_url(expected_url, response_body)


def check_self_url(expected_url: str, response_body):
    expected_relation = "self"
    actual_relation = response_body["link"][0]["relation"]
    actual_url = response_body["link"][0]["url"]
    assert actual_relation == expected_relation, (
        f"The actual 'link.relation' value: '{str(actual_relation)}' ",
        "did not match the expected 'link.relation' value: ",
        f"'{expected_relation}'",
    )
    assert actual_url == expected_url, (
        f"The actual 'link.url' value: '{str(actual_url)}' did not match ",
        f"the expected 'link.relation' value: '{expected_url}'",
    )


@then(parsers.parse("the total number of records is '{value:d}'"))
def _(value: int, api_response: Response) -> None:
    response_dict = api_response.json()
    total = response_dict["total"]
    assert total == value, f"Expected {value} but got {total}"


@then(
    parsers.parse("the total number of records is {total:d} with a type of searchset")
)
def check_total_number_of_records(api_response: Response, total):
    response_body = api_response.json()
    assert response_body["type"] == "searchset"
    delayed_assert.expect(response_body["total"] == total)


@then(
    parsers.parse(
        "the patient_identifier {patient_identifier} is returned in the patient record {index}"
    )
)
def patient_identifier_record_is_returned_at_index(
    helpers, api_response: Response, patient_identifier, index
):
    patient_identifier = helpers.remove_url_prefix(patient_identifier)
    ids = [int(x) for x in patient_identifier.split(",")]
    indices = [int(x) for x in index.split(",")]

    response_body = api_response.json()
    for i, patient_id in zip(indices, ids):
        actual_patient_identifier = response_body["entry"][i]["resource"]["patient"][
            "identifier"
        ]["value"]
        assert actual_patient_identifier == str(patient_id), (
            f"The actual 'patient.identifier' value: '{str(actual_patient_identifier)}'",
            f"did not match the expected 'identifier' value: '{str(patient_id)}'",
        )


@then(
    parsers.parse(
        "the identifier {identifier} and relationship_id {relationship_id} are returned in the related person {index}"
    )
)
def check_correct_identifier_is_returned(
    helpers, api_response: Response, identifier, relationship_id, index
):
    identifier = helpers.remove_url_prefix(identifier)
    indices = [int(x) for x in index.split(",")]

    rel_ids = list(relationship_id.split(","))

    response_body = api_response.json()
    for pointer in indices:
        actual_identifier = response_body["entry"][pointer]["resource"]["identifier"][
            0
        ]["value"]
        assert actual_identifier == str(identifier), (
            f"The actual 'identifier' value: '{str(actual_identifier)}'",
            f"did not match the expected 'identifier' value: '{str(identifier)}'",
        )
    for i, rel_id in zip(indices, rel_ids):
        actual_rel_id = response_body["entry"][i]["resource"]["id"]
        assert actual_rel_id == rel_id, (
            f"The actual relationship 'id' value: '{str(actual_rel_id)}' did not",
            f"match the expected relationship 'id' value: '{str(rel_id)}'",
        )


@then(
    parsers.parse(
        "the '{resource_type}' relationship.coding array contains only a MTH code entry"
    )
)
def check_related_person_relationship_coding_in_response(
    resource_type: str,
    api_response: Response,
    yaql_engine: yaql.factory.YaqlFactory,
):
    # pylint: disable=too-many-locals
    response_body = api_response.json()
    expected_code = "MTH"
    expected_display = "mother"
    expected_system = "http://terminology.hl7.org/CodeSystem/v3-RoleCode"
    expected_number_of_objects = 1
    actual_code = None
    actual_display = None
    actual_system = None
    actual_number_of_objects = None

    resource = yaql_engine(f"$.entry.where($.resource.resourceType = {resource_type})")
    entries = resource.evaluate(data=api_response.json())

    for entry in entries:
        try:
            actual_code = entry["resource"]["relationship"][0]["coding"][0]["code"]
            actual_display = entry["resource"]["relationship"][0]["coding"][0][
                "display"
            ]
            actual_system = entry["resource"]["relationship"][0]["coding"][0]["system"]
            actual_number_of_objects = len(
                entry["resource"]["relationship"][0]["coding"]
            )
        except KeyError as error:
            delayed_assert.expect(
                False, (f"{str(error)} not found in response {response_body}")
            )

        delayed_assert.expect(
            actual_code == expected_code,
            f"The actual relationship 'code' value: '{str(actual_code)}' did not match the expected relationship 'code' value: '{expected_code}'",
        )
        delayed_assert.expect(
            actual_display == expected_display,
            f"The actual relationship 'display' value: '{str(actual_display)}' did not match the expected relationship 'display' value: '{expected_display}'",
        )
        delayed_assert.expect(
            actual_system == expected_system,
            f"The actual relationship 'system' value: '{str(actual_system)}' did not match the expected relationship 'system' value: '{expected_system}'",
        )
        delayed_assert.expect(
            actual_number_of_objects == expected_number_of_objects,
            f"The actual number of relationship coding objects: '{str(actual_number_of_objects)}' did not match the expected number of relationship coding objects: '{str(expected_number_of_objects)}'",
        )


@then(
    parsers.parse(
        "the entry in the response will contain {num:d} resources of resourceType '{resource_type}'"
    ),
    target_fixture="entries",
)
def check_response_resource_type_content(
    num: int,
    resource_type: str,
    api_response: Response,
    yaql_engine: yaql.factory.YaqlFactory,
) -> list[dict]:
    expression = yaql_engine(
        f"$.entry.where($.resource.resourceType = {resource_type})"
    )
    entries = expression.evaluate(data=api_response.json())
    assert len(entries) == num, f"Expected {num} but got {len(entries)}"
    return entries


@then(parsers.parse("for each of the {num:d} entries '{path}' is '{value}'"))
def check_resource_attribute(
    num: int,
    path: str,
    value: str,
    entries: list[dict],
    yaql_engine: yaql.factory.YaqlFactory,
):
    expression = yaql_engine(f'$.where($.{path} = "{value}")')
    matches = expression.evaluate(data=entries)
    assert len(matches) == num, f"Expected {num} but got {len(matches)}"


# pylint: disable=too-many-arguments
@then(parsers.parse("the '{resource_type}' entries '{path}' matches {value}"))
def check_value(
    helpers,
    resource_type: str,
    path: str,
    value: str,
    entries: list[dict],
    api_response: Response,
    yaql_engine: yaql.factory.YaqlFactory,
):
    if path == "resource.identifier[0].value" and resource_type == "RelatedPerson":
        resource = yaql_engine(
            f"$.entry.where($.resource.resourceType = {resource_type})"
        )
        entries = resource.evaluate(data=api_response.json())
        value = helpers.remove_url_prefix(value)
        expression = yaql_engine(f"$.where($.{path} = '{value}')")
        matches = expression.evaluate(data=entries)
        assert len(matches) == len(entries), f"No entry found for {value}"
    else:
        resource = yaql_engine(
            f"$.entry.where($.resource.resourceType = {resource_type})"
        )
        entries = resource.evaluate(data=api_response.json())
        ids = value.split(",")
        for value_id in ids:
            expression = yaql_engine(f'$.where($.{path} = "{value_id}")')
            matches = expression.evaluate(data=entries)
            assert len(matches) == 1, f"No entry found for {value_id}"


@given("the Relationship Validation Service API is available")
def relationship_validation_service_is_available(nhsd_apim_proxy_url):
    resp = call_api(nhsd_apim_proxy_url, "/_ping", {}, {})
    assert resp.status_code == 200


@when(
    parsers.parse(
        "the client calls {path} with identifier {identifier}"
        " and patient:identifier {patient_identifier}"
    ),
    target_fixture="api_response",
)
# pylint: disable=too-many-arguments
def call_api_with_identifier_and_patient_identifier(
    nhsd_apim_proxy_url,
    headers,
    path,
    identifier,
    patient_identifier,
):
    if identifier == "empty value":
        parameters = {"identifier": "", "patient:identifier": patient_identifier}
    elif identifier == "missing key":
        parameters = {}
    elif identifier == "only patient identifier":
        parameters = {"patient:identifier": patient_identifier}
    else:
        parameters = {
            "identifier": unquote(identifier),
            "patient:identifier": unquote(patient_identifier),
        }

    return call_api(nhsd_apim_proxy_url, unquote(path), headers, parameters)


@then("the request will match the API Spec")
def check_request_against_spec(api_response: Response, openapi):
    """
    Check that we are making API compliant requests. This is testing our tests rather
    than the Validated Relationships Service itself. For example if we are not passing
    in a required parameter such as `X-Request-ID` then this step will fail.
    """
    openapi_request = RequestsOpenAPIRequest(api_response.request)
    openapi.validate_request(openapi_request)


@then("the response will match the API Spec")
def check_response_against_spec(api_response: Response, openapi):
    """
    Check that the Validated Relationships Service is returning an API compliant response.

    """
    openapi_response = RequestsOpenAPIResponse(api_response)
    openapi_request = RequestsOpenAPIRequest(api_response.request)
    try:
        openapi.validate_response(openapi_request, openapi_response)

    # This error is hidden by the previous DataValidationError
    except InvalidData as error:
        delayed_assert.expect(False, str(error))

    except DataValidationError as error:
        delayed_assert.expect(False, str(error))

    except ResponseNotFound as error:
        delayed_assert.expect(False, str(error))
