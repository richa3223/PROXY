"""Collection of errors objects for Validation"""

from http import HTTPStatus
from typing import TypedDict


class ErrorProxyValidation(TypedDict):
    """Represents the structure of an error response for proxy validation."""

    http_status: int
    eligibility: bool
    response_code: str
    validation_code: str
    audit_details_type: str
    audit_msg: str
    relationship_type: str


AUDIT_DETAILS = {
    "VALIDATION_SUCCESS": "Validation Successful",
    "VALIDATION_FAIL": "Validation Failed",
    "VALIDATION_ERROR": "Validation Errored",
}

# All rules met
VALIDATED_PROXY: ErrorProxyValidation = {
    "http_status": HTTPStatus.OK,
    "eligibility": True,
    "response_code": "VALIDATED_PROXY",
    "validation_code": "VALIDATED_PROXY",
    "audit_details_type": AUDIT_DETAILS["VALIDATION_SUCCESS"],
    "audit_msg": "Validated Proxy",
    "relationship_type": "",
}

#
PROXY_NO_RELATIONSHIPS_FOUND: ErrorProxyValidation = {
    "http_status": HTTPStatus.OK,
    "eligibility": False,
    "response_code": "PROXY_NO_RELATIONSHIPS_FOUND",
    "validation_code": "PROXY_NO_RELATIONSHIPS_FOUND",
    "audit_details_type": AUDIT_DETAILS["VALIDATION_FAIL"],
    "audit_msg": "Unable to validate: no proxy relationships on PDS",
    "relationship_type": "",
}

# Request unknown proxy record / Proxy not recorded on PDS
PROXY_NOT_FOUND: ErrorProxyValidation = {
    "http_status": HTTPStatus.OK,
    "eligibility": False,
    "response_code": "PROXY_NOT_FOUND",
    "validation_code": "PROXY_NOT_FOUND",
    "audit_details_type": AUDIT_DETAILS["VALIDATION_FAIL"],
    "audit_msg": "Unable to validate: no proxy record on PDS",
    "relationship_type": "",
}

# Request record for proxy that hasn't provided consent to share data / Proxy "S Flagged"
NO_PROXY_CONSENT: ErrorProxyValidation = {
    "http_status": HTTPStatus.OK,
    "eligibility": False,
    "response_code": "NO_PROXY_CONSENT",
    "validation_code": "NO_PROXY_CONSENT",
    "audit_details_type": AUDIT_DETAILS["VALIDATION_FAIL"],
    "audit_msg": "Unable to validate: proxy restricted record (-S)",
    "relationship_type": "",
}

# Proxy recorded as deceased
PROXY_DECEASED: ErrorProxyValidation = {
    "http_status": HTTPStatus.OK,
    "eligibility": False,
    "response_code": "PROXY_DECEASED",
    "validation_code": "PROXY_DECEASED",
    "audit_details_type": AUDIT_DETAILS["VALIDATION_FAIL"],
    "audit_msg": "Unable to validate: proxy is recorded as deceased on PDS",
    "relationship_type": "",
}

# Patient recorded as deceased
PATIENT_DECEASED: ErrorProxyValidation = {
    "http_status": HTTPStatus.OK,
    "eligibility": False,
    "response_code": "PATIENT_DECEASED",
    "validation_code": "PATIENT_DECEASED",
    "audit_details_type": AUDIT_DETAILS["VALIDATION_FAIL"],
    "audit_msg": "Validation failed: patient is recorded as deceased on PDS",
    "relationship_type": "",
}

# Patient age over 13
PATIENT_NOT_ELIGIBLE_OVER_13 = {
    "http_status": HTTPStatus.OK,
    "eligibility": False,
    "response_code": "NOT_ELIGIBLE",
    "validation_code": "PATIENT_NOT_ELIGIBLE_AGE",
    "audit_details_type": AUDIT_DETAILS["VALIDATION_FAIL"],
    "audit_msg": "Validation failed: patient not eligible - over 13",
    "relationship_type": "",
}

# Error when requesting patient record or patient not found
PATIENT_NOT_FOUND = {
    "http_status": HTTPStatus.OK,
    "eligibility": False,
    "response_code": "PATIENT_NOT_FOUND",
    "validation_code": "PATIENT_NOT_FOUND",
    "audit_details_type": AUDIT_DETAILS["VALIDATION_FAIL"],
    "audit_msg": "Validation failed: get PDS patient did not match a record in PDS",
    "relationship_type": "",
}

# Error when relationship lookup failed
RELATION_NOT_FOUND = {
    "http_status": HTTPStatus.OK,
    "eligibility": False,
    "response_code": "PATIENT_NO_RELATIONSHIPS_FOUND",
    "validation_code": "PATIENT_NO_RELATIONSHIPS_FOUND",
    "audit_details_type": AUDIT_DETAILS["VALIDATION_FAIL"],
    "audit_msg": "Unable to validate: no patient relationships on PDS",
    "relationship_type": "",
}

# A previous lambda provided a status that indicates failure
PATIENT_STATUS_FAIL = {
    "http_status": HTTPStatus.BAD_REQUEST,
    "eligibility": False,
    "response_code": "BAD_REQUEST - One or more previous operations failed",
    "validation_code": "BAD_REQUEST",
    "audit_details_type": AUDIT_DETAILS["VALIDATION_ERROR"],
    "audit_msg": "Unable to validate: get PDS patient failed",
    "relationship_type": "",
}

# A previous lambda provided a status that indicates failure
RELATION_STATUS_FAIL = {
    "http_status": HTTPStatus.BAD_REQUEST,
    "eligibility": False,
    "response_code": "BAD_REQUEST - One or more previous operations failed",
    "validation_code": "BAD_REQUEST",
    "audit_details_type": AUDIT_DETAILS["VALIDATION_ERROR"],
    "audit_msg": "Unable to validate: get PDS patient failed",
    "relationship_type": "",
}

# Request record for relationship is marked as Sensitive or restricted
NO_PATIENT_CONSENT: ErrorProxyValidation = {
    "http_status": HTTPStatus.OK,
    "eligibility": False,
    "response_code": "NO_PATIENT_CONSENT",
    "validation_code": "NO_PATIENT_CONSENT",
    "audit_details_type": AUDIT_DETAILS["VALIDATION_FAIL"],
    "audit_msg": "Validation failed: related person record is sensitive or restricted (-S)",
    "relationship_type": "",
}

# Relationship is not a valid
PATIENT_NOT_RELATED: ErrorProxyValidation = {
    "http_status": HTTPStatus.OK,
    "eligibility": False,
    "response_code": "PATIENT_NO_RELATIONSHIPS_FOUND",
    "validation_code": "PATIENT_NO_RELATIONSHIPS_FOUND",
    "audit_details_type": AUDIT_DETAILS["VALIDATION_FAIL"],
    "audit_msg": "Unable to validate: no patient relationships on PDS",
    "relationship_type": "",
}

# Relationship is validated
VALIDATED_RELATIONSHIP: ErrorProxyValidation = {
    "http_status": HTTPStatus.OK,
    "eligibility": True,
    "response_code": "VALIDATED_RELATIONSHIP",
    "validation_code": "VALIDATED_RELATIONSHIP",
    "audit_details_type": AUDIT_DETAILS["VALIDATION_SUCCESS"],
    "audit_msg": "Validated Relationship",
    "relationship_type": "",
}
