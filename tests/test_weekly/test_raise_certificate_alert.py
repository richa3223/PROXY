from datetime import datetime, timedelta
from logging import getLogger
from uuid import uuid4

import pytest
from boto3 import client
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import NameOID

from ..helpers import ENVIRONMENT, WORKSPACE, Helpers

S3_FILE_PREFIX = "weekly-test"
RAISE_CERTIFICATE_ALERT_FUNCTION_NAME = f"{WORKSPACE}-raise_certificate_alert"
TRUST_STORE_BUCKET = f"{WORKSPACE}-{ENVIRONMENT}-truststore-bucket"
s3_client = client("s3")
logger = getLogger(__name__)


class TestRaiseCertificateAlert:
    def teardown_class(self) -> None:
        """Remove any remaining log groups"""
        paginator = s3_client.get_paginator("list_objects_v2")
        operation_parameters = {"Bucket": TRUST_STORE_BUCKET, "Prefix": S3_FILE_PREFIX}
        page_iterator = paginator.paginate(**operation_parameters)
        for page in page_iterator:
            if "Contents" in page:
                for object in page["Contents"]:
                    s3_client.delete_object(
                        Bucket=TRUST_STORE_BUCKET,
                        Key=object["Key"],
                    )

    def certificate_builder(self, time_delta: timedelta) -> x509.Certificate:
        """Create a certificate"""
        root_key = ec.generate_private_key(ec.SECP256R1())
        subject = issuer = x509.Name(
            [
                x509.NameAttribute(NameOID.COUNTRY_NAME, "UK"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Yorkshire"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, "Leeds"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Test"),
                x509.NameAttribute(NameOID.COMMON_NAME, f"weekly-test-{str(uuid4())}"),
            ]
        )
        certificate = x509.CertificateBuilder(
            subject_name=subject,
            issuer_name=issuer,
            not_valid_after=datetime.now() + time_delta,
            not_valid_before=datetime.now(),
            serial_number=x509.random_serial_number(),
            public_key=root_key.public_key(),
        )
        return certificate.sign(root_key, hashes.SHA256())

    @pytest.mark.parametrize(
        "time_delta",
        [
            timedelta(days=7),
            timedelta(days=14),
            timedelta(days=30),
            timedelta(days=60),
            timedelta(days=90),
        ],
    )
    def test_raise_certificate_alerts(
        self, time_delta: timedelta, helpers: Helpers
    ) -> None:
        """Test the raise certificate alert lambda"""
        # Arrange
        s3_file_key = f"{S3_FILE_PREFIX}-{str(uuid4())}.pem"
        certificate = self.certificate_builder(time_delta)
        s3_client.put_object(
            Bucket=TRUST_STORE_BUCKET,
            Key=s3_file_key,
            Body=certificate.public_bytes(serialization.Encoding.PEM),
        )
        # Act
        response = helpers.invoke_lambda_function(
            RAISE_CERTIFICATE_ALERT_FUNCTION_NAME, {}
        )
        # Assert
        assert response == {"message": "Raise certificate alert lambda complete"}
        # TODO: Check alerts are raised - NPA-3178
        # Cleanup
        s3_client.delete_object(Bucket=TRUST_STORE_BUCKET, Key=s3_file_key)
        logger.info(f"Deleted {s3_file_key}")

    @pytest.mark.parametrize(
        "time_delta",
        [
            timedelta(days=6),
            timedelta(days=8),
            timedelta(days=13),
            timedelta(days=15),
            timedelta(days=29),
            timedelta(days=31),
            timedelta(days=59),
            timedelta(days=61),
            timedelta(days=89),
            timedelta(days=91),
        ],
    )
    def test_raise_certificate_alerts_with_no_alert(
        self, time_delta: timedelta, helpers: Helpers
    ) -> None:
        """Test the raise certificate alert lambda"""
        # Arrange
        s3_file_key = f"{S3_FILE_PREFIX}-{str(uuid4())}.pem"
        certificate = self.certificate_builder(time_delta)
        s3_client.put_object(
            Bucket=TRUST_STORE_BUCKET,
            Key=s3_file_key,
            Body=certificate.public_bytes(serialization.Encoding.PEM),
        )
        # Act
        response = helpers.invoke_lambda_function(
            RAISE_CERTIFICATE_ALERT_FUNCTION_NAME, {}
        )
        # Assert
        assert response == {"message": "Raise certificate alert lambda complete"}
        # TODO: Check no alerts are raised - NPA-3178
        # Cleanup
        s3_client.delete_object(Bucket=TRUST_STORE_BUCKET, Key=s3_file_key)
        logger.info(f"Deleted {s3_file_key}")
