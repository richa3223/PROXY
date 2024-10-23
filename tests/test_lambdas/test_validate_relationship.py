"""
Test validate proxy/patient relationship
"""

from datetime import date, timedelta

import pytest
from dateutil.relativedelta import relativedelta

from ..helpers import WORKSPACE, Helpers

FUNCTION_NAME = f"{WORKSPACE}-validate_relationship"


today: date = date.today()
yesterday: date = today - timedelta(days=1)
tomorrow: date = today + timedelta(days=1)
# relativedelta takes leap years into account
thirteen_years_ago: date = today - relativedelta(years=13)


def get_proxy_nhs_number(test_data):
    """
    Get Proxy's NHS number from
    """
    return test_data["proxyNhsNumber"]


def test_valid_relationship(helpers: Helpers) -> None:
    """
    Is relationship between patient and proxy valid?
    """
    test_data = helpers.load_test_data(
        "test_lambdas/test_input/validate_relationship/test1_input.json"
    )
    payload = helpers.invoke_lambda_function(FUNCTION_NAME, test_data)
    proxy_nhs_number = get_proxy_nhs_number(test_data)

    assert payload["statusCode"] == 200
    assert payload["body"]["pdsPatient"] is not None
    assert payload["body"]["pdsRelationshipLookup"] is not None
    assert (
        payload["body"]["pdsRelationshipLookup"]["patient"]["identifier"]["value"]
        == proxy_nhs_number
    )


def test_valid_relationship_active_not_present(helpers: Helpers) -> None:
    """
    Test patient has valid relationship with proxy
    """
    test_data = helpers.load_test_data(
        "test_lambdas/test_input/validate_relationship/test2_input.json"
    )
    payload = helpers.invoke_lambda_function(FUNCTION_NAME, test_data)
    proxy_nhs_number = get_proxy_nhs_number(test_data)

    assert payload["statusCode"] == 200
    assert payload["body"]["pdsPatient"] is not None
    assert payload["body"]["pdsRelationshipLookup"] is not None
    assert (
        payload["body"]["pdsRelationshipLookup"]["patient"]["identifier"]["value"]
        == proxy_nhs_number
    )


def test_valid_relationship_start_date_yesterday(helpers: Helpers) -> None:
    """
    Test boundary condition of relationship validity
    """

    test_data = helpers.load_test_data(
        "test_lambdas/test_input/validate_relationship/test1_input.json"
    )
    test_data["pdsRelationshipLookup"][0]["period"]["start"] = yesterday
    payload = helpers.invoke_lambda_function(FUNCTION_NAME, test_data)
    proxy_nhs_number = get_proxy_nhs_number(test_data)

    assert payload["statusCode"] == 200
    assert payload["body"]["pdsPatient"] is not None
    assert payload["body"]["pdsRelationshipLookup"] is not None
    assert (
        payload["body"]["pdsRelationshipLookup"]["patient"]["identifier"]["value"]
        == proxy_nhs_number
    )


def test_valid_relationship_start_date_today(helpers: Helpers) -> None:
    """
    Test boundary condition of relationship validity
    """
    test_data = helpers.load_test_data(
        "test_lambdas/test_input/validate_relationship/test1_input.json"
    )
    test_data["pdsRelationshipLookup"][0]["period"]["start"] = today
    payload = helpers.invoke_lambda_function(FUNCTION_NAME, test_data)
    proxy_nhs_number = get_proxy_nhs_number(test_data)

    assert payload["statusCode"] == 200
    assert payload["body"]["pdsPatient"] is not None
    assert payload["body"]["pdsRelationshipLookup"] is not None
    assert (
        payload["body"]["pdsRelationshipLookup"]["patient"]["identifier"]["value"]
        == proxy_nhs_number
    )


def test_valid_relationship_end_date_tomorrow(helpers: Helpers) -> None:
    """
    Test boundary condition of relationship validity
    """
    test_data = helpers.load_test_data(
        "test_lambdas/test_input/validate_relationship/test1_input.json"
    )
    test_data["pdsRelationshipLookup"][0]["period"]["end"] = tomorrow
    payload = helpers.invoke_lambda_function(FUNCTION_NAME, test_data)
    proxy_nhs_number = get_proxy_nhs_number(test_data)

    assert payload["statusCode"] == 200
    assert payload["body"]["pdsPatient"] is not None
    assert payload["body"]["pdsRelationshipLookup"] is not None
    assert (
        payload["body"]["pdsRelationshipLookup"]["patient"]["identifier"]["value"]
        == proxy_nhs_number
    )


