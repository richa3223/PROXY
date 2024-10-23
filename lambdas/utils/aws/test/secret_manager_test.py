import json
import os

from pytest_mock import MockerFixture

from lambdas.utils.aws.secret_manager import SecretManager


def test_when_secret_manager_initalised_then_defaults_are_loaded():
    store_name_environment_variable = "STORE_NAME"
    os.environ[store_name_environment_variable] = "storename"
    os.environ[SecretManager.STORE_REGION_VARIABLE] = "regionname"

    sut = SecretManager(store_name_environment_variable)

    assert sut.store_name == "storename"
    assert sut.store_region == "regionname"


def test_when_no_secrets_are_loaded_then_call_causes_secrets_to_be_loaded(
    mocker: MockerFixture,
):
    mocker.patch("botocore.client.BaseClient._make_api_call", new=amend_make_api_call)

    sut = SecretManager("STORE_NAME")
    sut.secrets = {}

    actual = sut.get_secret("foo")
    assert actual == "bar"


def test_when_secrets_are_loaded_then_they_are_not_loaded(mocker: MockerFixture):
    mocked_instance = mocker.patch.object(
        SecretManager, "load_secrets_from_aws", return_value=None
    )

    sut = SecretManager("STORE_NAME")
    sut.secrets = {"foo": "bar"}

    actual = sut.get_secret("foo")
    assert actual == "bar"
    mocked_instance.assert_not_called()


def test_when_loading_secrets_is_successful_then_secrets_are_loaded(
    mocker: MockerFixture,
):
    sut = SecretManager("STORE_NAME")
    mocker.patch("botocore.client.BaseClient._make_api_call", new=amend_make_api_call)

    # _amend_get_secret_value("sme", "supersecret", mocker)

    # mock_session_object = mocker.Mock()
    # mock_client = mocker.Mock()
    # mock_client.get_secret_value.return_value = {'SecretString': 'my-secret'}
    # mock_session_object.client.return_value = mock_client
    # mocker.patch('botocore.client.BaseClient._make_api_call', new=amend_make_api_call)

    sut.load_secrets_from_aws()
    expected = json.loads('{"foo":"bar"}')

    assert sut.secrets == expected


def amend_make_api_call(self, operation_name, kwargs):
    # Intercept boto3 operations for <secretsmanager.get_secret_value>. Optionally, you can also
    # check on the argument <SecretId> and control how you want the response would be. This is
    # a very flexible solution as you have full control over the whole process of fetching a
    # secret.

    if operation_name == "GetSecretValue" and kwargs["SecretId"] is not None:
        # if isinstance(secret_value, Exception):
        #     raise secret_value
        return {
            "Name": "secret_name",
            "SecretString": '{"foo":"bar"}',
        }
