"""Collection of errors string for the PDS Lambdas"""

from http import HTTPStatus
from typing import Optional, TypedDict

ERROR_NHS_NUMBER_REQUIRED = "NHS Number is required."
ERROR_AUTH_TKN_REQUIRED = "Authentication token is required."

ERROR_NHS_NUMBER_INVALID = "NHS Number is not valid."
ERROR_AUTH_TKN_INVALID = "Supplied authentication token is not valid."

ERROR_UNAUTHORIZED = "Access Denied - Unauthorised."
ERROR_RECORD_NOT_FOUND = "Record Not Found."

ERROR_OPERATION_FAILED = "Request Failed - Unexpected Error"

OPERATIONAL_OUTCOME_SYSTEM = (
    "https://fhir.nhs.uk/R4/CodeSystem/ValidatedRelationships-ErrorOrWarningCode"
)
OPERATIONAL_OUTCOME_VERSION = "1"
OPERATIONAL_OUTCOME_SEVERITY_ERROR = "error"

OPERATIONAL_OUTCOME_DISPLAY_FAILED = "Failed to generate response"

OPERATIONAL_OUTCOME_ISSUE_CODE_EXCEPTION = "exception"
OPERATIONAL_OUTCOME_ISSUE_CODE_REQUIRED = "required"
OPERATIONAL_OUTCOME_ISSUE_CODE_FORBIDDEN = "forbidden"
OPERATIONAL_OUTCOME_ISSUE_CODE_INVALID = "invalid"

BAD_REQUEST = "BAD_REQUEST"


class OperationalOutcomeResult(TypedDict):
    http_status: HTTPStatus
    response_code: str
    audit_msg: str
    system: str
    version: str
    display: str
    severity: str
    issue_code: str

    @staticmethod
    def create_operation_outcome_result_from_event(error_json: dict):
        error_http_status = error_json.get("http_status")
        error_response_code = error_json.get("response_code")
        error_audit_msg = error_json.get("audit_msg")
        error_system = error_json.get("system", OPERATIONAL_OUTCOME_SYSTEM)
        error_version = error_json.get("version", OPERATIONAL_OUTCOME_VERSION)
        error_display = error_json.get("display")
        error_severity = error_json.get("severity", OPERATIONAL_OUTCOME_SEVERITY_ERROR)
        error_issue_code = error_json.get(
            "issue_code", OPERATIONAL_OUTCOME_ISSUE_CODE_EXCEPTION
        )

        rtn: OperationalOutcomeResult = {
            "http_status": error_http_status,
            "response_code": error_response_code,
            "audit_msg": error_audit_msg,
            "system": error_system,
            "version": error_version,
            "display": error_display,
            "severity": error_severity,
            "issue_code": error_issue_code,
        }

        return rtn


# General error
INTERNAL_SERVER_ERROR: OperationalOutcomeResult = {
    "http_status": HTTPStatus.INTERNAL_SERVER_ERROR,
    "response_code": "SERVER_ERROR",
    "audit_msg": "Internal Server Error - Failed to generate response",
    "system": OPERATIONAL_OUTCOME_SYSTEM,
    "version": OPERATIONAL_OUTCOME_VERSION,
    "display": OPERATIONAL_OUTCOME_DISPLAY_FAILED,
    "severity": OPERATIONAL_OUTCOME_SEVERITY_ERROR,
    "issue_code": OPERATIONAL_OUTCOME_ISSUE_CODE_INVALID,
}

FORBIDDEN: OperationalOutcomeResult = {
    "http_status": HTTPStatus.FORBIDDEN,
    "response_code": "FORBIDDEN",
    "audit_msg": "Access denied to resource.",
    "system": OPERATIONAL_OUTCOME_SYSTEM,
    "version": OPERATIONAL_OUTCOME_VERSION,
    "display": "Access Denied",
    "severity": OPERATIONAL_OUTCOME_SEVERITY_ERROR,
    "issue_code": OPERATIONAL_OUTCOME_ISSUE_CODE_FORBIDDEN,
}

INSUFFICIENT_AUTH_LEVEL: OperationalOutcomeResult = {
    "http_status": HTTPStatus.UNAUTHORIZED,
    "response_code": "FORBIDDEN",
    "audit_msg": "Insufficient authorisation to access resource - requires P9.",
    "system": OPERATIONAL_OUTCOME_SYSTEM,
    "version": OPERATIONAL_OUTCOME_VERSION,
    "display": "Access Denied",
    "severity": OPERATIONAL_OUTCOME_SEVERITY_ERROR,
    "issue_code": OPERATIONAL_OUTCOME_ISSUE_CODE_FORBIDDEN,
}

# Header X-Correlation-ID is not a valid UUID
HEADER_INVALID_CORRELATION_ID: OperationalOutcomeResult = {
    "http_status": HTTPStatus.BAD_REQUEST,
    "response_code": BAD_REQUEST,
    "audit_msg": "Invalid request with error - X-Correlation-ID header invalid",
    "system": OPERATIONAL_OUTCOME_SYSTEM,
    "version": OPERATIONAL_OUTCOME_VERSION,
    "display": "Required header parameter(s) are invalid.",
    "severity": OPERATIONAL_OUTCOME_SEVERITY_ERROR,
    "issue_code": OPERATIONAL_OUTCOME_ISSUE_CODE_INVALID,
}

