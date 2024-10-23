"""
Cache and adapt PDS responses
"""

from hashlib import sha256
from json import dumps, loads
from os import getenv

import boto3
from aws_lambda_powertools import Logger
from botocore.exceptions import ClientError
from requests import Request, Response, Session

logger = Logger(service="cache_pds_response")
TIMEOUT = 200

CACHE_STATUS_HEADER = "X-Cache-Status"
CACHE_KEY_HEADER = "X-Cache-Key"
CACHE_HIT = "HIT"
CACHE_MISS = "MISS"


class CachePDSResponse:
    """
    Cache PDS Responses
    """

    target = "https://int.api.service.nhs.uk/personal-demographics"

    def __init__(self, table_name) -> None:
        self.table_name = table_name

    def get_base_url_from_event(self, event: dict) -> str:
        """
        Extract the url path from the event
        """
        base_url = f"{self.target}{event['path']}"
        return base_url

    def create_cache_key(self, base_url: str, query_string_params: dict = None) -> str:
        """
        Create a cache key from a base url and query string
        """
        if isinstance(query_string_params, dict):
            sorted_query_params = sorted(query_string_params.items())
            serialized_params = "&".join(
                f"{key}={','.join(value)}" for key, value in sorted_query_params
            )
            cache_key = f"{base_url}?{serialized_params}"
        else:
            cache_key = base_url

        sha256_hash = sha256()
        sha256_hash.update(cache_key.encode("utf-8"))

        return sha256_hash.hexdigest()

    def cache_pds_response(self, key: str, response: Response) -> str:
        """
        Cache the response from PDS
        """
        dynamodb = boto3.client("dynamodb")

        try:
            dynamodb.put_item(
                TableName=self.table_name,
                Item={
                    "CacheKey": {"S": key},
                    "Body": {"S": response.text},
                    "Headers": {"S": dumps(dict(response.headers))},
                    "StatusCode": {"N": str(response.status_code)},
                },
            )
            return key

        except Exception as e:
            logger.error(f"Error writing to cache: {str(e)}")

            return None

    def get_response_from_cache(self, key: str) -> dict:
        """
        Get cached response for previously called requests
        """
        dynamodb = boto3.client("dynamodb")

        try:
            key = {"CacheKey": {"S": key}}
            item = dynamodb.get_item(TableName=self.table_name, Key=key)
        except ClientError:
            # ResourceNotFoundException
            return None

        if "Item" in item:
            return item["Item"]

        return None

    def request(self, event: dict) -> Response:
        """
        Pass request on to PDS
        """

        headers = {}
        try:
            # Filter out headers that PDS complains about
            headers = {
                key: event["headers"][key] for key in ["Authorization", "X-Request-ID"]
            }
        except Exception as e:
            logger.warning(f"error filtering headers:{e}")

        api_request = Request(
            method=event["httpMethod"],
            url=self.get_base_url_from_event(event),
            params=event["queryStringParameters"],
            headers=headers,
        )
        logger.info("pds request", url=api_request.url)
        session = Session()
        prepped = session.prepare_request(api_request)
        try:
            response = session.send(prepped, timeout=TIMEOUT)
            logger.info(
                "pds response", status=response.status_code, json=response.json()
            )
            return response

        except Exception as e:
            logger.exception("Error fetching from pds", url=api_request.url)
            return None

    def main(self, event: dict, context: dict) -> dict:
        """
        Get responses from PDS checking cache first and caching successful responses
        """
        url = self.get_base_url_from_event(event)
        key = self.create_cache_key(url, event["queryStringParameters"])

        lambda_response = {"headers": {"Content-Type": "application/json"}}

        cached_response = self.get_response_from_cache(key)

        if cached_response is not None:
            lambda_response["body"] = cached_response["Body"]["S"]
            lambda_response["headers"] = lambda_response["headers"] | loads(
                cached_response["Headers"]["S"]
            )
            lambda_response["headers"][CACHE_STATUS_HEADER] = CACHE_HIT
            lambda_response["statusCode"] = cached_response["StatusCode"]["N"]
        else:

            pds_response = self.request(event)
            if pds_response is not None:
                if pds_response.ok:
                    self.cache_pds_response(key, pds_response)
                lambda_response["body"] = dumps(pds_response.json())
                lambda_response["headers"] = lambda_response["headers"] | dict(
                    pds_response.headers
                )
                lambda_response["headers"][CACHE_STATUS_HEADER] = CACHE_MISS
                lambda_response["statusCode"] = pds_response.status_code
            else:
                # Handle the case where pds_response is None
                lambda_response["body"] = dumps({"error": "No response from PDS"})
                lambda_response["statusCode"] = 500  # Internal Server Error

        lambda_response["headers"][CACHE_KEY_HEADER] = key

        return lambda_response


def lambda_handler(event: dict, context: dict) -> str:
    """
    Returns the response from a request to PDS.
    Response is cached if URL requested is not in the cache
    and subsequent calls will return it from there.
    """
    try:
        cache_table = getenv("DYNAMODB_TABLE_NAME")
        cache_pds = CachePDSResponse(cache_table)
        result = cache_pds.main(event, context)
    except Exception as e:
        result = {
            "body": f'{{"error": {e}}}',
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
        }

    return result
