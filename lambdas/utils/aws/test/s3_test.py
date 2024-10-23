from pytest_mock import MockerFixture

from lambdas.utils.aws.s3 import get_s3_file, put_s3_file


def test_get_s3_file(mocker: MockerFixture) -> None:
    """Test get_s3_file"""
    # Arrange
    mock_client = mocker.patch("lambdas.utils.aws.s3.client")
    file_name = "file"
    bucket = "bucket"
    # Act
    assert (
        get_s3_file(bucket, file_name)
        == mock_client.return_value.get_object.return_value["Body"]
        .read()
        .decode.return_value
    )
    # Assert
    mock_client.assert_called_once_with("s3")
    mock_client.return_value.get_object.assert_called_once_with(
        Bucket=bucket, Key=file_name
    )


def test_put_s3_file(mocker: MockerFixture) -> None:
    """Test put_s3_file"""
    # Arrange
    mock_client = mocker.patch("lambdas.utils.aws.s3.client")
    file_name = "file"
    bucket = "bucket"
    # Act
    put_s3_file(bucket, file_name, "content")
    # Assert
    mock_client.assert_called_once_with("s3")
    mock_client.return_value.put_object.assert_called_once_with(
        Body="content", Bucket=bucket, Key=file_name
    )
