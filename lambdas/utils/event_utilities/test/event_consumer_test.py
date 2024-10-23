"""Test event_consumer module."""

# pylint: disable=redefined-outer-name
import json
from datetime import datetime
from pathlib import Path

import pytest

from lambdas.utils.code_bindings.validation_result import (
    Detail,
    Detail_metadata,
    Detail_sensitive,
    Detail_standard,
)
from lambdas.utils.code_bindings.validation_result import Event as ValidationResult
from lambdas.utils.code_bindings.validation_result import (
    Marshaller as ValidationResultMarshaller,
)
from lambdas.utils.event_utilities.event_consumer import unmarshall


def _load_json(file_name: str) -> dict:
    """Deserialises a json file into a dict.

    Args:
        file_name (str): The name of the json file relative to the directory
            this module is in.

    Returns:
        dict: The deserialised json object
    """
    with open(
        Path(Path(__file__).parent, file_name),
        "r",
        encoding="utf-8",
    ) as f:
        return json.load(f)


@pytest.fixture
def validation_failed_event_json() -> dict:
    """Yield an example 'Validation Failed' event."""
    yield _load_json("validation-failed-event.json")


def test_unmarshal_validation_result_event(validation_failed_event_json: dict):
    """Test the unmarshal method on a validation result event."""
    expected = ValidationResult(
        Detail(
            Detail_metadata(
                client_key="0ce6574f-a702-4359-9c1f-ff87a83aefa0",
                correlation_id="639d1d64-b6da-45a3-b0f6-0263f14baa35",
                created=datetime(2024, 1, 25, 11, 42, 23, 544872).isoformat(),
                request_id="d2ef3f40-e387-491b-b2a4-3d5473f73268",
            ),
            Detail_sensitive(
                patient_identifier="9435797881", proxy_identifier="9435775039"
            ),
            Detail_standard(
                proxy_identifier_type="NHS Number",
                relationship_type="GESTM",
                validation_result_info={
                    "NO_PATIENT_CONSENT": "\
Validation failed: related person record is sensitive or restricted (-S)"
                },
            ),
        ),
        DetailType="Validation Failed",
        EventBusName=None,
        Source="Validation Service",
    )
    actual = unmarshall(
        validation_failed_event_json,
        ValidationResultMarshaller.unmarshall,
        ValidationResult,
    )
    assert expected == actual


@pytest.mark.parametrize("required_item", ["source", "detail-type", "detail"])
def test_validation_result_event_with_missing_attributes(
    validation_failed_event_json: dict, required_item: str
):
    """Test no exceptions are raised when items are missing."""
    del validation_failed_event_json[required_item]
    unmarshall(
        validation_failed_event_json,
        ValidationResultMarshaller.unmarshall,
        ValidationResult,
    )