# Header X-Request-ID is missing in API request
HEADER_MISSING_REQUEST_ID: OperationalOutcomeResult = {
    "http_status": HTTPStatus.BAD_REQUEST,
    "response_code": BAD_REQUEST,
    "audit_msg": "Invalid request with error - X-Request-ID header not found.",
    "system": OPERATIONAL_OUTCOME_SYSTEM,
    "version": OPERATIONAL_OUTCOME_VERSION,
    "display": "Required header parameter(s) are missing.",
    "severity": OPERATIONAL_OUTCOME_SEVERITY_ERROR,
    "issue_code": OPERATIONAL_OUTCOME_ISSUE_CODE_INVALID,
}

# Header X-Request-ID is not a valid UUID
HEADER_INVALID_REQUEST_ID: OperationalOutcomeResult = {
    "http_status": HTTPStatus.BAD_REQUEST,
    "response_code": BAD_REQUEST,
    "audit_msg": "Invalid request with error - X-Request-ID header invalid",
    "system": OPERATIONAL_OUTCOME_SYSTEM,
    "version": OPERATIONAL_OUTCOME_VERSION,
    "display": "Required header parameter(s) are invalid.",
    "severity": OPERATIONAL_OUTCOME_SEVERITY_ERROR,
    "issue_code": OPERATIONAL_OUTCOME_ISSUE_CODE_INVALID,
}

# Invalid Identifier System
INVALID_IDENTIFIER_SYSTEM: OperationalOutcomeResult = {
    "http_status": HTTPStatus.BAD_REQUEST,
    "response_code": "INVALID_IDENTIFIER_SYSTEM",
    "audit_msg": "The identifier system is not valid.",
    "system": OPERATIONAL_OUTCOME_SYSTEM,
    "version": OPERATIONAL_OUTCOME_VERSION,
    "display": "Invalid identifier system",
    "severity": OPERATIONAL_OUTCOME_SEVERITY_ERROR,
    "issue_code": OPERATIONAL_OUTCOME_ISSUE_CODE_INVALID,
}

# Identifier is missing in API request
MISSING_IDENTIFIER_VALUE: OperationalOutcomeResult = {
    "http_status": HTTPStatus.BAD_REQUEST,
    "response_code": "MISSING_IDENTIFIER_VALUE",
    "audit_msg": "The 'identifier' parameter is required",
    "system": OPERATIONAL_OUTCOME_SYSTEM,
    "version": OPERATIONAL_OUTCOME_VERSION,
    "display": "Missing RelatedPerson NHS number.",
    "severity": OPERATIONAL_OUTCOME_SEVERITY_ERROR,
    "issue_code": OPERATIONAL_OUTCOME_ISSUE_CODE_INVALID,
}

# Identifier is not a valid NHS Number
INVALID_IDENTIFIER_VALUE: OperationalOutcomeResult = {
    "http_status": HTTPStatus.BAD_REQUEST,
    "response_code": "INVALID_IDENTIFIER_VALUE",
    "audit_msg": "Not a valid NHS Number provided for the 'identifier' parameter",
    "system": OPERATIONAL_OUTCOME_SYSTEM,
    "version": OPERATIONAL_OUTCOME_VERSION,
    "display": "Provided value is invalid",
    "severity": OPERATIONAL_OUTCOME_SEVERITY_ERROR,
    "issue_code": OPERATIONAL_OUTCOME_ISSUE_CODE_INVALID,
}

# Patient:identifier is not a valid NHS Number
INVALID_PATIENT_IDENTIFIER_VALUE: OperationalOutcomeResult = {
    "http_status": HTTPStatus.BAD_REQUEST,
    "response_code": "INVALID_PATIENT_IDENTIFIER_VALUE",
    "audit_msg": "Not a valid NHS Number provided for the 'patient:identifier' parameter",
    "system": OPERATIONAL_OUTCOME_SYSTEM,
    "version": OPERATIONAL_OUTCOME_VERSION,
    "display": "Provided value is invalid",
    "severity": OPERATIONAL_OUTCOME_SEVERITY_ERROR,
    "issue_code": OPERATIONAL_OUTCOME_ISSUE_CODE_INVALID,
}

# Identifier not set but patient:identifier is set
NOT_SUPPORTED: OperationalOutcomeResult = {
    "http_status": HTTPStatus.BAD_REQUEST,
    "response_code": "NOT_SUPPORTED",
    "audit_msg": "The request is not currently supported.",
    "system": OPERATIONAL_OUTCOME_SYSTEM,
    "version": OPERATIONAL_OUTCOME_VERSION,
    "display": "The request is not currently supported.",
    "severity": OPERATIONAL_OUTCOME_SEVERITY_ERROR,
    "issue_code": "not-supported",
}
