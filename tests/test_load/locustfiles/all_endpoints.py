"""
Runs load tests for all endpoints
"""

import uuid

from locust import HttpUser, task

from test_load.auth import get_bearer_token


class RelationshipValidationUser(HttpUser):
    """This class is responsible for running the load testing mock validation endpoint"""

    def on_start(self):
        self.bearer_token = get_bearer_token()
        self.client.headers.update(self.set_spec_headers())

    def set_spec_headers(self):
        return {
            "X-Request-ID": str(uuid.uuid4()),
            "X-Correlation-ID": str(uuid.uuid4()),
            "Content-Type": "application/fhir+json",
            "Authorization": f"Bearer {self.bearer_token}",
        }

    @task
    def relationship_validation(self) -> None:
        parameters = {
            "identifier": "9730675953",
            "patient:identifier": "9730676429",
            "_include": "RelatedPerson:patient",
        }
        self.client.get("/RelatedPerson", params=parameters)


class QuestionnaireResponseUser(HttpUser):
    """This class is responsible for running the load testing mock questionnaire response endpoint"""

    def on_start(self):
        self.bearer_token = get_bearer_token()
        self.client.headers.update(self.set_spec_headers())

    def set_spec_headers(self):
        return {
            "X-Request-ID": str(uuid.uuid4()),
            "X-Correlation-ID": str(uuid.uuid4()),
            "Content-Type": "application/fhir+json",
            "Authorization": f"Bearer {self.bearer_token}",
        }

    @task
    def questionnaire_response(self) -> None:
        kwargs = {
            "json": {
                "resourceType": "QuestionnaireResponse",
                "status": "completed",
                "authored": "2024-03-24T16:32:12.363Z",
                "source": {
                    "type": "RelatedPerson",
                    "identifier": {
                        "value": "9730675953",
                        "system": "https://fhir.nhs.uk/Id/nhs-number",
                    },
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
                                "answer": [{"valueString": "9730675953"}],
                            },
                            {
                                "linkId": "relationship",
                                "text": "Relationship",
                                "answer": [
                                    {
                                        "valueCoding": {
                                            "system": "http://terminology.hl7.org/CodeSystem/v3-RoleCode",
                                            "code": "PRN",
                                            "display": "???",
                                        }
                                    }
                                ],
                            },
                        ],
                    },
                    {
                        "linkId": "patient_details",
                        "text": "Patient details",
                        "item": [
                            {
                                "linkId": "nhs_number",
                                "text": "NHS Number",
                                "answer": [{"valueString": "9730676429"}],
                            },
                            {
                                "linkId": "first_name",
                                "text": "First Name",
                                "answer": [{"valueString": "David"}],
                            },
                            {
                                "linkId": "last_name",
                                "text": "Last name",
                                "answer": [{"valueString": "WOMACK"}],
                            },
                            {
                                "linkId": "date_of_birth",
                                "text": "Date of Birth",
                                "answer": [{"valueDate": "2018-06-24"}],
                            },
                            {
                                "linkId": "postcode",
                                "text": "Postcode",
                                "answer": [{"valueString": "DN17 2QS"}],
                            },
                        ],
                    },
                    {
                        "linkId": "requested_services",
                        "text": "Requested services",
                        "answer": [
                            {
                                "valueCoding": {
                                    "system": "http://terminology.hl7.org/CodeSystem/consentaction",
                                    "code": "appointments",
                                    "display": "???",
                                }
                            },
                            {
                                "valueCoding": {
                                    "system": "http://terminology.hl7.org/CodeSystem/consentaction",
                                    "code": "medicines",
                                    "display": "???",
                                }
                            },
                            {
                                "valueCoding": {
                                    "system": "http://terminology.hl7.org/CodeSystem/consentaction",
                                    "code": "records",
                                    "display": "???",
                                }
                            },
                            {
                                "valueCoding": {
                                    "system": "http://terminology.hl7.org/CodeSystem/consentaction",
                                    "code": "demographics",
                                    "display": "???",
                                }
                            },
                        ],
                    },
                ],
            }
        }
        self.client.post("/QuestionnaireResponse", **kwargs)