def test_valid_relationship_end_date_today(helpers: Helpers) -> None:
    """
    Test boundary condition of relationship validity
    """
    test_data = helpers.load_test_data(
        "test_lambdas/test_input/validate_relationship/test1_input.json"
    )
    test_data["pdsRelationshipLookup"][0]["period"]["end"] = today
    payload = helpers.invoke_lambda_function(FUNCTION_NAME, test_data)
    proxy_nhs_number = get_proxy_nhs_number(test_data)

    assert payload["statusCode"] == 200
    assert payload["body"]["pdsPatient"] is not None
    assert payload["body"]["pdsRelationshipLookup"] is not None
    assert (
        payload["body"]["pdsRelationshipLookup"]["patient"]["identifier"]["value"]
        == proxy_nhs_number
    )


def test_valid_relationship_end_date_not_present(helpers: Helpers) -> None:
    """
    Test boundary condition of relationship validity
    """
    test_data = helpers.load_test_data(
        "test_lambdas/test_input/validate_relationship/test3_input.json"
    )
    payload = helpers.invoke_lambda_function(FUNCTION_NAME, test_data)
    proxy_nhs_number = get_proxy_nhs_number(test_data)

    assert payload["statusCode"] == 200
    assert payload["body"]["pdsPatient"] is not None
    assert payload["body"]["pdsRelationshipLookup"] is not None
    assert (
        payload["body"]["pdsRelationshipLookup"]["patient"]["identifier"]["value"]
        == proxy_nhs_number
    )


def test_valid_relationship_both_relationship_dates_not_present(
    helpers: Helpers,
) -> None:
    """
    Test where both relationship dates are not present
    """
    test_data = helpers.load_test_data(
        "test_lambdas/test_input/validate_relationship/test4_input.json"
    )
    payload = helpers.invoke_lambda_function(FUNCTION_NAME, test_data)
    proxy_nhs_number = get_proxy_nhs_number(test_data)

    assert payload["statusCode"] == 200
    assert payload["body"]["pdsPatient"] is not None
    assert payload["body"]["pdsRelationshipLookup"] is not None
    assert (
        payload["body"]["pdsRelationshipLookup"]["patient"]["identifier"]["value"]
        == proxy_nhs_number
    )


def test_two_relationships_one_valid(helpers: Helpers) -> None:
    """
    Test where one of two relationships is valid
    """
    test_data = helpers.load_test_data(
        "test_lambdas/test_input/validate_relationship/test5_input.json"
    )
    payload = helpers.invoke_lambda_function(FUNCTION_NAME, test_data)
    proxy_nhs_number = get_proxy_nhs_number(test_data)

    assert payload["statusCode"] == 200
    assert payload["body"]["pdsPatient"] is not None
    assert payload["body"]["pdsRelationshipLookup"] is not None
    assert (
        payload["body"]["pdsRelationshipLookup"]["patient"]["identifier"]["value"]
        == proxy_nhs_number
    )


def test_three_relationships_one_valid(helpers: Helpers) -> None:
    """
    Test three relationships where one is valid
    """
    test_data = helpers.load_test_data(
        "test_lambdas/test_input/validate_relationship/test6_input.json"
    )
    payload = helpers.invoke_lambda_function(FUNCTION_NAME, test_data)
    proxy_nhs_number = get_proxy_nhs_number(test_data)

    assert payload["statusCode"] == 200
    assert payload["body"]["pdsPatient"] is not None
    assert payload["body"]["pdsRelationshipLookup"] is not None
    assert (
        payload["body"]["pdsRelationshipLookup"]["patient"]["identifier"]["value"]
        == proxy_nhs_number
    )


