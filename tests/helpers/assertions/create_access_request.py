def assert_400_bad_request(payload: dict) -> None:
    """Asserts the payload is a 400 Bad Request response

    Args:
        payload (dict): The response payload
    """
    assert payload["body"]["issue"][0]["code"] == "invalid"
    assert payload["body"]["issue"][0]["details"]["coding"][0]["code"] == "BAD_REQUEST"
    assert (
        payload["body"]["issue"][0]["details"]["coding"][0]["display"]
        == "The request could not be processed."
    )
    assert (
        payload["body"]["issue"][0]["details"]["coding"][0]["system"]
        == "https://fhir.nhs.uk/R4/CodeSystem/ValidatedRelationships-ErrorOrWarningCode"
    )
    assert payload["body"]["issue"][0]["details"]["coding"][0]["version"] == "1"
    assert "The supplied input is not a valid FHIR QuestionnaireResponse." in (
        payload["body"]["issue"][0]["diagnostics"]
    )
    assert payload["body"]["issue"][0]["severity"] == "error"
    assert payload["body"]["resourceType"] == "OperationOutcome"
