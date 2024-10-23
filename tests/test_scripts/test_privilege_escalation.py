from json import dumps
from logging import getLogger

import pytest
from boto3 import client

sts = client("sts")
iam = client("iam")
current_account_id = sts.get_caller_identity()["Account"]
logger = getLogger(__name__)

TAGS = [
    {
        "Key": "Test_Script",
        "Value": "tests/test_scripts/test_privilege_escalation.py",
    }
]
EXPECTED_EXPLICIT_DENY_ERROR_MSG = "with an explicit deny in an identity-based policy"


class TestPrivilegeEscalation:

    def setup(self) -> None:
        """Check roles that can be tested"""
        caller = sts.get_caller_identity()
        if "SSO" not in caller["Arn"]:
            raise ValueError("Not a testable role")
        elif "SSO" in caller["Arn"] and "Admin" in caller["Arn"]:
            raise ValueError("Role is expected to have all these permisisons")

    def test_create_role(self) -> None:
        """Test create role"""
        with pytest.raises(Exception) as exc_info:
            iam.create_role(
                RoleName="privilege_escalation_test_role",
                AssumeRolePolicyDocument=dumps(
                    {
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Effect": "Allow",
                                "Principal": {"Service": "events.amazonaws.com"},
                                "Action": "sts:AssumeRole",
                            }
                        ],
                    }
                ),
                Description="Test event bus delivery to DLQ",
                MaxSessionDuration=3600,
                Tags=TAGS,
            )

        assert EXPECTED_EXPLICIT_DENY_ERROR_MSG in str(
            exc_info.value
        ), "Role creation didn't fail as expected"

    def test_create_policy(self) -> None:
        """Test create policy"""
        with pytest.raises(Exception) as exc_info:
            iam.create_policy(
                PolicyName="privilege_escalation_test_policy",
                PolicyDocument=dumps(
                    {
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Effect": "Allow",
                                "Action": "s3:GetObject",
                                "Resource": "*",
                            }
                        ],
                    }
                ),
                Tags=TAGS,
            )
        assert EXPECTED_EXPLICIT_DENY_ERROR_MSG in str(
            exc_info.value
        ), "Policy creation didn't fail as expected"

    def test_delete_policy(self) -> None:
        """Test delete policy"""
        with pytest.raises(Exception) as exc_info:
            iam.delete_policy(
                PolicyArn=f"arn:aws:iam::{current_account_id}:policy/PVRS-Developer"
            )
        assert EXPECTED_EXPLICIT_DENY_ERROR_MSG in str(
            exc_info.value
        ), "Policy deletion didn't fail as expected"

    def test_attach_role_policy(self) -> None:
        """Test attach role policy"""
        with pytest.raises(Exception) as exc_info:
            iam.attach_role_policy(
                RoleName="PVRS-ReadOnly",
                PolicyArn="arn:aws:iam::aws:policy/AdministratorAccess",
            )
        assert EXPECTED_EXPLICIT_DENY_ERROR_MSG in str(
            exc_info.value
        ), "Role policy attachment didn't fail as expected"

    def test_detach_role_policy(self) -> None:
        """Test detach role policy"""
        with pytest.raises(Exception) as exc_info:
            iam.detach_role_policy(
                RoleName="PVRS-ReadOnly",
                PolicyArn="arn:aws:iam::aws:policy/ReadOnlyAccess",
            )
        assert EXPECTED_EXPLICIT_DENY_ERROR_MSG in str(
            exc_info.value
        ), "Role policy detachment didn't fail as expected"

    def test_delete_permission_boundary(self) -> None:
        """Test delete permission boundary"""
        with pytest.raises(Exception) as exc_info:
            iam.delete_role_permissions_boundary(RoleName="PVRS-ReadOnly")
        assert EXPECTED_EXPLICIT_DENY_ERROR_MSG in str(
            exc_info.value
        ), "Permission boundary deletion didn't fail as expected"

    def test_can_not_assume_role(self) -> None:
        """Test can not assume role"""
        with pytest.raises(Exception) as exc_info:
            sts.assume_role(
                RoleArn=f"arn:aws:iam::{current_account_id}:role/PVRS-ReadOnly",
                RoleSessionName="test",
            )
        assert "is not authorized to perform: sts:AssumeRole" in str(
            exc_info.value
        ), "Role assumption didn't fail as expected"