def test_three_relationships_all_invalid(helpers: Helpers) -> None:
    """
    Test three relationships where all invalid
    """
    payload = helpers.invoke_lambda_function_from_file(
        FUNCTION_NAME,
        "test_lambdas/test_input/validate_relationship/test7_input.json",
    )

    assert payload["statusCode"] == 200
    assert payload["body"]["error"] == "PATIENT_NO_RELATIONSHIPS_FOUND"


def test_no_patient_relationships_exist(helpers: Helpers) -> None:
    """
    Test no patient relationships exist
    """
    payload = helpers.invoke_lambda_function_from_file(
        FUNCTION_NAME,
        "test_lambdas/test_input/validate_relationship/test8_input.json",
    )

    assert payload["statusCode"] == 200
    assert payload["body"]["error"] == "PATIENT_NO_RELATIONSHIPS_FOUND"


def test_patient_identifier_no_pds_record(helpers: Helpers) -> None:
    """
    Lambda receives a patient:identifier NHS number for a patient who has no PDS record.
    The Lambda returns:
    Status code is 200
    pdsPatient and pdsRelationship objects are not present
    An error message is present
    An event is published stating no PDS record found
    """
    payload = helpers.invoke_lambda_function_from_file(
        FUNCTION_NAME,
        "test_lambdas/test_input/validate_relationship/test9_input.json",
    )
    assert payload["statusCode"] == 200
    assert payload["body"]["error"] == "PATIENT_NOT_FOUND"


def test_patient_identifier_deceased(helpers: Helpers) -> None:
    """
    Lambda receives a patient:identifier NHS number for a patient who is deceased.
    The Lambda returns:
    Status code is 200
    pdsPatient and pdsRelationship objects are not present
    An error message is present
    An event is published stating the patient:identifier is deceased
    """
    payload = helpers.invoke_lambda_function_from_file(
        FUNCTION_NAME,
        "test_lambdas/test_input/validate_relationship/test10_input.json",
    )

    assert payload["statusCode"] == 200
    assert payload["body"]["error"] == "PATIENT_DECEASED"


def test_patient_identifier_restricted(helpers: Helpers) -> None:
    """
    Lambda receives a patient:identifier NHS number for a patient who is
    marked as restricted.
    The Lambda returns:
    Status code is 200
    pdsPatient and pdsRelationship objects are not present
    An error message is present
    An event is published stating the patient:identifier is restricted
    """
    payload = helpers.invoke_lambda_function_from_file(
        FUNCTION_NAME,
        "test_lambdas/test_input/validate_relationship/test11_input.json",
    )

    assert payload["statusCode"] == 200
    assert payload["body"]["error"] == "NO_PATIENT_CONSENT"


def test_relationship_not_active(helpers: Helpers) -> None:
    """
    Test relationship where patient is not active
    """
    test_data = helpers.load_test_data(
        "test_lambdas/test_input/validate_relationship/test1_input.json"
    )
    test_data["pdsRelationshipLookup"][0]["active"] = False
    payload = helpers.invoke_lambda_function(FUNCTION_NAME, test_data)

    assert payload["statusCode"] == 200
    assert payload["body"]["error"] == "PATIENT_NO_RELATIONSHIPS_FOUND"


def test_relationship_start_date_tomorrow(helpers: Helpers) -> None:
    """
    Test edge case where relationship validity starts tomorrow
    """
    test_data = helpers.load_test_data(
        "test_lambdas/test_input/validate_relationship/test1_input.json"
    )
    test_data["pdsRelationshipLookup"][0]["period"]["start"] = tomorrow
    payload = helpers.invoke_lambda_function(FUNCTION_NAME, test_data)

    assert payload["statusCode"] == 200
    assert payload["body"]["error"] == "PATIENT_NO_RELATIONSHIPS_FOUND"


def test_relationship_end_date_yesterday(helpers: Helpers) -> None:
    """
    Test edge case where relationship validity ended yesterday
    """
    test_data = helpers.load_test_data(
        "test_lambdas/test_input/validate_relationship/test1_input.json"
    )
    test_data["pdsRelationshipLookup"][0]["period"]["end"] = yesterday
    payload = helpers.invoke_lambda_function(FUNCTION_NAME, test_data)

    assert payload["statusCode"] == 200
    assert payload["body"]["error"] == "PATIENT_NO_RELATIONSHIPS_FOUND"


