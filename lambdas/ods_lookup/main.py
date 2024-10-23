import traceback
from http import HTTPStatus
from os import getenv

from boto3.dynamodb.types import TypeSerializer
from requests import get
from requests.exceptions import HTTPError
from spine_aws_common import LambdaApplication

from lambdas.utils.aws.secret_manager import SecretManager
from lambdas.utils.logging.logger import LOG_BASE, initialise_logger, write_log

type_serializer = TypeSerializer()


class ODSLookup(LambdaApplication):

    settings = {"api_url": "", "api_subscription_key": ""}

    secret_manager = SecretManager("ODS_LOOKUP_CREDENTIALS")

    def initialise(self) -> None:
        """Initialise with log object"""
        initialise_logger(self.log_object)
        self.settings["api_url"] = getenv("ODS_LOOKUP_BASE_URL")

    def __load_secrets(self) -> None:
        """Loads secrets required for this lambda from AWS secret store"""
        self.settings["api_subscription_key"] = self.secret_manager.get_secret(
            "ODS-lookup-subscription-key"
        )

    def start(self) -> None:
        """Retrieves the GP information associated with the ODS code"""

        write_log("DEBUG", {"info": "ODSLookup : Start ran"})
        ods_code = self.event.get("ods_code")
        if ods_code is None or ods_code == "":
            write_log(
                "ERROR",
                {
                    "info": "Invalid parameters supplied.",
                    "error": "ods_code is required",
                },
            )
            raise ValueError("ods_code is required")
        try:
            self.__load_secrets()
            response = get(
                f'{self.settings["api_url"]}/{ods_code}',
                timeout=60,
                headers={"Subscription-key": self.settings["api_subscription_key"]},
            )
            if response.status_code != HTTPStatus.OK:
                write_log(
                    "ERROR",
                    {
                        "info": f"Response from API: status_code={response.status_code} content={response.content}",
                        "error": "",
                    },
                )
                raise HTTPError("Failed to get 200 response from remote.")
            self.response = type_serializer.serialize(
                response.json()["email"].split(":")
            )

        except Exception as ex:
            write_log(
                "ERROR",
                {
                    "info": f"Unexpected error in processing - {ex}",
                    "error": traceback.format_exc(),
                },
            )
            raise


ods_lookup = ODSLookup(additional_log_config=LOG_BASE)


def lambda_handler(event: dict, context: dict) -> dict:
    """Wrapper function to allow invoking of the underlying ODSLookup logic.

    Args:
        event (dict): Parameters to supply to ODSLookup
        context (dict): Current context

    Returns:
        dict: Generated response or error.
    """
    return ods_lookup.main(event, context)
