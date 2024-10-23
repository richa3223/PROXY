Feature: Operation Outcome Tests
    @phase_two
    Scenario Outline: Call /QuestionnaireResponse with invalid FHIR QuestionnaireResponse
        Given A questionnaire response:
            {}
        And the Relationship Validation Service API is available
        And the client is authenticated with 9730675929
        And the header Content-Type is set to application/fhir+json
        And the X-Request-ID and X-Correlation-ID headers are set to UUIDs
        When the client POSTs the request body to /FHIR/R4/QuestionnaireResponse
        Then the Relationship Validation Service will return 400
        And the response will be JSON
        And the request will match the API Spec
        And the response will match the API Spec
        And the code invalid is present in the response
        And the system, version, severity and resourceType are correct in the response
        And the error code BAD_REQUEST is present in the response
        And the diagnostics The supplied input is not a valid FHIR QuestionnaireResponse. is present in the response

    @phase_two
    Scenario Outline: Call /QuestionnaireResponse with HTTP verbs returning content
        Given A questionnaire response:
            {
            "resourceType": "QuestionnaireResponse",
            "status": "completed",
            "authored": "2024-03-24T16:32:12.363Z",
            "source": {
            "type": "RelatedPerson",
            "identifier": {
                "value": "9000000001",
                "system": "https://fhir.nhs.uk/Id/nhs-number"
            }
            },
            "questionnaire": "Questionnaire/example-questionnaire",
            "item": [
                {
                "linkId": "proxy_details",
                "text": "Proxy details",
                "item": [
                    {
                    "linkId": "nhs_number",
                    "text": "NHS Number",
                    "answer": [
                        {
                        "valueString": "9000000001"
                        }
                    ]
                    },
                    {
                    "linkId": "relationship",
                    "text": "Relationship",
                    "answer": [
                        {
                        "valueCoding": {
                            "system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode",
                            "code": "PRN",
                            "display": "???"
                        }
                        }
                    ]
                    }
                ]
                },
                {
                "linkId": "patient_details",
                "text": "Patient details",
                "item": [
                    {
                    "linkId": "nhs_number",
                    "text": "NHS Number",
                    "answer": [
                        {
                        "valueString": "9000000002"
                        }
                    ]
                    },
                    {
                    "linkId": "first_name",
                    "text": "First Name",
                    "answer": [
                        {
                        "valueString": "Timmy"
                        }
                    ]
                    },
                    {
                    "linkId": "last_name",
                    "text": "Last name",
                    "answer": [
                        {
                        "valueString": "Tenenbaum"
                        }
                    ]
                    },
                    {
                    "linkId": "date_of_birth",
                    "text": "Date of Birth",
                    "answer": [
                        {
                        "valueDate": "2020-10-22"
                        }
                    ]
                    },
                    {
                    "linkId": "postcode",
                    "text": "Postcode",
                    "answer": [
                        {
                        "valueString": "LS1 4AP"
                        }
                    ]
                    }
                ]
                },
                {
                "linkId": "requested_services",
                "text": "Requested services",
                "answer": [
                    {
                        "valueCoding": {
                            "system": "http://terminology.hl7.org/CodeSystem/consentaction",
                            "code": "appointments",
                            "display": ""
                        }
                    }
                ]
                }
            ]
            }
        And the Relationship Validation Service API is available
        And the client is authenticated with 9730675929
        And the header Content-Type is set to application/fhir+json
        And the X-Request-ID and X-Correlation-ID headers are set to UUIDs
        When the client <verb>s the request body to /FHIR/R4/QuestionnaireResponse
        Then the Relationship Validation Service will return <status_code>
        And the response will be JSON
        And the error code METHOD_NOT_ALLOWED is present in the response
        And the display The method is not allowed. is present in the response
        And the diagnostics The method is not allowed for the requested resource. is present in the response
        And the system, version, severity and resourceType are correct in the response

    Examples:
        | identifier | verb    | status_code |
        | 9730675929 | DELETE  | 405         |
        | 9730675929 | OPTIONS | 405         |
        | 9730675929 | PATCH   | 405         |
        | 9730675929 | GET     | 405         |
        | 9730675929 | PUT     | 405         |

    @phase_two
    Scenario Outline: Call /QuestionnaireResponse with HTTP verbs returning no content
        Given A questionnaire response:
            {
            "resourceType": "QuestionnaireResponse",
            "status": "completed",
            "authored": "2024-03-24T16:32:12.363Z",
            "source": {
            "type": "RelatedPerson",
            "identifier": {
                "value": "9000000001",
                "system": "https://fhir.nhs.uk/Id/nhs-number"
            }
            },
            "questionnaire": "Questionnaire/example-questionnaire",
            "item": [
                {
                "linkId": "proxy_details",
                "text": "Proxy details",
                "item": [
                    {
                    "linkId": "nhs_number",
                    "text": "NHS Number",
                    "answer": [
                        {
                        "valueString": "9000000001"
                        }
                    ]
                    },
                    {
                    "linkId": "relationship",
                    "text": "Relationship",
                    "answer": [
                        {
                        "valueCoding": {
                            "system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode",
                            "code": "PRN",
                            "display": "???"
                        }
                        }
                    ]
                    }
                ]
                },
                {
                "linkId": "patient_details",
                "text": "Patient details",
                "item": [
                    {
                    "linkId": "nhs_number",
                    "text": "NHS Number",
                    "answer": [
                        {
                        "valueString": "9000000002"
                        }
                    ]
                    },
                    {
                    "linkId": "first_name",
                    "text": "First Name",
                    "answer": [
                        {
                        "valueString": "Timmy"
                        }
                    ]
                    },
                    {
                    "linkId": "last_name",
                    "text": "Last name",
                    "answer": [
                        {
                        "valueString": "Tenenbaum"
                        }
                    ]
                    },
                    {
                    "linkId": "date_of_birth",
                    "text": "Date of Birth",
                    "answer": [
                        {
                        "valueDate": "2020-10-22"
                        }
                    ]
                    },
                    {
                    "linkId": "postcode",
                    "text": "Postcode",
                    "answer": [
                        {
                        "valueString": "LS1 4AP"
                        }
                    ]
                    }
                ]
                },
                {
                "linkId": "requested_services",
                "text": "Requested services",
                "answer": [
                    {
                        "valueCoding": {
                            "system": "http://terminology.hl7.org/CodeSystem/consentaction",
                            "code": "appointments",
                            "display": ""
                        }
                    }
                ]
                }
            ]
            }
        And the Relationship Validation Service API is available
        And the client is authenticated with 9730675929
        And the X-Request-ID and X-Correlation-ID headers are set to UUIDs
        And the header Content-Type is set to application/fhir+json
        When the client <verb>s the request body to /FHIR/R4/QuestionnaireResponse
        Then the Relationship Validation Service will return <status_code>

    Examples:
        | verb | status_code |
        | HEAD | 405         |

    @phase_two
    Scenario Outline: Check invalid URL returns a 404 for QuestionnaireResponse
        Given A questionnaire response:
            {
            "resourceType": "QuestionnaireResponse",
            "status": "completed",
            "authored": "2024-03-24T16:32:12.363Z",
            "source": {
            "type": "RelatedPerson",
            "identifier": {
                "value": "9000000001",
                "system": "https://fhir.nhs.uk/Id/nhs-number"
            }
            },
            "questionnaire": "Questionnaire/example-questionnaire",
            "item": [
                {
                "linkId": "proxy_details",
                "text": "Proxy details",
                "item": [
                    {
                    "linkId": "nhs_number",
                    "text": "NHS Number",
                    "answer": [
                        {
                        "valueString": "9000000001"
                        }
                    ]
                    },
                    {
                    "linkId": "relationship",
                    "text": "Relationship",
                    "answer": [
                        {
                        "valueCoding": {
                            "system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode",
                            "code": "PRN",
                            "display": "???"
                        }
                        }
                    ]
                    }
                ]
                },
                {
                "linkId": "patient_details",
                "text": "Patient details",
                "item": [
                    {
                    "linkId": "nhs_number",
                    "text": "NHS Number",
                    "answer": [
                        {
                        "valueString": "9000000002"
                        }
                    ]
                    },
                    {
                    "linkId": "first_name",
                    "text": "First Name",
                    "answer": [
                        {
                        "valueString": "Timmy"
                        }
                    ]
                    },
                    {
                    "linkId": "last_name",
                    "text": "Last name",
                    "answer": [
                        {
                        "valueString": "Tenenbaum"
                        }
                    ]
                    },
                    {
                    "linkId": "date_of_birth",
                    "text": "Date of Birth",
                    "answer": [
                        {
                        "valueDate": "2020-10-22"
                        }
                    ]
                    },
                    {
                    "linkId": "postcode",
                    "text": "Postcode",
                    "answer": [
                        {
                        "valueString": "LS1 4AP"
                        }
                    ]
                    }
                ]
                },
                {
                "linkId": "requested_services",
                "text": "Requested services",
                "answer": [
                    {
                        "valueCoding": {
                            "system": "http://terminology.hl7.org/CodeSystem/consentaction",
                            "code": "appointments",
                            "display": ""
                        }
                    }
                ]
                }
            ]
            }
        And the Relationship Validation Service API is available
        And the client is authenticated with 9730675929
        And the X-Request-ID and X-Correlation-ID headers are set to UUIDs
        And the header Content-Type is set to application/fhir+json
        When the client POSTs the request body to <path>
        Then the Relationship Validation Service will return 404
        And the response will be JSON
        And the system, version, severity and resourceType are correct in the response
        And the error code INVALIDATED_RESOURCE is present in the response
        And the code processing is present in the response
        And the display Resource that has been marked as invalid was requested - invalid resources cannot be retrieved is present in the response

    Examples:
        | path                                 |
        | %2FQuestionnaireResponse             |
        | %2FFHIR%2FR3%2FQuestionnaireResponse |
        | %2Ffhir%2Fr4%2FQuestionnaireResponse |
        | %2FFHIR%2FR4%2FQUESTIONNAIRERESPONSE |
        | %2FFHIR%2FR4%2Fquestionnaireresponse |


    @phase_two
    Scenario Outline: Call /QuestionnaireResponse with incorrect Content-Type
        Given A questionnaire response:
            {
            "resourceType": "QuestionnaireResponse",
            "status": "completed",
            "authored": "2024-03-24T16:32:12.363Z",
            "source": {
            "type": "RelatedPerson",
            "identifier": {
                "value": "9000000001",
                "system": "https://fhir.nhs.uk/Id/nhs-number"
            }
            },
            "questionnaire": "Questionnaire/example-questionnaire",
            "item": [
                {
                "linkId": "proxy_details",
                "text": "Proxy details",
                "item": [
                    {
                    "linkId": "nhs_number",
                    "text": "NHS Number",
                    "answer": [
                        {
                        "valueString": "9000000001"
                        }
                    ]
                    },
                    {
                    "linkId": "relationship",
                    "text": "Relationship",
                    "answer": [
                        {
                        "valueCoding": {
                            "system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode",
                            "code": "PRN",
                            "display": "???"
                        }
                        }
                    ]
                    }
                ]
                },
                {
                "linkId": "patient_details",
                "text": "Patient details",
                "item": [
                    {
                    "linkId": "nhs_number",
                    "text": "NHS Number",
                    "answer": [
                        {
                        "valueString": "9000000002"
                        }
                    ]
                    },
                    {
                    "linkId": "first_name",
                    "text": "First Name",
                    "answer": [
                        {
                        "valueString": "Timmy"
                        }
                    ]
                    },
                    {
                    "linkId": "last_name",
                    "text": "Last name",
                    "answer": [
                        {
                        "valueString": "Tenenbaum"
                        }
                    ]
                    },
                    {
                    "linkId": "date_of_birth",
                    "text": "Date of Birth",
                    "answer": [
                        {
                        "valueDate": "2020-10-22"
                        }
                    ]
                    },
                    {
                    "linkId": "postcode",
                    "text": "Postcode",
                    "answer": [
                        {
                        "valueString": "LS1 4AP"
                        }
                    ]
                    }
                ]
                },
                {
                "linkId": "requested_services",
                "text": "Requested services",
                "answer": [
                    {
                        "valueCoding": {
                            "system": "http://terminology.hl7.org/CodeSystem/consentaction",
                            "code": "appointments",
                            "display": ""
                        }
                    }
                ]
                }
            ]
            }
        And the Relationship Validation Service API is available
        And the client is authenticated with 9730675929
        And the header Content-Type is set to <content_type>
        And the X-Request-ID and X-Correlation-ID headers are set to UUIDs
        When the client POSTs the request body to /FHIR/R4/QuestionnaireResponse
        Then the Relationship Validation Service will return 415
        And the response will be JSON
        And the error code UNSUPPORTED_MEDIA_TYPE is present in the response
        And the display Unsupported Media Type. is present in the response
        And the diagnostics Unsupported Media Type. is present in the response
        And the system, version, severity and resourceType are correct in the response

    Examples:
        | content_type                                           |
        | application%2Fjson                                     |
        | application%2Ffhir                                     |
        | application%2Fxml                                      |
        | application%2Ffhir%2Bjson%3B%20charset%3DWindows-1252  |
        | empty value                                            |


    @phase_two
    Scenario Outline: Test malformed JSON request body
        Given the Relationship Validation Service API is available
        And the client is authenticated with 9730675929
        And the header Content-Type is set to application/fhir+json
        And the X-Request-ID and X-Correlation-ID headers are set to UUIDs
        When the client POSTs body: { to /FHIR/R4/QuestionnaireResponse
        Then the Relationship Validation Service will return 400
        And the response will be JSON
        And the response will match the API Spec
        And the error code BAD_REQUEST is present in the response
        And the display The request could not be processed. is present in the response
        And the diagnostics The supplied input is not a valid FHIR QuestionnaireResponse. is present in the response
        And the system, version, severity and resourceType are correct in the response
