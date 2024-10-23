"""Creating the reference code to use in the questionnaire response."""

import datetime
import secrets
import string
from os import getenv

from boto3 import resource


class ReferenceCode:
    """Reference code for use in the questionnaire response."""

    TABLE_NAME = getenv("DYNAMODB_TABLE_NAME")

    def create_reference_code(self) -> str:
        """Create a reference code. We then check the DynamoDB table for a duplicate.
        We have a retry limit of 10 in place.
        """
        ref_code = ""
        for _ in range(10):
            try:
                ref_code = self.generate_ref_code()

                self.check_dynamo_db_for_duplicates(ref_code)
            except KeyError:
                ref_code = ""
                continue
            else:
                break
        if ref_code != "":
            return ref_code
        else:
            raise ValueError("Generated reference code duplicated 10 times.")

    def generate_ref_code(self) -> str:
        """Generation of the actual reference code - we have a 5 character hex
        code representing the date concatenated with a 5 character random
        alphanumeric string."""
        now = self.get_date()

        # Hex year value
        year = now.year - 2000
        hex_year = f"{year:02x}"

        # Hex month value
        month = now.month
        hex_month = f"{month:0x}"

        # Hex day - force a 2 character values
        day = now.day
        hex_day = f"{day:02x}" if now.day < 16 else f"{day:0x}"

        datestamp = f"{hex_year}{hex_month}{hex_day}"

        alphabet = string.ascii_lowercase + string.digits
        random_string = "".join(secrets.choice(alphabet) for _ in range(5))
        ref_code = f"{datestamp}{random_string}"

        return ref_code

    def get_date(self) -> datetime:
        """Return today's date"""
        return datetime.date.today()

    def check_dynamo_db_for_duplicates(self, ref_code: str) -> bool:
        """Make a call to the DynamoDB table to check if the current
        reference code exists"""
        table_name = self.TABLE_NAME

        # Initialize DynamoDB resource
        dynamodb = resource("dynamodb")

        # Specify the table
        table = dynamodb.Table(table_name)
        key = {"ReferenceCode": ref_code}
        item = table.get_item(Key=key)
        if "Item" in item:
            raise KeyError("Duplicate entry. Retrying...")
        return False
