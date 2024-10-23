from os import getenv

from boto3 import client

sts = client("sts")

WORKSPACE = getenv("WORKSPACE", "main")
ENVIRONMENT = getenv("ENVIRONMENT", "dev")
AWS_REGION = getenv("AWS_REGION", "eu-west-2")
AWS_ACCOUNT_ID = sts.get_caller_identity().get("Account")