def test_relationship_not_mth(helpers: Helpers) -> None:
    """
    Test where relationship between proxy and patient is not mother
    """
    test_data = helpers.load_test_data(
        "test_lambdas/test_input/validate_relationship/test1_input.json"
    )
    test_data["pdsRelationshipLookup"][0]["relationship"][0]["coding"][0][
        "code"
    ] = "PRN"
    payload = helpers.invoke_lambda_function(FUNCTION_NAME, test_data)

    assert payload["statusCode"] == 200
    assert payload["body"]["error"] == "PATIENT_NO_RELATIONSHIPS_FOUND"


def test_relationship_proxy_nhs_number_mismatch(helpers: Helpers) -> None:
    """
    Test Proxy relationship mismatch
    """
    test_data = helpers.load_test_data(
        "test_lambdas/test_input/validate_relationship/test1_input.json"
    )
    test_data["pdsRelationshipLookup"][0]["patient"]["identifier"][
        "value"
    ] = "9000000025"
    payload = helpers.invoke_lambda_function(FUNCTION_NAME, test_data)

    assert payload["statusCode"] == 200
    assert payload["body"]["error"] == "PATIENT_NO_RELATIONSHIPS_FOUND"


def test_patient_identifier_12_years_364_days_old(helpers: Helpers) -> None:
    """
    Lambda receives a patient:identifier NHS number for a patient who is
    today 12 years 364 days old.
    The Lambda returns:
    Status code is 200
    pdsPatient object contains the patient details
    pds Relationship object contains relationship details
    """
    test_data = helpers.load_test_data(
        "test_lambdas/test_input/validate_relationship/test1_input.json"
    )
    test_data["pdsPatient"]["birthDate"] = thirteen_years_ago + timedelta(days=1)
    payload = helpers.invoke_lambda_function(FUNCTION_NAME, test_data)
    proxy_nhs_number = get_proxy_nhs_number(test_data)

    assert payload["statusCode"] == 200
    assert payload["body"]["pdsPatient"] is not None
    assert payload["body"]["pdsRelationshipLookup"] is not None
    assert (
        payload["body"]["pdsRelationshipLookup"]["patient"]["identifier"]["value"]
        == proxy_nhs_number
    )


def test_patient_identifier_13_years_old(helpers: Helpers) -> None:
    """
    Lambda receives a patient:identifier NHS number for a patient who is
    today 13 years 0 days old.
    The Lambda returns:
    Status code is 200
    pdsPatient and pdsRelationship objects are not present
    An error message is present
    An event is published stating the patient:identifier is over 13
    """
    test_data = helpers.load_test_data(
        "test_lambdas/test_input/validate_relationship/test1_input.json"
    )
    test_data["pdsPatient"]["birthDate"] = thirteen_years_ago
    payload = helpers.invoke_lambda_function(FUNCTION_NAME, test_data)

    assert payload["statusCode"] == 200
    assert payload["body"]["error"] == "NOT_ELIGIBLE"


def test_patient_identifier_13_years_1_day_old(helpers: Helpers) -> None:
    """
    Lambda receives a patient:identifier NHS number for a patient who is
    today 13 years 1 day old.
    The Lambda returns:
    Status code is 200
    pdsPatient and pdsRelationship objects are not present
    An error message is present
    An event is published stating the patient:identifier is over 13
    """
    test_data = helpers.load_test_data(
        "test_lambdas/test_input/validate_relationship/test1_input.json"
    )
    test_data["pdsPatient"]["birthDate"] = thirteen_years_ago - timedelta(days=1)
    payload = helpers.invoke_lambda_function(FUNCTION_NAME, test_data)

    assert payload["statusCode"] == 200
    assert payload["body"]["error"] == "NOT_ELIGIBLE"


