import os

import boto3
from botocore.exceptions import ClientError
from spine_aws_common import LambdaApplication

from lambdas.utils.logging.logger import initialise_logger, write_log


class StartGlueCrawler(LambdaApplication):
    """Lambda process to start a glue crawler"""

    def initialise(self) -> None:
        """Initialise with log object"""
        initialise_logger(self.log_object)

    def start(self) -> None:
        crawler_name = os.environ["CRAWLER_NAME"]
        client = self._create_glue_client()

        try:
            client.start_crawler(Name=crawler_name)
            write_log("DEBUG", {"info": f"Started Glue crawler: {crawler_name}"})
        except ClientError as error:
            write_log(
                "ERROR",
                {
                    "info": f"Failed to start Glue crawler: {crawler_name}",
                    "error": str(error),
                },
            )

    def _create_glue_client(self, client_region="eu-west-2"):
        return boto3.client("glue", client_region)
