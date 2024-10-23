Feature: OAuth and Authentication

    @phase_two
    Scenario Outline: Confirm invalid or missing auth tokens are handled appropriately
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
        And the header Authorization is set to <header_value>
        And the header Content-Type is set to application/fhir+json
        And the X-Request-ID and X-Correlation-ID headers are set to UUIDs
        When the client POSTs the request body to /FHIR/R4/QuestionnaireResponse
        Then the Relationship Validation Service will return 401
        And the response will be JSON
        And the response will match the API Spec
        And the diagnostics Invalid access token - Access Denied. is present in the response
        And the system, version, severity and resourceType are correct in the response
        And the error code ACCESS_DENIED is present in the response
        And the code forbidden is present in the response
        And the display Missing or invalid OAuth 2.0 bearer token in request. is present in the response

        Examples:
        | header_value       |
        | missing key        |
        | empty value        |
        | invalid auth token |
