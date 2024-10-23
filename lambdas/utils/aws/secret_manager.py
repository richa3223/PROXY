"""Retrieves and keeps a copy of the retrieved secrets from AWS.

Raises:
    ClientError: Raised if there is an error with the request for retrieval
    KeyError: Raised if the requested secret does not exist within the secret manager
"""

import json
import os

import boto3
from botocore.exceptions import ClientError

from lambdas.utils.logging.logger import write_log


class SecretManager:
    """Retrieves and keeps a copy of the retrieved secrets from AWS."""

    STORE_REGION_VARIABLE = "REGION"

    secrets = {}
    store_name = ""
    store_region = ""

    def __init__(self, store_name_environment_variable: str) -> None:
        """Initialise the object"""
        self.store_name = os.getenv(store_name_environment_variable)
        self.store_region = os.getenv(self.STORE_REGION_VARIABLE)

    def get_secret(self, key: str) -> str:
        """Retrieves the given key value from the local copy of the secrets store.
        If the secret store has not been initialised locally, then it is initalised.

        Args:
            key (str): The secret store key to retrieve

        Returns:
            str: Value of the secret as a string.

        Raises:
            ClientError: Raised if there is an error with the request for retrieval
            KeyError: Raised if the requested secret does not exist within the secret manager
        """
        # If the secrets store is not initalised
        # Then load the remote store
        if len(self.secrets) == 0:
            self.load_secrets_from_aws()

        secret = self.secrets[key]
        return secret

    def load_secrets_from_aws(self):
        """Retrieves the contents of the secret store from AWS and copies them locally.

        Raises:
            ClientError: Raised if there is an error with the request for retrieval
        """

        write_log("DEBUG", {"info": "Retrieving secrets from AWS store"})

        # Create a client to access the secrets manager service
        # Region name is retrieved from the environment store
        session = boto3.session.Session()
        client = session.client(
            service_name="secretsmanager", region_name=self.store_region
        )

        try:
            # Retrieve information from the specific store
            # This secret store may hold information for multiple lambdas.
            # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
            get_secret_value_response = client.get_secret_value(
                SecretId=self.store_name
            )

            # Decrypts secret using the associated KMS key.
            json_str = get_secret_value_response["SecretString"]

            self.secrets = json.loads(json_str)

            write_log("DEBUG", {"info": "Successfully retrieved secrets from AWS"})

        except ClientError as err:
            # Catching request errors
            write_log(
                "WARNING",
                {"info": "An error occurred retrieving secrets", "exception": err},
            )
            raise err
