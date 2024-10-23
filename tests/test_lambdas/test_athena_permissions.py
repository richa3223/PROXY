"""Test to validate permissions and access to athena"""

from os import getenv

import boto3
import pytest
from botocore.exceptions import ClientError

from ..helpers import ENVIRONMENT, WORKSPACE, Helpers

# The sensitive and non-sensitive profiles should be created in the AWS config
# They should map to roles that already exist in AWS for the various ENVIRONMENTs
sensitive_profile = "nhs-dev-sensitive"
sensitive_catalogue = f"{WORKSPACE}-sensitive-data-catalogue"
sensitive_table = (
    f"{WORKSPACE}_audit_{WORKSPACE}_{ENVIRONMENT}_sensitive_audit_events_bucket"
)
sensitive_output_location = (
    f"s3://{WORKSPACE}-{ENVIRONMENT}-sensitive-query-results-bucket/"
)
sensitive_s3 = f"{WORKSPACE}-{ENVIRONMENT}-sensitive-query-results-bucket"
sensitive_workgroup = f"{WORKSPACE}-sensitive-athena-workgroup"

nonsensitive_profile = "nhs-dev-non-sensitive"
nonsensitive_catalogue = f"{WORKSPACE}-queryable-data-catalogue"
nonsensitive_table = (
    f"{WORKSPACE}_audit_{WORKSPACE}_{ENVIRONMENT}_queryable_audit_events_bucket"
)
nonsensitive_output_location = (
    f"s3://{WORKSPACE}-{ENVIRONMENT}-standard-query-results-bucket/"
)
nonsensitive_s3 = f"{WORKSPACE}-{ENVIRONMENT}-standard-query-results-bucket"
nonsensitive_workgroup = f"{WORKSPACE}-standard-athena-workgroup"


# Sensitive role checks
@pytest.mark.skipif(
    getenv("GH_SKIP_TESTS") == "true",
    reason="Skipping test due to AWS Profile not available in GitHub Actions",
)
def test_when_using_sensitive_role_can_access_sensitive_info(helpers: Helpers) -> None:
    """
    Test Scenario: Sensitive role can access sensitive data
    Given: Using the sensitive profile
    And running a query on sensitive data
    Then: Operation succeeds
    """

    result = helpers.query_select_id_from_catalogue(
        sensitive_catalogue,
        sensitive_table,
        sensitive_output_location,
        sensitive_profile,
        sensitive_workgroup,
    )

    assert result is not None


@pytest.mark.skipif(
    getenv("GH_SKIP_TESTS") == "true",
    reason="Skipping test due to AWS Profile not available in GitHub Actions",
)
def test_when_using_sensitive_role_cannot_access_nonsensitive_info(
    helpers: Helpers,
) -> None:
    """
    Test Scenario: Sensitive role cannot access non-sensitive data
    Given: Using the sensitive profile
    And running a query on non-sensitive data
    Then: Operation fails
    """

    with pytest.raises(ClientError) as exinfo:
        helpers.query_select_id_from_catalogue(
            nonsensitive_catalogue,
            nonsensitive_table,
            nonsensitive_output_location,
            sensitive_profile,
            nonsensitive_workgroup,
        )

    assert exinfo.value.response["Error"]["Code"] == "AccessDeniedException"


@pytest.mark.skipif(
    getenv("GH_SKIP_TESTS") == "true",
    reason="Skipping test due to AWS Profile not available in GitHub Actions",
)
def test_when_using_sensitive_role_cannot_access_nonsensitive_s3():
    """
    Test Scenario: Sensitive role cannot directly access non-sensitive s3
    Given: Using the sensitive profile
    And attempting to read from non-sensitive s3 buckets
    Then: Operation fails
    """

    session = boto3.session.Session(profile_name=sensitive_profile)
    s3 = session.resource("s3")
    bucket = s3.Bucket(nonsensitive_s3)
    with pytest.raises(ClientError) as exinfo:
        for obj in bucket.objects.all():
            obj.key

    assert exinfo.value.response["Error"]["Code"] == "AccessDenied"


# Non-Sensitive role checks
@pytest.mark.skipif(
    getenv("GH_SKIP_TESTS") == "true",
    reason="Skipping test due to AWS Profile not available in GitHub Actions",
)
def test_when_using_nonsensitive_role_can_access_nonsensitive_info(
    helpers: Helpers,
) -> None:
    """
    Test Scenario: Non-Sensitive role can access non-sensitive data
    Given: Using the non-sensitive profile
    And running a query on non-sensitive data
    Then: Operation succeeds
    """

    result = helpers.query_select_id_from_catalogue(
        nonsensitive_catalogue,
        nonsensitive_table,
        nonsensitive_output_location,
        nonsensitive_profile,
        nonsensitive_workgroup,
    )

    assert result is not None


@pytest.mark.skipif(
    getenv("GH_SKIP_TESTS") == "true",
    reason="Skipping test due to AWS Profile not available in GitHub Actions",
)
def test_when_using_nonsensitive_role_cannot_access_sensitive_info(
    helpers: Helpers,
) -> None:
    """
    Test Scenario: Non-Sensitive role cannot access sensitive data
    Given: Using the non-sensitive profile
    And running a query on sensitive data
    Then: Operation fails
    """

    with pytest.raises(ClientError) as exinfo:
        helpers.query_select_id_from_catalogue(
            sensitive_catalogue,
            sensitive_table,
            sensitive_output_location,
            nonsensitive_profile,
            sensitive_workgroup,
        )

    assert exinfo.value.response["Error"]["Code"] == "AccessDeniedException"


@pytest.mark.skipif(
    getenv("GH_SKIP_TESTS") == "true",
    reason="Skipping test due to AWS Profile not available in GitHub Actions",
)
def test_when_using_nonsensitive_role_cannot_access_sensitive_s3():
    """
    Test Scenario: Non-sensitive role cannot directly access sensitive s3
    Given: Using the non-sensitive profile
    And attempting to read from non-sensitive s3 buckets
    Then: Operation fails
    """

    session = boto3.session.Session(profile_name=nonsensitive_profile)
    s3 = session.resource("s3")
    bucket = s3.Bucket(sensitive_s3)
    with pytest.raises(ClientError) as exinfo:
        for obj in bucket.objects.all():
            obj.key

    assert exinfo.value.response["Error"]["Code"] == "AccessDenied"
