import datetime
import re
import unittest
from unittest import mock

from lambdas.utils.reference_code.ref_code import ReferenceCode


class RefCodeTests(unittest.TestCase):
    TABLE_NAME = "DYNAMODB_TABLE_NAME"

    def test_generate_reference_code(self):
        """Check that the reference code created is of the correct format"""
        regex = "([0-9a-f]){5}([a-z0-9]){5}"
        ref = ReferenceCode()
        ref_code = ref.generate_ref_code()
        assert re.match(regex, ref_code)

    @mock.patch(
        "lambdas.utils.reference_code.ref_code.ReferenceCode.get_date",
        return_value=datetime.date(2024, 1, 1),
    )
    def test_single_digit_day_in_date(self, date_mock):
        """Test that the day component has one character when it's a single-digit date"""
        expected = "18101"
        ref = ReferenceCode()
        ref_code = ref.generate_ref_code()
        datestamp = ref_code[:5]  # Extract the first 5 characters for datestamp
        assert expected == datestamp

    @mock.patch(
        "lambdas.utils.reference_code.ref_code.ReferenceCode.get_date",
        return_value=datetime.date(2024, 12, 31),
    )
    def test_double_digit_day_in_date(self, date_mock):
        """Test that a double-digit date is populated as expected"""
        expected = "18c1f"
        ref = ReferenceCode()
        ref_code = ref.generate_ref_code()
        datestamp = ref_code[:5]
        assert expected == datestamp

    @mock.patch(
        "lambdas.utils.reference_code.ref_code.ReferenceCode.get_date",
        return_value=datetime.date(2024, 7, 10),
    )
    def test_tenth_date_in_july(self, date_mock):
        """Test that the generated reference code has the correct format for 10th of July date"""
        expected = "1870a"
        ref = ReferenceCode()
        ref_code = ref.generate_ref_code()
        datestamp = ref_code[:5]
        assert expected == datestamp

    @mock.patch(
        "lambdas.utils.reference_code.ref_code.ReferenceCode.TABLE_NAME",
        return_value=TABLE_NAME,
    )
    @mock.patch(
        "lambdas.utils.reference_code.ref_code.resource.Table.get_item",
        return_value={},
    )
    @mock.patch("lambdas.utils.reference_code.ref_code.resource")
    def test_check_dynamodb_for_duplicates(
        self, resource_mock, get_item_mock, table_name_mock
    ):
        """Test that check function accepts ref codes and checks DynamoDb"""
        test_ref_code = "18701abcde"
        ref = ReferenceCode()
        check_for_duplicates = ref.check_dynamo_db_for_duplicates(test_ref_code)
        assert check_for_duplicates is False

    @mock.patch(
        "lambdas.utils.reference_code.ref_code.ReferenceCode.TABLE_NAME",
        return_value=TABLE_NAME,
    )
    @mock.patch(
        "lambdas.utils.reference_code.ref_code.ReferenceCode.check_dynamo_db_for_duplicates",
        return_value=False,
    )
    def test_ref_code_returned_from_loop(self, check_dynamodb_mock, table_name_mock):
        ref = ReferenceCode()
        ref_code = ref.create_reference_code()
        assert len(ref_code) == 10
        regex = "([0-9a-f]){5}([a-z0-9]){5}"
        assert re.match(regex, ref_code)

    @mock.patch(
        "lambdas.utils.reference_code.ref_code.ReferenceCode.TABLE_NAME",
        return_value=TABLE_NAME,
    )
    @mock.patch(
        "lambdas.utils.reference_code.ref_code.ReferenceCode.check_dynamo_db_for_duplicates",
        side_effect=KeyError("Duplicate entry. Retrying..."),
    )
    def test_retries_triggered_by_check(self, check_dynamodb_mock, table_name_mock):
        """Show that the retry loop is triggered when the DynamoDB check returns true"""
        ref = ReferenceCode()
        with self.assertRaises(
            ValueError, msg="Generated reference code duplicated 10 times."
        ) as val:
            ref.create_reference_code()
        self.assertEqual(
            "Generated reference code duplicated 10 times.", str(val.exception)
        )

    def test_get_date_function(self):
        """Test for get_date function - wraps datetime.date.today() for mocking purposes"""
        expected = datetime.date.today()
        ref = ReferenceCode()
        actual_date = ref.get_date()
        assert actual_date == expected