def test_patient_identifier_dob_yyyy_mm_eligible(helpers: Helpers) -> None:
    """
    Lambda receives a patient:identifier NHS number for a patient who has
    a date of birth format yyyy-mm 2011-02 (today's actual date is 2024-01-22).
    The Lambda returns:
    Status code is 200
    pdsPatient object contains the patient details
    pds Relationship object contains relationship details
    """
    test_data = helpers.load_test_data(
        "test_lambdas/test_input/validate_relationship/test1_input.json"
    )
    one_month_date = (thirteen_years_ago + relativedelta(months=1)).strftime("%Y-%m")
    test_data["pdsPatient"]["birthDate"] = one_month_date
    payload = helpers.invoke_lambda_function(FUNCTION_NAME, test_data)
    proxy_nhs_number = get_proxy_nhs_number(test_data)

    assert payload["statusCode"] == 200
    assert payload["body"]["pdsPatient"] is not None
    assert payload["body"]["pdsRelationshipLookup"] is not None
    assert (
        payload["body"]["pdsRelationshipLookup"]["patient"]["identifier"]["value"]
        == proxy_nhs_number
    )


def test_patient_identifier_dob_yyyy_mm_ineligible(helpers: Helpers) -> None:
    """
    Lambda receives a patient:identifier NHS number for a patient who has
    a date of birth format yyyy-mm 2011-01 (today's actual date is 2024-01-22).
    The Lambda returns:
    Status code is 200
    pdsPatient and pdsRelationship objects are not present
    An error message is present
    An event is published stating the patient:identifier is over 13
    """
    test_data = helpers.load_test_data(
        "test_lambdas/test_input/validate_relationship/test1_input.json"
    )
    test_data["pdsPatient"]["birthDate"] = thirteen_years_ago.strftime("%Y-%m")
    payload = helpers.invoke_lambda_function(FUNCTION_NAME, test_data)

    assert payload["statusCode"] == 200
    assert payload["body"]["error"] == "NOT_ELIGIBLE"


def test_patient_identifier_dob_yyyy_eligible(helpers: Helpers) -> None:
    """
    Lambda receives a patient:identifier NHS number for a patient who has
    a date of birth format yyyy 2012 (today's actual date is 2024-01-22).
    The Lambda returns:
    Status code is 200
    pdsPatient object contains the patient details
    pds Relationship object contains relationship details
    """
    one_year_date = (thirteen_years_ago + relativedelta(years=1)).strftime("%Y")
    test_data = helpers.load_test_data(
        "test_lambdas/test_input/validate_relationship/test1_input.json"
    )
    test_data["pdsPatient"]["birthDate"] = one_year_date
    payload = helpers.invoke_lambda_function(FUNCTION_NAME, test_data)
    proxy_nhs_number = get_proxy_nhs_number(test_data)

    assert payload["statusCode"] == 200
    assert payload["body"]["pdsPatient"] is not None
    assert payload["body"]["pdsRelationshipLookup"] is not None
    assert (
        payload["body"]["pdsRelationshipLookup"]["patient"]["identifier"]["value"]
        == proxy_nhs_number
    )


def test_patient_identifier_dob_yyyy_ineligible(helpers: Helpers) -> None:
    """
    Lambda receives a patient:identifier NHS number for a patient who has
    a date of birth format yyyy 2011 (today's actual date is 2024-01-22).
    The Lambda returns:
    Status code is 200
    pdsPatient and pdsRelationship objects are not present
    An error message is present
    An event is published stating the patient:identifier is over 13
    """
    test_data = helpers.load_test_data(
        "test_lambdas/test_input/validate_relationship/test1_input.json"
    )
    test_data["pdsPatient"]["birthDate"] = thirteen_years_ago.strftime("%Y")
    payload = helpers.invoke_lambda_function(FUNCTION_NAME, test_data)

    assert payload["statusCode"] == 200
    assert payload["body"]["error"] == "NOT_ELIGIBLE"


def test_patient_identifier_deceased_and_restricted(helpers: Helpers) -> None:
    """
    Lambda receives a patient:identifier NHS number for a patient who
    is marked as deceased and restricted.
    The Lambda returns:
    Status code is 200
    pdsPatient and pdsRelationship objects are not present
    An error message is present
    An event is published stating the patient:identifier is deceased
    """
    test_data = helpers.load_test_data(
        "test_lambdas/test_input/validate_relationship/test10_input.json"
    )
    test_data["pdsPatient"]["meta"]["security"][0]["code"] = "R"
    payload = helpers.invoke_lambda_function(FUNCTION_NAME, test_data)

    assert payload["statusCode"] == 200
    assert payload["body"]["error"] == "PATIENT_DECEASED"


