Feature: Receive Questionnaire Response
    @phase_two
    Scenario Outline: A Questionnaire Response
        Given A questionnaire response:
            {
                "resourceType": "QuestionnaireResponse",
                "status": "completed",
                "authored": "2024-03-24T16:32:12.363Z",
                "source": {
                    "type": "RelatedPerson",
                    "identifier": {
                    "value": "<related_person_nhs_number>",
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
                            "valueString": "<proxy_nhs_number>"
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
                                "code": "<relationship_code>",
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
                            "valueString": "<patient_nhs_number>"
                            }
                        ]
                        },
                        {
                        "linkId": "first_name",
                        "text": "First Name",
                        "answer": [
                            {
                            "valueString": "<first_name>"
                            }
                        ]
                        },
                        {
                        "linkId": "last_name",
                        "text": "Last name",
                        "answer": [
                            {
                            "valueString": "<last_name>"
                            }
                        ]
                        },
                        {
                        "linkId": "date_of_birth",
                        "text": "Date of Birth",
                        "answer": [
                            {
                            "valueDate": "<date_of_birth>"
                            }
                        ]
                        },
                        {
                        "linkId": "postcode",
                        "text": "Postcode",
                        "answer": [
                            {
                            "valueString": "<postcode>"
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
                            "code": "<requested_services.valueCoding.codes>",
                            "display": "???"
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
        Then the Relationship Validation Service will return 200
        And the response will be JSON
        And the request will match the API Spec
        And the response will match the API Spec
        And the resourceType OperationOutcome is present in the response
        And the severity information is present in the response
        And the code informational is present in the response
        And the details include a dynamic reference code

        Examples:
            | content_type                                   |related_person_nhs_number|proxy_nhs_number|relationship_code|patient_nhs_number|first_name|last_name|date_of_birth|postcode|requested_services.valueCoding.codes       |
            | application%2Ffhir%2Bjson%20                   |               9730675929|      9730675929|              PRN|        9730676399|     David|WOMACK   |   2018-06-24|DN17 2QS|appointments,medicines,records,demographics|
            | application%2Ffhir%2Bjson%20                   |               9730675988|      9730675988|         Personal|        9730676445|    Joanna|   FILSON|   2011-02-28|DN19 7SU|appointments,medicines,records,demographics|
            | application%2Ffhir%2Bjson%3B%20charset%3Dutf-8 |               9730675929|      9730675929|              PRN|        9730676399|     David|WOMACK   |   2018-06-24|DN17 2QS|appointments,medicines,records,demographics|
            | application%2Ffhir%2Bjson%3B%20charset%3Dutf-8 |               9730675988|      9730675988|         Personal|        9730676445|    Joanna|   FILSON|   2011-02-28|DN19 7SU|appointments,medicines,records,demographics|

    # Unskip when LPA is added to the API Spec
    # Note the JSON may be invalid. Please validate before running
    @phase_two @skip
    Scenario: A Questionnaire Response with an LPA Access Code
        Given A questionnaire response:
            {
                "resourceType": "QuestionnaireResponse",
                "status": "completed",
                "authored": "2024-03-24T16:32:12.363Z",
                "source": {
                    "type": "RelatedPerson",
                    "identifier": "9876543210"
                },
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
                            "valueString": "9876543210"
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
                                "code": "HPOWATT",
                                "display": "Health Power of Attorney"
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
                            "valueString": "9000000008"
                            }
                        ]
                        },
                        {
                        "linkId": "first_name",
                        "text": "First Name",
                        "answer": [
                            {
                            "valueString": "Florence"
                            }
                        ]
                        },
                        {
                        "linkId": "last_name",
                        "text": "Last name",
                        "answer": [
                            {
                            "valueString": "Smith"
                            }
                        ]
                        },
                        {
                        "linkId": "date_of_birth",
                        "text": "Date of Birth",
                        "answer": [
                            {
                            "valueDate": "1935-01-02"
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
                    "linkId": "lpa_access_code",
                    "text": "LPA access code",
                    "answer": [
                        {
                        "valueString": "X123456"
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
                            "display": "manage appointments"
                        }
                        },
                        {
                        "valueCoding": {
                            "system": "http://terminology.hl7.org/CodeSystem/consentaction",
                            "code": "medicines",
                            "display": "manage medicines"
                        }
                        },
                        {
                        "valueCoding": {
                            "system": "http://terminology.hl7.org/CodeSystem/consentaction",
                            "code": "records",
                            "display": "access medical records"
                        }
                        },
                        {
                        "valueCoding": {
                            "system": "http://terminology.hl7.org/CodeSystem/consentaction",
                            "code": "demographics",
                            "display": "manage demographics and contact details"
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
        When the client POSTs the request body to /FHIR/R4/QuestionnaireResponse
        Then the Relationship Validation Service will return 200
        And the response will be JSON
        And the request will match the API Spec
        And the response will match the API Spec
        And the resourceType OperationOutcome is present in the response
        And the severity information is present in the response
        And the code informational is present in the response
        And the details include a dynamic reference code
