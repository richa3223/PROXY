from json import dumps

import boto3
import pytest

iam = boto3.client("iam")
sts = boto3.client("sts")

EXPECTED_EXPLICIT_DENY_ERROR_MSG = "with an explicit deny in an identity-based policy"

current_account_id = sts.get_caller_identity()["Account"]
caller = sts.get_caller_identity()
developer_sso_role = [
    role["RoleName"]
    for role in iam.list_roles()["Roles"]
    if "Developer" in role["RoleName"]
][0]


@pytest.mark.skipif(
    "SSO" in caller["Arn"] and "Admin" in caller["Arn"],
    reason="Only non-admin SSO/GH Action roles can be tested",
)
class TestIAMPermissions:
    """Test IAM permissions

    This test suite is designed to ensure that the GitHub Actions IAM permissions are set correctly and can't be escalated.
    It can only be run by non-admin SSO/GH Action roles.
    """

    def test_attach_policy_to_sso_role(self) -> None:
        """Test attach policy to SSO role

        This test will fail if the user does not have the necessary permissions to attach a policy to an SSO role
        """
        with pytest.raises(Exception) as exc_info:
            iam.attach_role_policy(
                RoleName=developer_sso_role,
                PolicyArn="arn:aws:iam::aws:policy/AdministratorAccess",
            )
        assert EXPECTED_EXPLICIT_DENY_ERROR_MSG in str(
            exc_info.value
        ), "Role policy attachment didn't fail as expected"

    def test_detach_policy_from_sso_role(self) -> None:
        """Test detach policy from SSO role

        This test will fail if the user does not have the necessary permissions to detach a policy from an SSO role
        """
        with pytest.raises(Exception) as exc_info:
            iam.detach_role_policy(
                RoleName=developer_sso_role,
                PolicyArn="arn:aws:iam::aws:policy/PVRS-Developer",
            )
        assert EXPECTED_EXPLICIT_DENY_ERROR_MSG in str(
            exc_info.value
        ), "Role policy detachment didn't fail as expected"

    def test_delete_sso_permission_boundary(self) -> None:
        """Test delete SSO permission boundary

        This test will fail if the user does not have the necessary permissions to delete a permission boundary from an SSO role
        """
        with pytest.raises(Exception) as exc_info:
            iam.delete_role_permissions_boundary(RoleName=developer_sso_role)
        assert EXPECTED_EXPLICIT_DENY_ERROR_MSG in str(
            exc_info.value
        ), "Permission boundary deletion didn't fail as expected"

    def test_update_sso_assume_role_policy(self) -> None:
        """Test update SSO assume role policy

        This test will fail if the user does not have the necessary permissions to update an assume role policy for an SSO role
        """
        with pytest.raises(Exception) as exc_info:
            iam.update_assume_role_policy(
                RoleName=developer_sso_role,
                PolicyDocument=dumps(
                    {
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Effect": "Allow",
                                "Principal": {"Service": "sso.amazonaws.com"},
                                "Action": "sts:AssumeRole",
                            }
                        ],
                    }
                ),
            )
        assert EXPECTED_EXPLICIT_DENY_ERROR_MSG in str(
            exc_info.value
        ), "Assume role policy update didn't fail as expected"

    def test_cannot_assume_sso_role(self) -> None:
        """Test cannot assume SSO role

        This test will fail if the user can assume an SSO role
        """
        with pytest.raises(Exception) as exc_info:
            sts.assume_role(
                RoleArn=f"arn:aws:iam::{current_account_id}:role/{developer_sso_role}",
                RoleSessionName="test",
            )
        assert "is not authorized to perform: sts:AssumeRole" in str(exc_info.value)
