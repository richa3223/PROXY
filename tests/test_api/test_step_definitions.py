# pylint: disable=missing-function-docstring
# pylint: disable=line-too-long
"""
Step implementations for feature files.
"""
import re
from copy import deepcopy
from json import loads
from logging import INFO, basicConfig, getLogger
from urllib.parse import unquote

import delayed_assert
import jwt
import yaql
from pytest_bdd import given, parsers, scenarios, then, when
from requests import Response

from ..conftest import Helpers
from ..helpers import apigee_authentication
from ..helpers.api import call_api, set_optional_parameter

logger = getLogger(__name__)
basicConfig(level=INFO)

scenarios(
    "./features/RelatedPerson/1_valid_relationships.feature",
    "./features/RelatedPerson/2_valid_relationships_include_parameter.feature",
    "./features/RelatedPerson/3_invalid_relationships.feature",
    "./features/RelatedPerson/4_operation_outcomes.feature",
    "./features/RelatedPerson/5_oauth.feature",
    "./features/QuestionnaireResponse/1_questionnaire_response_exchange.feature",
    "./features/QuestionnaireResponse/2_operation_outcomes.feature",
    "./features/QuestionnaireResponse/3_oauth.feature",
)


@given(
    parsers.parse("the header {header_key} is set to {header_value}"),
    target_fixture="headers",
)
def set_header(helpers: Helpers, header_key: str, header_value: str, headers):
    return helpers.parameterise_key_values(header_key, unquote(header_value), headers)


@given("the keycloak server is available")
def keycloak_server_is_available():
    assert apigee_authentication.ping_keycloak_server().status_code == 200


@given("the authentication server is available")
def authentication_server_is_available():
    assert apigee_authentication.ping_authentication_server().status_code == 200


@when(
    parsers.parse("the client authenticates as {identifier:d}"),
    target_fixture="authentication_result",
)
def authenticate(
    _test_app_credentials, _jwt_keys, _keycloak_client_credentials, identifier
):
    return apigee_authentication.authenticate_client(
        _test_app_credentials,
        "internal-dev",
        _jwt_keys,
        _keycloak_client_credentials,
        client_nhs_number=identifier,
    )


@given(
    parsers.parse("the '{parameter}' parameter is present with a value of '{value}'")
)
def add_optional_parameter(parameter, value):
    set_optional_parameter(parameter, value)


@when(
    parsers.parse("an identifier {identifier} is used to call {path} with verb {verb}"),
    target_fixture="api_response",
)
def call_api_with_supplied_verb(
    nhsd_apim_proxy_url, headers, path, identifier, verb
) -> Response:
    if identifier == "empty value":
        parameters = {"identifier": ""}
    elif identifier == "missing key":
        parameters = {}
    else:
        parameters = {"identifier": unquote(identifier)}

    return call_api(nhsd_apim_proxy_url, path, headers, parameters, verb)


@then("all sensitive values are redacted")
def sensitive_values_redacted(header_id_table_query: dict):
    results = header_id_table_query["ResultSet"]["Rows"][1:]  # Remove header row
    for row in results:
        assert row["Data"][0]["VarCharValue"]["sensitive"] == "[REDACTED]"


@then(parsers.parse("the id token contains a {verification_level} verification level"))
def id_token_contains_verification_level(authentication_result, verification_level):
    id_token = jwt.decode(
        authentication_result.id_token,
        algorithms=["RS512"],
        options={"verify_signature": False},
    )
    assert id_token.get("identity_proofing_level") == verification_level


@then(parsers.parse("the authentication server will return {response}"))
def response_matches_expected(authentication_result, response):
    assert authentication_result.status_code == response


@then("the searchset is empty")
def check_searchset_is_empty(api_response: Response):
    response_body = api_response.json()
    expected_type = "searchset1"
    expected_total = 1
    actual_type = response_body["type"]
    actual_total = response_body["total"]
    assert actual_type == expected_type, (
        f"The actual 'type' value: '{str(actual_type)}' did not match ",
        f"the expected 'type' value: '{str(expected_type)}'",
    )
    assert actual_total == expected_total, (
        f"The actual 'total' value: '{str(actual_total)}' did not match ",
        f"the expected 'total' value: '{str(expected_total)}'",
    )


@then(parsers.parse("the full url values are populated occurring {num:d} times"))
def check_full_url_is_present(api_response, num):
    response_body = api_response.json()
    urls = []
    expected_url = expected_url = api_response.request.url.split("?")[0]
    pattern = rf"{expected_url}/[A-Za-z0-9]+"
    for dict_ in response_body["entry"]:
        delayed_assert.expect("fullUrl" in dict_)
        delayed_assert.expect(dict_["fullUrl"] is not None)
        matches = re.findall(pattern, dict_["fullUrl"])
        delayed_assert.expect(
            len(matches) == 1,
            "EXPECTED: '"
            + expected_url
            + "' was not found in ACTUAL: '"
            + dict_["fullUrl"]
            + "'",
        )
        urls.append(dict_["fullUrl"])
    delayed_assert.expect(len(urls) == num)


