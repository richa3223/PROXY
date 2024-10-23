""" Helper functions for the automated tests."""

import logging
import random
import string
import time
import timeit
import uuid
from datetime import datetime
from json import dumps, load, loads
from typing import Tuple
from urllib import parse

import boto3
from botocore.exceptions import ClientError

from .environment_variables import AWS_REGION, WORKSPACE
from .event_publisher import EventPublisher
from .validation_result import (
    Detail,
    Detail_metadata,
    Detail_sensitive,
    Detail_standard,
)
from .validation_result import Event as ValidationResultEvent

logger = logging.getLogger(__name__)


class Helpers:
    """
    Helper class for regularly functions used across multiple test suites
    """

    FHIR_PREFIX = "https://fhir.nhs.uk/Id/nhs-number|"

    @staticmethod
    def has_query_succeeded(client, execution_id):
        """
        Wait for an Athena query to either succeed or fail
        """
        state = "RUNNING"
        max_execution = 5
        wait_time = 5

        while max_execution > 0 and state in ["RUNNING", "QUEUED"]:
            max_execution -= 1
            response = client.get_query_execution(QueryExecutionId=execution_id)
            if (
                "QueryExecution" in response
                and "Status" in response["QueryExecution"]
                and "State" in response["QueryExecution"]["Status"]
            ):
                state = response["QueryExecution"]["Status"]["State"]
                if state == "SUCCEEDED":
                    return True

            print(".", end="")
            time.sleep(wait_time)

        return False

    @staticmethod
    def query_header_id(
        data_catalogue, table, output_location, header_id, column_name
    ) -> dict:
        """
        Search for a header ID in a given Data Catalogue/Table
        """

        def parse_result_json(response: dict):
            """Parse the first column the query result to json, in place."""
            for row in response["ResultSet"]["Rows"][1:]:
                detail = row["Data"][0]["VarCharValue"]
                row["Data"][0]["VarCharValue"] = loads(detail)

        client = boto3.client("athena")
        query_string = (
            "select cast(detail as JSON) as detail, "
            "detail.metadata as metadata "
            f'from "{data_catalogue}"."{table}" '
            f"where detail.metadata.\"{column_name}\" = '{header_id}';"
        )
        logger.info("Querying Athena for %s with:%s", column_name, query_string)
        response = client.start_query_execution(
            QueryString=query_string,
            ResultConfiguration={"OutputLocation": output_location},
        )
        execution_id = response["QueryExecutionId"]
        Helpers.has_query_succeeded(client, execution_id)
        response = client.get_query_results(QueryExecutionId=execution_id)
        parse_result_json(response)
        return response

    @staticmethod
    def result_contains_entry_with_header_id(response, header_id, column_name) -> bool:
        """
        Return True if header id the response matches the expected value.
        """
        results = response["ResultSet"]["Rows"][1:]  # Remove header row
        return any(
            row["Data"][0]["VarCharValue"]["metadata"][column_name] == header_id
            for row in results
        )

    @staticmethod
    def query_select_id_from_catalogue(
        data_catalogue, table, output_location, profile, workgroup
    ):
        """
        Runs a select id query against the given athena catalogue
        """
        session = boto3.session.Session(profile_name=profile)
        client = session.client("athena")

        query_string = f'SELECT 1 as id FROM "{data_catalogue}"."{table}" LIMIT 1;'
        response = client.start_query_execution(
            QueryString=query_string,
            ResultConfiguration={"OutputLocation": output_location},
            WorkGroup=workgroup,
        )

        execution_id = response["QueryExecutionId"]

        result = Helpers.has_query_succeeded(client, execution_id)

        if result:
            response = client.get_query_results(QueryExecutionId=execution_id)

            results = response["ResultSet"]["Rows"]
            results.pop(0)  # Remove header row
            for row in results:
                return row["Data"][0]["VarCharValue"]

        return None

    @staticmethod
    def load_test_data(test_data_path) -> dict:
        """Load test data used as input to lambdas"""
        with open(test_data_path, encoding="utf-8") as f:
            payload_dict = load(f)
        return payload_dict

    @staticmethod
    def load_test_data_as_str(test_data_path) -> str:
        """Load test data used as input to lambdas as text"""
        with open(test_data_path, encoding="utf-8") as f:
            return f.read()

    @staticmethod
    def get_test_data_as_json(test_data):
        """
        Convert the test data to JSON so it can be used
        as an input to Lambdas under test
        """
        return dumps(test_data, indent=4, sort_keys=True, default=str)

    @staticmethod
    def get_pds_access_token():
        """
        Get PDS Access Token - required for non sandbox environments
        """
        function_name = f"{WORKSPACE}-pds_access_token"
        client = boto3.client("lambda", region_name=AWS_REGION)
        response = client.invoke(FunctionName=function_name, Payload="{}")
        payload = loads(response["Payload"].read())
        return payload["body"]["token"]["access_token"]

    @staticmethod
    def index_data_from_api_call(crawler, timestamp) -> None:
        """
        Makes sure data ingested into the system through the api gets
        indexed before returning.

        If an AWS Crawler is running and the run has started before
        the specified API Call time, then the data will be indexed once
        the crawler is finished, and there is no need to restart the crawler,
        just wait for the run to end. Otherwise, the an AWS crawler is
        not running, or the current run started after the specified API
        Call Time, then we must  wait for the run to end, start a new data
        crawl, and wait for that crawl to finish
        indexing the data.
        """
        client = boto3.client("glue")
        crawler_response = client.get_crawler(Name=crawler)
        crawler_last_start_time = crawler_response["Crawler"]["LastCrawl"]["StartTime"]

        crawler_is_running = crawler_response["Crawler"]["State"] == "RUNNING"
        crawler_started_before_api_call = crawler_last_start_time < timestamp
        if crawler_is_running and crawler_started_before_api_call:
            return
        __class__.wait_until_crawler_ready(crawler)
        client.start_crawler(Name=crawler)
        __class__.wait_until_crawler_ready(crawler)

    @staticmethod
    def wait_until_crawler_ready(crawler) -> None:
        """
        Waits until a specified AWS crawler has finished running
        """
        logger.info("Waiting for crawler to finish running")
        timeout_minutes: int = 120
        retry_seconds: int = 5
        timeout_seconds = timeout_minutes * 60
        client = boto3.client("glue")
        start_time = timeit.default_timer()
        abort_time = start_time + timeout_seconds
        state_previous = None
        while True:
            try:
                crawler_response = client.get_crawler(Name=crawler)
            except ClientError as error:
                logger.error("Failed to get crawler %s, error was: %s", crawler, error)
            state = crawler_response["Crawler"]["State"]
            if state != state_previous:
                logger.info("Crawler %s is %s.", crawler, state.lower())
                state_previous = state
            if state == "READY":  # Other known states: RUNNING, STOPPING
                return
            if timeit.default_timer() > abort_time:
                raise TimeoutError(
                    f"Failed to crawl {crawler}. The allocated time of "
                    f"{timeout_minutes:,} minutes has elapsed."
                )
            time.sleep(retry_seconds)

    @staticmethod
    def publish_event():
        """
        Publishes as AWS event and returns the related correlation id
        """
        event = Helpers.validation_result_event()
        publisher = EventPublisher()
        published = publisher.publish(
            event.DetailType,
            dumps(event.Detail.to_dict(), default=str),
            event.EventBusName,
            event.Source,
        )
        assert published is True
        return event.Detail.metadata.correlation_id

    @staticmethod
    def validation_result_event():
        """
        Builds an event
        """
        return ValidationResultEvent(
            Detail(
                Detail_metadata(
                    client_key=str(uuid.uuid4()),
                    correlation_id=str(uuid.uuid4()) + "-automated-testing",
                    created=datetime.now(),
                    request_id=str(uuid.uuid4()),
                ),
                Detail_sensitive(
                    patient_identifier="9435797881", proxy_identifier="9435775039"
                ),
                Detail_standard(
                    proxy_identifier_type="NHS Number",
                    relationship_type="GESTM",
                    validation_result_info={
                        "VALIDATED_RELATIONSHIP": "Validated relationship"
                    },
                ),
            ),
            DetailType="Validation Successful",
            EventBusName="main-event-bus",
            Source="Validation Service",
        )

    @classmethod
    def remove_url_prefix(cls, nhs_number):
        """
        Remove 'FHIR URL' prefix from nhs number if present
        """
        unquoted_nhs_number = parse.unquote(nhs_number)
        if cls.FHIR_PREFIX in unquoted_nhs_number:
            return unquoted_nhs_number.replace(cls.FHIR_PREFIX, "")

        return nhs_number

    @staticmethod
    def invoke_lambda_function(function_name: str, payload: dict) -> dict:
        """Invoke an AWS lambda function.

        Args:
            function_name (str): The name of the lambda
            payload (dict): The payload to invoke the lambda with

        Returns:
            dict: The response payload from the lambda function

        .. _Lambda.Client.invoke:
            https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda/client/invoke.html
        """
        _response, response_payload = Helpers.invoke_lambda_function_with_response(
            function_name, payload
        )
        return response_payload

    @staticmethod
    def invoke_lambda_function_with_response(
        function_name: str, payload: dict
    ) -> Tuple[dict, dict]:
        """Invoke an AWS lambda function.

        Args:
            function_name (str): The name of the lambda
            payload (dict): The payload to invoke the lambda with

        Returns:
            Tuple[dict, dict]:
                dict: The response dict from the lambda function
                dict: The response payload from the lambda function

        .. _Lambda.Client.invoke:
            https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda/client/invoke.html
        """
        payload = Helpers.get_test_data_as_json(payload)
        client = boto3.client("lambda", region_name=AWS_REGION)
        logger.info(f"Invoking {function_name} lambda function: {payload}")
        response = client.invoke(FunctionName=function_name, Payload=payload)
        logger.info(f"Response received from {function_name}: {response}")
        response_payload = loads(response["Payload"].read())
        logger.info(f"Received payload from {function_name}: {response_payload}")
        return response, response_payload

    @staticmethod
    def invoke_lambda_function_from_file(function_name: str, file: str) -> dict:
        """Invoke an AWS lambda function with a payload from a file.

        Args:
            function_name (str): The name of the lambda
            file (str): The path of the file to use as the payload

        Returns:
            dict: The response payload from the lambda function.
        """
        payload = Helpers.load_test_data(file)
        return Helpers.invoke_lambda_function(function_name, payload)

    @staticmethod
    def parameterise_key_values(key, value, fixture):
        """
        Changes a key value based on keyphrase
        """
        if value == "empty value":
            fixture[key] = ""
        elif value == "missing key":
            del fixture[key]
        elif value == "1000 characters":
            fixture[key] = "".join(
                random.choice(string.ascii_lowercase + string.digits)
                for _ in range(1000)
            )
        elif value == "null":
            fixture[key] = None
        else:
            fixture[key] = value
        return fixture
