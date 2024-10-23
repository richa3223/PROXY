from boto3 import client

from ..environment_variables import ENVIRONMENT, WORKSPACE

s3 = client("s3")
HYDRATED_EMAIL_BUCKET = (
    f"{WORKSPACE}-{ENVIRONMENT}-hydrated-email-temporary-storage-bucket"
)


def put_object(bucket_name: str, key: str, body: str) -> None:
    """Put an object into the S3 bucket

    Args:
        bucket_name (str): The name of the bucket
        key (str): The key of the object
        body (str): The body of the object
    """
    s3.put_object(Bucket=bucket_name, Key=key, Body=body)
