""" Authenticates with PDS to generate an authorisation token for any PDS queries
"""

import json
import os
import uuid
from http import HTTPStatus
from time import time

import jwt
import requests
from requests.exceptions import ConnectionError as connection_error
from requests.exceptions import HTTPError, RequestException, Timeout
from spine_aws_common import LambdaApplication

from lambdas.utils.aws.secret_manager import SecretManager
from lambdas.utils.logging.logger import LOG_BASE, initialise_logger, write_log


class PdsAccessToken(LambdaApplication):
    """Authenticates with API Service to generate an authorisation token."""

    SETTINGS = {
        "token_url": os.getenv("PDS_AUTH_URL"),
        "private_key": "",
        "subject": "",
        "issuer": "",
        "audience": os.getenv("PDS_AUTH_URL"),
        "algorithm": "RS512",
        "key_id": "",
    }

    secret_manager = SecretManager("PDS_CREDENTIALS")

    def initialise(self) -> None:
        """Initialise with log object"""
        initialise_logger(self.log_object)

    def load_secrets(self):
        """Loads secrets required for this lambda from AWS secret store"""
        key = self.secret_manager.get_secret("NHS-api-private-key")
        key = key.replace("\\n", "\n")  # Preserve new lines in key
        self.SETTINGS["private_key"] = key
        self.SETTINGS["subject"] = self.secret_manager.get_secret("NHS-api-client-id")
        self.SETTINGS["issuer"] = self.secret_manager.get_secret("NHS-api-client-id")
        self.SETTINGS["key_id"] = self.secret_manager.get_secret("NHS-api-key-id")

    def start(self) -> None:
        """Authenticates with API Service to generate an authorisation token."""
        write_log("DEBUG", {"info": "PdsAccessToken : Start ran"})

        self.load_secrets()

        claims = {
            "sub": self.SETTINGS["subject"],
            "iss": self.SETTINGS["issuer"],
            "jti": str(uuid.uuid4()),
            "aud": self.SETTINGS["audience"],
            "exp": int(time()) + 300,  # 300 = 60 * 5 (5 Mins)
        }

        additional_headers = {
            "alg": self.SETTINGS["algorithm"],
            "typ": "JWT",
            "kid": self.SETTINGS["key_id"],
        }

        assertion = jwt.encode(
            claims,
            self.SETTINGS["private_key"],
            algorithm=self.SETTINGS["algorithm"],
            headers=additional_headers,
        )

        payload = {
            "grant_type": "client_credentials",
            "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            "client_assertion": assertion,
        }

        url = self.SETTINGS["token_url"]

        try:
            # requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
            response = requests.post(url, data=payload, timeout=60)
            if response.status_code != HTTPStatus.OK:
                raise RequestException("Failed to get 200 response from remote.")

            response_dict = json.loads(response.content)
            self.generate_response(HTTPStatus.OK, response_dict)
            write_log("DEBUG", {"info": "PdsAccessToken : Generation successful"})

        except connection_error as conn_error:
            write_log(
                "ERROR",
                {
                    "info": "Error establishing connection to remote host.",
                    "error": conn_error,
                },
            )
            self.generate_response(HTTPStatus.BAD_REQUEST, None)

        except HTTPError as response_error:
            write_log(
                "ERROR",
                {
                    "info": "Remote host responded with invalid response.",
                    "error": response_error,
                },
            )
            self.generate_response(HTTPStatus.BAD_REQUEST, None)

        except Timeout as timeout:
            write_log(
                "ERROR",
                {
                    "info": "Request timed out.",
                    "error": timeout,
                },
            )
            self.generate_response(HTTPStatus.REQUEST_TIMEOUT, None)

        except RequestException as request_ex:
            write_log(
                "ERROR",
                {
                    "info": "Error when requesting API token.",
                    "error": request_ex,
                },
            )
            self.generate_response(HTTPStatus.INTERNAL_SERVER_ERROR, None)

        except AttributeError as attrib_error:
            write_log(
                "ERROR",
                {
                    "info": "Error when requesting API token.",
                    "error": attrib_error,
                },
            )
            self.generate_response(HTTPStatus.INTERNAL_SERVER_ERROR, None)

        except Exception as ex:  # pylint: disable=broad-exception-caught
            write_log(
                "ERROR",
                {
                    "info": "Unexpected error in processing.",
                    "error": ex,
                },
            )
            self.generate_response(HTTPStatus.INTERNAL_SERVER_ERROR, None)

    def generate_response(self, status_code: int, token):
        """Generates a response based on the supplied parameters"""

        self.response = {
            "statusCode": status_code,
            "body": {"token": token},
        }


pds_access_token = PdsAccessToken(additional_log_config=LOG_BASE)


def lambda_handler(event: dict, context: dict) -> str:
    """Generates a PDS Access token by authenticating with the API service.

    Args:
        None

    Returns:
        authToken (string) : The authorisation token
    """
    result = pds_access_token.main(event, context)

    return result
