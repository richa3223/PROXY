"""Redacts all the fields inside the "sensitive" block of an event in the standard project event format.
   Sensitive field values are replaced with [REDACTED]
"""

import json
from base64 import b64decode, b64encode

from spine_aws_common import LambdaApplication

from lambdas.utils.logging.logger import LOG_BASE, initialise_logger, write_log


class RedactData(LambdaApplication):
    """Lambda process to redact sensitive values before they are stored in s3 buckets."""

    def initialise(self) -> None:
        """Initialise with log object"""
        initialise_logger(self.log_object)

    def start(self) -> None:
        """Redact all sensitive fields in a given event."""

        write_log("DEBUG", {"info": "Start run"})
        outputs = []

        for record in self.event["records"]:
            business_event = json.loads(b64decode(record["data"]).decode("utf-8"))
            result = "Ok"

            if "detail" in business_event and "sensitive" in business_event["detail"]:
                business_event["detail"]["sensitive"] = "[REDACTED]"
                write_log("DEBUG", {"info": "Data successfully redacted for event."})
            else:
                result = "ProcessingFailed"
                write_log(
                    "ERROR",
                    {
                        "info": "Processing failed because the sensitive block was not found in the passed events, see CloudWatch logs for details.",
                        "error": "",
                    },
                )

            redacted_record = {
                "recordId": record["recordId"],
                "result": result,
                "data": b64encode(json.dumps(business_event).encode("utf-8")).decode(
                    "utf-8"
                ),
            }
            outputs.append(redacted_record)

        write_log(
            "DEBUG",
            {"info": "Processed {} records.".format(len(self.event["records"]))},
        )
        self.response = {"records": outputs}


process_result = RedactData(additional_log_config=LOG_BASE)


def lambda_handler(event: dict, context: dict) -> dict:
    """Redacts values in the sensitive field of any event input in the agreed format before returning the redacted event.

    Args:
        event (dict): The event to redact
        context (dict): Current context

    Returns:
        records (list) : A list containing dicts that consists of recordID, result of transformation (ok,dropped,failure) and the redacted event itself.
    """

    return process_result.main(event, context)
