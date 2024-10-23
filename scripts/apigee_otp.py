import sys
import pyotp


def main(username: str, otp_key: str) -> None:
    """Generate APIGEE OTP for API Tests

    Args:
        username (str): Username to generate OTP
        otp_key (str): OTP key
    """
    otp = pyotp.parse_uri(f"otpauth://totp/{username}?secret={otp_key}")
    print(otp.now())


if __name__ == "__main__":
    username = sys.argv[1]
    otp_key = sys.argv[2]
    main(username, otp_key)
