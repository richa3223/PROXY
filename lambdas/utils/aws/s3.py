from boto3 import client


def get_s3_file(bucket: str, file_name: str) -> str:
    """Get the contents of a file from an S3 bucket

    Args:
        bucket (str): The name of the bucket
        file_name (str): The name of the file

    Returns:
        str: The contents of the file
    """
    s3 = client("s3")
    response = s3.get_object(Bucket=bucket, Key=file_name)
    return response["Body"].read().decode("utf-8")


def put_s3_file(bucket: str, file_name: str, body: str) -> str:
    s3 = client("s3")
    response = s3.put_object(Bucket=bucket, Key=file_name, Body=body)
    print(f"Response {response}")
