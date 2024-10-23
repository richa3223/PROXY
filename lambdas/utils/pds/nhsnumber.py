"""NHS Number class to extract and validate to the Module-11 requirements."""

import re
from typing import Optional
from urllib.parse import unquote


class NHSNumber:
    """NHS Number class to extract and validate to the Module-11 requirements."""

    NHS_NUMBER_FORMAT = r"(\d{10})$"
    NHS_NUMBER_SYSTEM_BASE_URL = "https://fhir.nhs.uk/Id/nhs-number|"

    def extract_nhs_number(self, nhs_number_input: Optional[str]) -> Optional[str]:
        """
        Extracts the NHS Number from a given string
        If no NHS Number found original input is returned

        Args:
            nhs_number_input (str): String to extract the NHS Number from.

        Returns:
            str: NHS number extracted from the input string
        """

        if nhs_number_input is None:
            return nhs_number_input

        match = re.search(self.NHS_NUMBER_FORMAT, nhs_number_input)
        nhs_number_input_decode = unquote(nhs_number_input)  # URL decode
        if match:
            return self.sanitise_input(nhs_number_input_decode.rsplit("|")[-1])

        # Check if the input is a URL with NHS Number and extract
        if nhs_number_input_decode.startswith(self.NHS_NUMBER_SYSTEM_BASE_URL):
            nhs_number_input_decode.removeprefix(self.NHS_NUMBER_SYSTEM_BASE_URL)
            return self.sanitise_input(nhs_number_input_decode)

        # Attempt to extract NHS Number from sanitized input
        sanitised_number = self.sanitise_input(nhs_number_input)
        if re.match(self.NHS_NUMBER_FORMAT, sanitised_number):
            return sanitised_number

        # No valid NHS Number found, return the original input
        return nhs_number_input

    def is_valid_nhs_number(self, nhs_number: str) -> bool:
        """
        Determines whether a given string is a valid NHS number format.

        Args:
            nhs_number (str): The number to be checked for validity.

        Returns:
            boo: True if the number is valid, False otherwise
        """
        sanitised_number = self.sanitise_input(nhs_number)

        return bool(
            re.match(self.NHS_NUMBER_FORMAT, sanitised_number)
            and self.valid_check_sum(sanitised_number)
        )

    def is_correct_nhs_number_system(self, nhs_number: str) -> bool:
        """
        Determines whether a given string is a valid NHS number system.

        Args:
            nhs_number (str): The number to be checked for validity.

        Returns:
            boo: True if the number is valid, False otherwise
        """
        if self.valid_check_sum(self.sanitise_input(nhs_number)):
            # NHS Number System URL is not found
            return True
        decoded_number = unquote(nhs_number)  # URL may be encoded so decode it first
        return decoded_number.startswith(self.NHS_NUMBER_SYSTEM_BASE_URL)

    def sanitise_input(self, input_string: str) -> str:
        """Removes any spaces or dashes within the given string

        Args:
            input_string (str): The string to sanitise

        Returns:
            str: The sanitised string
        """
        sanitised = re.sub(r"[- ]", "", input_string)
        return sanitised

    def valid_check_sum(self, nhs_number: str) -> bool:
        """Validates the checksum digit for the given nhs number

        Args:
            nhs_number (str): The NHS number to validate

        Returns:
            bool: True if the checksum is valid, False otherwise
        """
        if not re.match(self.NHS_NUMBER_FORMAT, nhs_number):
            return False

        # The first 9 digits are used to calculate the checksum
        # The last digit is the check digit and should match checksum
        (digits, check_digit) = (nhs_number[:-1], int(nhs_number[-1]))

        # https://digital.nhs.uk/services/nhs-number/nhs-number-client
        # https://en.wikipedia.org/wiki/NHS_number
        # https://www.activebarcode.com/codes/checkdigit/modulo11
        # Calculate modulo 11
        parts_list = [int(digit) * (10 - index) for index, digit in enumerate(digits)]
        list_sum = sum(parts_list)

        # If checksum is 11, then it is zeroed out
        # If checksum is 10, then it should error out
        # Otherwise we do an equality check
        checksum = 11 - (list_sum % 11)
        if checksum == 11:
            checksum = 0

        return checksum == check_digit
