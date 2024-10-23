"""
Tests for lambdas.utils.pds.nhsnumber
These tests cover the various input validation required.
"""

import pytest

from lambdas.utils.pds.nhsnumber import NHSNumber


def test_when_an_invalid_nhs_number_then_returns_false():
    """Validation fails when invalid nhs number is provided"""
    sut = NHSNumber()
    actual = sut.is_valid_nhs_number("0")

    assert not actual


@pytest.mark.parametrize(
    "nhs_number, expected",
    [
        pytest.param("9000000009", "9000000009", id="Standard input"),
        pytest.param("900-000-0009", "9000000009", id="Standard input with dashes"),
        pytest.param(" 900 000 0009 ", "9000000009", id="Standard input with spaces"),
        pytest.param(
            "https://fhir.nhs.uk/Id/nhs-number|9000000009",
            "9000000009",
            id="System URL",
        ),
        pytest.param(
            "https%3A%2F%2Ffhir.nhs.uk%2FId%2Fnhs-number%7C9000000009",
            "9000000009",
            id="System URL encoded",
        ),
        pytest.param(
            "random-string", "random-string", id="Non NHS Number original returned"
        ),
        pytest.param(
            None, None, id="confirm original input is returned on optional case"
        ),
    ],
)
def test_extracting_nhs_number_from_string(nhs_number: str, expected: str):
    """Validation results in expected result based on inputs"""
    sut = NHSNumber()
    actual = sut.extract_nhs_number(nhs_number)

    assert actual == expected


@pytest.mark.parametrize(
    "nhs_number, expected",
    [
        pytest.param(" 900 000 0009 ", True, id="Valid with spaces"),
        pytest.param("900-000-0009", True, id="Valid with dashes"),
        pytest.param("9000000009", True, id="Valid"),
        pytest.param("900A000B0009", False, id="Ignores invalid characters"),
        pytest.param("1234567890", False, id="Checksum fail"),
    ],
)
def test_when_a_valid_nhs_number_then_returns_false(nhs_number: str, expected: bool):
    """Validation results in expected result based on inputs"""
    sut = NHSNumber()
    actual = sut.is_valid_nhs_number(nhs_number)

    assert actual == expected


@pytest.mark.parametrize(
    "nhs_number, expected",
    [
        pytest.param(" 900 000 0009 ", "9000000009", id="Strip spaces"),
        pytest.param("900-000-0009", "9000000009", id="Strip dashes"),
        pytest.param("900A000B0009", "900A000B0009", id="Ignores invalid characters"),
    ],
)
def test_alphanumeric_characters_are_not_removed_when_stripping_characters(
    nhs_number, expected
):
    """Input string removes expected characters"""
    sut = NHSNumber()
    actual = sut.sanitise_input(nhs_number)

    assert actual == expected


@pytest.mark.parametrize(
    "nhs_number, expected",
    [
        pytest.param("9000000009", True, id="Valid checksum"),
        pytest.param("9100000000", True, id="Valid checksum - Check is 11(0)"),
        pytest.param("9000000050", False, id="Invalid checksum - Check is 10"),
        pytest.param("900000009", False, id="Nhs number too short"),
        pytest.param("90000000009", False, id="Nhs number too long"),
        pytest.param("9000000008", False, id="Invlaid checksum"),
        pytest.param("900000000A", False, id="Invalid checksum character"),
    ],
)
def test_checksum_when_invalid_characters(nhs_number, expected):
    """Checksum character is validated with the expected result"""
    sut = NHSNumber()
    actual = sut.valid_check_sum(nhs_number)
    assert actual == expected
