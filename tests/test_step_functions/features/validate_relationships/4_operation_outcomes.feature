Feature: Operation Outcome Tests for the validate_relationship_state_machine step function

  Scenario Outline: Check missing and invalid requestId
    Given a state machine input JSON:
        {
            "proxyNhsNumber": "9730675988",
            "patientNhsNumber": "9730676445",
            "_include": "",
            "correlationId": "e608c0dc-3c05-4e77-876b-326da36219d8",
            "requestId": "e26470b0-1e84-4d46-94d0-394b8ae3136e",
            "originalRequestUrl": "validated-relationships-service-dev.national.nhs.uk"
        }
    And the key <key> is set to <value>
    When the step function validate-relationships-state-machine is called
    Then the step function will return <status_code>
    And the response will be JSON
    And the diagnostics <diagnostics> is present in the response
    And the system, version, severity and resourceType are correct in the response
    And the error code <error_code> is present in the response
    And the code <code> is present in the response
    And the display <display> is present in the response

    Examples:
      | key           | value                           | status_code | diagnostics                                                  | error_code  | code    | display                                   |
      | requestId     | missing key                     | 400         | Invalid request with error - X-Request-ID header not found.  | BAD_REQUEST | invalid | Required header parameter(s) are missing. | # missing X-Request-ID key
      | requestId     | empty value                     | 400         | Invalid request with error - X-Request-ID header not found.  | BAD_REQUEST | invalid | Required header parameter(s) are missing. | # empty X-Request-ID value
      | requestId     | invalid X-Request-ID header     | 400         | Invalid request with error - X-Request-ID header invalid     | BAD_REQUEST | invalid | Required header parameter(s) are invalid. | # invalid X-Request-ID value
      | requestId     | 1000 characters                 | 400         | Invalid request with error - X-Request-ID header invalid     | BAD_REQUEST | invalid | Required header parameter(s) are invalid. | # invalid 1000 chars X-Request-ID value
      | requestId     | null                            | 400         | Invalid request with error - X-Request-ID header not found.  | BAD_REQUEST | invalid | Required header parameter(s) are missing. | # null X-Request-ID value
      | correlationId | invalid X-Correlation-ID header | 400         | Invalid request with error - X-Correlation-ID header invalid | BAD_REQUEST | invalid | Required header parameter(s) are invalid. | # invalid X-Correlation-ID key
      | correlationId | 1000 characters                 | 400         | Invalid request with error - X-Correlation-ID header invalid | BAD_REQUEST | invalid | Required header parameter(s) are invalid. | # invalid 1000 X-Correlation-ID key


  Scenario Outline: Check invalid identifier and patient identifier query parameter requests (No _include parameter)
    Given a state machine input JSON:
        {
            "proxyNhsNumber": "<identifier>",
            "patientNhsNumber": "<patient_identifier>",
            "_include": "",
            "correlationId": "e608c0dc-3c05-4e77-876b-326da36219d8",
            "requestId": "e26470b0-1e84-4d46-94d0-394b8ae3136e",
            "originalRequestUrl": "validated-relationships-service-dev.national.nhs.uk"
        }
    When the step function validate-relationships-state-machine is called
    Then the step function will return <status_code>
    And the response will be JSON
    And the diagnostics <diagnostics> is present in the response
    And the system, version, severity and resourceType are correct in the response
    And the error code <error_code> is present in the response
    And the code <code> is present in the response
    And the display <display> is present in the response

    Examples:
      | identifier                                                  | patient_identifier                                        | status_code | diagnostics                                                            | error_code                       | code    | display                           |
      | https%3A%2F%2Ffhir.nhs.uk%2FId%2Fnhs-number%2F%7C9730675988 | 9730676445                                                | 400         | The identifier system is not valid.                                    | INVALID_IDENTIFIER_SYSTEM        | invalid | Invalid identifier system         | # malformed identifier value identifier system
      | 9730675988                                                  | https%3A%2F%2Ffhir.nhs.uk%2Fid%2Fnhs-number%7C9730676445  | 400         | The identifier system is not valid.                                    | INVALID_IDENTIFIER_SYSTEM        | invalid | Invalid identifier system         | # malformed patient:identifier value identifier system
      | https%3A%2F%2Ffhir.nhs.uk%2FId%2FNhs-number%7C9730675988    | https%3A%2F%2FFhir.nhs.uk%2FId%2Fnhs-number%7C9730676445  | 400         | The identifier system is not valid.                                    | INVALID_IDENTIFIER_SYSTEM        | invalid | Invalid identifier system         | # malformed identifier and patient:identifier value identifier system
      | 9730675988                                                  | 9999999998                                                | 400         | Not a valid NHS Number provided for the 'patient:identifier' parameter | INVALID_PATIENT_IDENTIFIER_VALUE | invalid | Provided value is invalid         | # invalid patient identifier - invalid NHS number
      | 9730675988                                                  | https%3A%2F%2Ffhir.nhs.uk%2FId%2Fnhs-number%7C9999999998  | 400         | Not a valid NHS Number provided for the 'patient:identifier' parameter | INVALID_PATIENT_IDENTIFIER_VALUE | invalid | Provided value is invalid         | # invalid patient identifier - invalid NHS number
      | 9730675988                                                  | https%3A%2F%2FFhir.nhs.uk%2FId%2Fnhs-number%2F9730676445  | 400         | Not a valid NHS Number provided for the 'patient:identifier' parameter | INVALID_PATIENT_IDENTIFIER_VALUE | invalid | Provided value is invalid         | # invalid patient identifier - forward slash intead of pipe
      | 9730675988                                                  | 97306764459                                               | 400         | Not a valid NHS Number provided for the 'patient:identifier' parameter | INVALID_PATIENT_IDENTIFIER_VALUE | invalid | Provided value is invalid         | # invalid patient identifier - NHS number too long
      | 9730675988                                                  | 973067644                                                 | 400         | Not a valid NHS Number provided for the 'patient:identifier' parameter | INVALID_PATIENT_IDENTIFIER_VALUE | invalid | Provided value is invalid         | # invalid patient identifier - NHS number too short
      | 9730675988                                                  | https%3A%2F%2FFhir.nhs.uk%2FId%2Fnhs-number%7C97306764459 | 400         | Not a valid NHS Number provided for the 'patient:identifier' parameter | INVALID_PATIENT_IDENTIFIER_VALUE | invalid | Provided value is invalid         | # invalid patient identifier - NHS number too long
      | 9730675988                                                  | https%3A%2F%2FFhir.nhs.uk%2FId%2Fnhs-number%7C973067644   | 400         | Not a valid NHS Number provided for the 'patient:identifier' parameter | INVALID_PATIENT_IDENTIFIER_VALUE | invalid | Provided value is invalid         | # invalid patient identifier - NHS number too short


  Scenario Outline: Check invalid identifier query parameter requests (No _include parameter)
    Given a state machine input JSON:
        {
            "proxyNhsNumber": "<identifier>",
            "patientNhsNumber": "",
            "_include": "",
            "correlationId": "e608c0dc-3c05-4e77-876b-326da36219d8",
            "requestId": "e26470b0-1e84-4d46-94d0-394b8ae3136e",
            "originalRequestUrl": "validated-relationships-service-dev.national.nhs.uk"
        }
    When the step function validate-relationships-state-machine is called
    Then the step function will return <status_code>
    And the response will be JSON
    And the diagnostics <diagnostics> is present in the response
    And the system, version, severity and resourceType are correct in the response
    And the error code <error_code> is present in the response
    And the code <code> is present in the response
    And the display <display> is present in the response

    Examples:
      | identifier                                                  | status_code | diagnostics                         | error_code                | code    | display                           |
      | https%3A%2F%2Ffhir.nhs.uk%2FId%2Fnhs-number%2F%7C9730675929 | 400         | The identifier system is not valid. | INVALID_IDENTIFIER_SYSTEM | invalid | Invalid identifier system         | # malformed identifier value identifier system


  Scenario Outline: Check invalid identifier and patient identifier query parameter requests (with _include parameter)
    Given a state machine input JSON:
        {
            "proxyNhsNumber": "<identifier>",
            "patientNhsNumber": "<patient_identifier>",
            "_include": "RelatedPerson:patient",
            "correlationId": "e608c0dc-3c05-4e77-876b-326da36219d8",
            "requestId": "e26470b0-1e84-4d46-94d0-394b8ae3136e",
            "originalRequestUrl": "validated-relationships-service-dev.national.nhs.uk"
        }
    When the step function validate-relationships-state-machine is called
    Then the step function will return <status_code>
    And the response will be JSON
    And the diagnostics <diagnostics> is present in the response
    And the system, version, severity and resourceType are correct in the response
    And the error code <error_code> is present in the response
    And the code <code> is present in the response
    And the display <display> is present in the response

    Examples:
      | identifier                                                  | patient_identifier                                        | status_code | diagnostics                                                            | error_code                       | code    | display                           |
      | https%3A%2F%2Ffhir.nhs.uk%2FId%2Fnhs-number%2F%7C9730675988 | 9730676445                                                | 400         | The identifier system is not valid.                                    | INVALID_IDENTIFIER_SYSTEM        | invalid | Invalid identifier system         | # malformed identifier value identifier system
      | 9730675988                                                  | https%3A%2F%2Ffhir.nhs.uk%2Fid%2Fnhs-number%7C9730676445  | 400         | The identifier system is not valid.                                    | INVALID_IDENTIFIER_SYSTEM        | invalid | Invalid identifier system         | # malformed patient:identifier value identifier system
      | https%3A%2F%2Ffhir.nhs.uk%2FId%2FNhs-number%7C9730675988    | https%3A%2F%2FFhir.nhs.uk%2FId%2Fnhs-number%7C9730676445  | 400         | The identifier system is not valid.                                    | INVALID_IDENTIFIER_SYSTEM        | invalid | Invalid identifier system         | # malformed identifier and patient:identifier value identifier system
      | 9730675988                                                  | 9999999998                                                | 400         | Not a valid NHS Number provided for the 'patient:identifier' parameter | INVALID_PATIENT_IDENTIFIER_VALUE | invalid | Provided value is invalid         | # invalid patient identifier - invalid NHS number
      | 9730675988                                                  | https%3A%2F%2Ffhir.nhs.uk%2FId%2Fnhs-number%7C9999999998  | 400         | Not a valid NHS Number provided for the 'patient:identifier' parameter | INVALID_PATIENT_IDENTIFIER_VALUE | invalid | Provided value is invalid         | # invalid patient identifier - invalid NHS number
      | 9730675988                                                  | https%3A%2F%2FFhir.nhs.uk%2FId%2Fnhs-number%2F9730676445  | 400         | Not a valid NHS Number provided for the 'patient:identifier' parameter | INVALID_PATIENT_IDENTIFIER_VALUE | invalid | Provided value is invalid         | # invalid patient identifier - forward slash intead of pipe
      | 9730675988                                                  | 97306764459                                               | 400         | Not a valid NHS Number provided for the 'patient:identifier' parameter | INVALID_PATIENT_IDENTIFIER_VALUE | invalid | Provided value is invalid         | # invalid patient identifier - NHS number too long
      | 9730675988                                                  | 973067644                                                 | 400         | Not a valid NHS Number provided for the 'patient:identifier' parameter | INVALID_PATIENT_IDENTIFIER_VALUE | invalid | Provided value is invalid         | # invalid patient identifier - NHS number too short
      | 9730675988                                                  | https%3A%2F%2FFhir.nhs.uk%2FId%2Fnhs-number%7C97306764459 | 400         | Not a valid NHS Number provided for the 'patient:identifier' parameter | INVALID_PATIENT_IDENTIFIER_VALUE | invalid | Provided value is invalid         | # invalid patient identifier - NHS number too long
      | 9730675988                                                  | https%3A%2F%2FFhir.nhs.uk%2FId%2Fnhs-number%7C973067644   | 400         | Not a valid NHS Number provided for the 'patient:identifier' parameter | INVALID_PATIENT_IDENTIFIER_VALUE | invalid | Provided value is invalid         | # invalid patient identifier - NHS number too short


  Scenario Outline: Check invalid identifier query parameter requests (with _include parameter)
    Given a state machine input JSON:
        {
            "proxyNhsNumber": "<identifier>",
            "patientNhsNumber": "",
            "_include": "RelatedPerson:patient",
            "correlationId": "e608c0dc-3c05-4e77-876b-326da36219d8",
            "requestId": "e26470b0-1e84-4d46-94d0-394b8ae3136e",
            "originalRequestUrl": "validated-relationships-service-dev.national.nhs.uk"
        }
    When the step function validate-relationships-state-machine is called
    Then the step function will return <status_code>
    And the response will be JSON
    And the diagnostics <diagnostics> is present in the response
    And the system, version, severity and resourceType are correct in the response
    And the error code <error_code> is present in the response
    And the code <code> is present in the response
    And the display <display> is present in the response

    Examples:
      | identifier                                                  | status_code | diagnostics                                                    | error_code                | code    | display                           |
      | https%3A%2F%2Ffhir.nhs.uk%2FId%2Fnhs-number%2F%7C9730675929 | 400         | The identifier system is not valid.                            | INVALID_IDENTIFIER_SYSTEM | invalid | Invalid identifier system         | # malformed identifier value identifier system


  Scenario Outline: Confirm invalid include value returns zero resources for a specific mother and child (_include=RelatedPerson:NotAPatient)
    Given a state machine input JSON:
        {
            "proxyNhsNumber": "<identifier>",
            "patientNhsNumber": "<patient_identifier>",
            "_include": "RelatedPerson:NotAPatient",
            "correlationId": "e608c0dc-3c05-4e77-876b-326da36219d8",
            "requestId": "e26470b0-1e84-4d46-94d0-394b8ae3136e",
            "originalRequestUrl": "validated-relationships-service-dev.national.nhs.uk"
        }
    When the step function validate-relationships-state-machine is called
    Then the step function will return 200
    And the response will be JSON
    And the entry in the response will contain 0 resources of resourceType 'Patient'
    And the entry in the response will contain <number_of_children> resources of resourceType 'RelatedPerson'
    And the total number of records is '<number_of_children>'
    And the 'RelatedPerson' entries 'resource.identifier[0].value' matches <identifier>


    Examples:
      | identifier                                               | patient_identifier | number_of_children |
      | 9730675929                                               | 9730676399         | 1                  |
      | https%3A%2F%2Ffhir.nhs.uk%2FId%2Fnhs-number%7C9730675988 | 9730676445         | 1                  |

  Scenario Outline: Confirm invalid include value returns zero resources for a specific mother(_include=RelatedPerson:NotAPatient)
    Given a state machine input JSON:
        {
            "proxyNhsNumber": "<identifier>",
            "patientNhsNumber": "",
            "_include": "RelatedPerson:NotAPatient",
            "correlationId": "e608c0dc-3c05-4e77-876b-326da36219d8",
            "requestId": "e26470b0-1e84-4d46-94d0-394b8ae3136e",
            "originalRequestUrl": "validated-relationships-service-dev.national.nhs.uk"
        }
    When the step function validate-relationships-state-machine is called
    Then the step function will return 200
    And the response will be JSON
    And the entry in the response will contain 0 resources of resourceType 'Patient'
    And the entry in the response will contain <number_of_children> resources of resourceType 'RelatedPerson'
    And the total number of records is '<number_of_children>'
    And the 'RelatedPerson' entries 'resource.identifier[0].value' matches <identifier>


    Examples:
      | identifier                                               | number_of_children |
      | 9730675929                                               | 1                  |
      | 9730675988                                               | 2                  |
      | https%3A%2F%2Ffhir.nhs.uk%2FId%2Fnhs-number%7C9730675988 | 2                  |
