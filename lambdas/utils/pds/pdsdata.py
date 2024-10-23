"""
FHIR Patient Record Utility Functions

This module provides utility functions for extracting information from FHIR
Patient records in JSON format.
"""

from datetime import date, datetime
from typing import Optional

from dateutil.relativedelta import relativedelta
from fhirclient.models.codeableconcept import CodeableConcept
from fhirclient.models.fhirdate import FHIRDate
from fhirclient.models.patient import Patient
from fhirclient.models.period import Period
from fhirclient.models.relatedperson import RelatedPerson


def get_patient_age(patient: Patient) -> Optional[int]:
    """
    Determines the age of the supplied patient in whole years.

    Args:
        patient (Patient): The patient for whom the age needs to be determined.

    Returns:
        int: Patient age in years,
        or None if the date of birth is invalid or missing.
    """

    # The underlying library will convert a partial date into a isodate
    # As such, no additonal validation/parsing needs to be done
    #
    # From isodate.parse_date :
    # Parse an ISO 8601 date string into a datetime.date object.

    # As the datetime.date implementation is limited to dates starting from
    # 0001-01-01, negative dates (BC) and year 0 can not be parsed by this
    # method.

    # For incomplete dates, this method chooses the first day for it. For
    # instance if only a century is given, this method returns the 1st of
    # January in year 1 of this century.

    # supported formats: (expanded formats are shown with 6 digits for year)
    #     YYYYMMDD    +-YYYYYYMMDD      basic complete date
    #     YYYY-MM-DD  +-YYYYYY-MM-DD    extended complete date
    #     YYYYWwwD    +-YYYYYYWwwD      basic complete week date
    #     YYYY-Www-D  +-YYYYYY-Www-D    extended complete week date
    #     YYYYDDD     +-YYYYYYDDD       basic ordinal date
    #     YYYY-DDD    +-YYYYYY-DDD      extended ordinal date
    #     YYYYWww     +-YYYYYYWww       basic incomplete week date
    #     YYYY-Www    +-YYYYYY-Www      extended incomplete week date
    #     YYYMM       +-YYYYYYMM        basic incomplete month date
    #     YYY-MM      +-YYYYYY-MM       incomplete month date
    #     YYYY        +-YYYYYY          incomplete year date
    #     YY          +-YYYY            incomplete century date

    age = None
    bday = patient.birthDate

    if bday is not None and isinstance(bday, FHIRDate):
        today = datetime.now()
        # using relative delta to calculate as it accounts for leap days
        # better than manually calculating years and days minus now
        age = relativedelta(dt1=today, dt2=bday.date).years

    return age


def get_is_person_deceased(patient: Patient) -> bool:
    """
    Determines if a person is deceased based on the presence of deceasedBoolean flag
    in the FHIR Patient record.

    Args:
        pds_data (dict): The FHIR Patient record.

    Returns:
        bool: True if the person is deceased, False otherwise.
    """
    if patient.deceasedBoolean is not None:
        return patient.deceasedBoolean

    dday = patient.deceasedDateTime
    return isinstance(dday, FHIRDate) and isinstance(dday.date, date)


def get_security_code(patient: Patient) -> Optional[str]:
    """
    Returns the security code associated with the record.

    Args:
        pds_data (dict): The FHIR Patient record.

    Returns:
        str or None: The security code if present, or None if not found.
    """
    rtn = None

    if patient.meta is not None and patient.meta.security is not None:
        rtn = patient.meta.security[0].code

    return rtn


def get_relationship(related: RelatedPerson) -> list[str]:
    """
    Returns the relationship from the related person record

    Args:
        related (RelatedPerson): The FHIR related person record.

    Returns:
        list[str]: The relationship(s) or empty list
    """

    rtn = []

    # If the supplied data is not present
    if related is None:
        return rtn
    # If the relationship is not active
    if related.active is not None and related.active == False:
        return rtn
    # If period is not active
    if __is_period_range_in_past(related.period):
        return rtn
    # If relationship record are not present
    if related.relationship is None:
        return rtn

    rtn = __extract_code_from_codeable(related.relationship)

    return rtn


def __is_period_range_in_past(dp: Period) -> bool:
    """
    Determines if the period is active and if its already passed.
    A None value will result in true.

    Args:
        date (Period): Date value to evaluate

    Returns:
        bool: True if the period has passed or not yet started, false otherwise
    """
    dt = date.today()
    rtn = False
    if dp is None:
        # date is not defined
        # NPA-2374
        # Following discussion with PDS this needs to be treated
        # as a valid active relationship
        rtn = False
    elif (
        # end date has already passed
        (dp.end is not None and dp.end.date is not None and dp.end.date < dt)
        or
        # start date has not yet started
        (dp.start is None or dp.start.date is None or dp.start.date > dt)
    ):
        rtn = True

    return rtn


def __extract_code_from_codeable(codeables: list[CodeableConcept]):
    """
    Extracts the list of 'code' values from the parameters

    Args:
        codeables (list[CodeableConcept]): list of values to iterate over

    Returns:
        _type_: list of code values or blank if no values found
    """
    rtn = []
    for code in codeables:
        if code.coding is not None and len(code.coding) > 0:
            for coding in code.coding:
                if coding.code is not None:
                    rtn.append(coding.code)

    return rtn