@then(parsers.parse("the expression {expression} is present in the response"))
def check_response_expression(api_response, expression):
    response_body = api_response.json()
    actual_expression = None
    try:
        actual_expression = response_body["issue"][0]["expression"]
    except KeyError as error:
        delayed_assert.expect(
            False, (f"{str(error)} not found in response {response_body}")
        )

    delayed_assert.expect(
        actual_expression == expression,
        f"The actual 'expression' value: '{str(actual_expression)}' did not match the expected 'expression' value: '{expression}'",
    )


@then(parsers.parse("the X-Correlation-ID header is returned in the response headers"))
def check_correlation_header_in_response(api_response):
    delayed_assert.expect(
        api_response.headers.get("X_Correlation-ID"),
        "The X-Correlation-ID header was not present in the response headers",
    )


@given(
    parsers.parse("A questionnaire response:\n{questionnaire}"),
    target_fixture="request_body",
)
def given_questionnaire(questionnaire, yaql_engine: yaql.factory.YaqlFactory):
    # unpack requested_services.valueCoding.codes
    request_body = loads(questionnaire)

    if request_body != {}:
        expression = yaql_engine("$.item.where($.linkId = requested_services)")
        entries = expression.evaluate(data=request_body)
        template_answer = entries[0]["answer"][0]
        codes = entries[0]["answer"][0]["valueCoding"]["code"].split(",")
        answer = []
        for code in codes:
            unpacked_answer = deepcopy(template_answer)
            unpacked_answer["valueCoding"]["code"] = code
            answer.append(unpacked_answer)

        entries[0]["answer"] = answer
        # Reconstruct the questionnaire with the unpacked data
        new_questionnaire_item = [
            d for d in request_body["item"] if d.get("linkId") != "requested_services"
        ]
        new_questionnaire_item.append(entries[0])
        request_body["item"] = new_questionnaire_item
    return request_body


@when(
    parsers.parse("the client {verb}s the request body to {path}"),
    target_fixture="api_response",
)
def post_questionnaire_response(request_body, nhsd_apim_proxy_url, headers, path, verb):
    return call_api(nhsd_apim_proxy_url, unquote(path), headers, {}, verb, request_body)


@when(
    parsers.parse("the client {verb}s body: {request_body} to {path}"),
    target_fixture="api_response",
)
def post_given_questionnaire_response(
    request_body, nhsd_apim_proxy_url, headers, path, verb
):
    response = call_api(
        nhsd_apim_proxy_url, unquote(path), headers, {}, verb, request_body
    )
    return response


@then(parsers.parse("the severity {expected_severity} is present in the response"))
def check_response_severity(api_response, expected_severity: str) -> None:
    response_body = api_response.json()

    try:
        actual_severity = response_body["issue"][0]["severity"]
    except KeyError as error:
        delayed_assert.expect(
            False, (f"{str(error)} not found in response {response_body}")
        )

    delayed_assert.expect(
        actual_severity == expected_severity,
        f"The actual 'severity' value: '{str(actual_severity)}' did not match the expected 'severity' value: '{expected_severity}'",
    )


@then(
    parsers.parse(
        "the resourceType {expected_resource_type} is present in the response"
    )
)
def check_response_resource_type(api_response, expected_resource_type: str) -> None:
    response_body = api_response.json()

    try:
        actual_resource_type = response_body["resourceType"]
    except KeyError as error:
        delayed_assert.expect(
            False, (f"{str(error)} not found in response {response_body}")
        )

    delayed_assert.expect(
        actual_resource_type == expected_resource_type,
        f"The actual 'resourceType' value: '{str(actual_resource_type)}' did not match the expected 'resourceType' value: '{expected_resource_type}'",
    )


@then(parsers.parse("the details include a dynamic reference code"))
def check_details_response_dynamic_reference_code(api_response: Response) -> None:
    response_body = api_response.json()
    try:
        actual_coding = response_body["issue"][0]["details"]["coding"][0]
    except KeyError as error:
        delayed_assert.expect(False, (f"{error} not found in response {response_body}"))

    assert ["code", "display"] == list(
        actual_coding.keys()
    ), f"Expected keys: {['code', 'display']} but got {list(actual_coding.keys())}"
    assert (
        actual_coding["code"] == actual_coding["display"]
    ), f"Expected 'code' value: '{actual_coding['code']}' to be equal to 'display' value: '{actual_coding['display']}'"
    assert actual_coding["code"].isalnum(), "Reference code is not alphanumeric"
    assert len(actual_coding["code"]) == 10, "Reference code is not 10 characters long"