def test_patient_identifier_restricted_and_13_years_old(helpers: Helpers) -> None:
    """
    Lambda receives a patient:identifier NHS number for a patient who
    is marked as restricted and is 13 years 0 days old.
    The Lambda returns:
    Status code is 200
    pdsPatient and pdsRelationship objects are not present
    An error message is present
    An event is published stating the patient:identifier is restricted
    """
    test_data = helpers.load_test_data(
        "test_lambdas/test_input/validate_relationship/test11_input.json"
    )
    test_data["pdsPatient"]["birthDate"] = thirteen_years_ago
    payload = helpers.invoke_lambda_function(FUNCTION_NAME, test_data)

    assert payload["statusCode"] == 200
    assert payload["body"]["error"] == "NO_PATIENT_CONSENT"


def test_patient_identifier_13_years_old_and_relationship_not_mth(
    helpers: Helpers,
) -> None:
    """
    Test where patient is 13 and relationship with proxy is not mother
    """
    test_data = helpers.load_test_data(
        "test_lambdas/test_input/validate_relationship/test1_input.json"
    )
    test_data["pdsPatient"]["birthDate"] = thirteen_years_ago
    test_data["pdsRelationshipLookup"][0]["relationship"][0]["coding"][0][
        "code"
    ] = "PRN"
    payload = helpers.invoke_lambda_function(FUNCTION_NAME, test_data)

    assert payload["statusCode"] == 200
    assert payload["body"]["error"] == "NOT_ELIGIBLE"


def test_no_input(helpers: Helpers) -> None:
    """
    Lambda receives no input
    The Lambda returns:
    Status code is 500
    pdsPatient and pdsRelationship objects are not present
    An error message is present stating server error
    """
    payload = helpers.invoke_lambda_function(FUNCTION_NAME, {})

    assert payload["statusCode"] == 500
    assert payload["body"]["error"] == "SERVER_ERROR"


def test_patient_status_400(helpers: Helpers) -> None:
    """
    Lambda receives a patient status code that is not 200
    The Lambda returns:
    Status code is 400
    pdsPatient and pdsRelationship objects are not present
    An error message is present
    An event is published stating bad request
    """
    test_data = helpers.load_test_data(
        "test_lambdas/test_input/validate_relationship/test1_input.json"
    )
    test_data["pdsPatientStatus"] = 400
    payload = helpers.invoke_lambda_function(FUNCTION_NAME, test_data)

    assert payload["statusCode"] == 400
    assert (
        payload["body"]["error"]
        == "BAD_REQUEST - One or more previous operations failed"
    )


def test_relationship_lookup_status_400(helpers: Helpers) -> None:
    """
    Test lookup returning relationship status 400
    """
    test_data = helpers.load_test_data(
        "test_lambdas/test_input/validate_relationship/test1_input.json"
    )
    test_data["pdsRelationshipLookupStatus"] = 400
    payload = helpers.invoke_lambda_function(FUNCTION_NAME, test_data)

    assert payload["statusCode"] == 400
    assert (
        payload["body"]["error"]
        == "BAD_REQUEST - One or more previous operations failed"
    )


def test_patient_status_404(helpers: Helpers) -> None:
    """
    Test where patient record is not found
    """
    test_data = helpers.load_test_data(
        "test_lambdas/test_input/validate_relationship/test1_input.json"
    )
    test_data["pdsPatientStatus"] = 404
    payload = helpers.invoke_lambda_function(FUNCTION_NAME, test_data)

    assert payload["statusCode"] == 200
    assert payload["body"]["error"] == "PATIENT_NOT_FOUND"


def test_relationship_lookup_status_404(helpers: Helpers) -> None:
    """
    Test where relationship lookup is not found
    """
    test_data = helpers.load_test_data(
        "test_lambdas/test_input/validate_relationship/test1_input.json"
    )
    test_data["pdsRelationshipLookupStatus"] = 404
    payload = helpers.invoke_lambda_function(FUNCTION_NAME, test_data)

    assert payload["statusCode"] == 200
    assert payload["body"]["error"] == "PATIENT_NO_RELATIONSHIPS_FOUND"
