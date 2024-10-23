Feature: Invalid Relationships for the validate_relationship_state_machine step function

  Scenario Outline: Confirm an invalid relationship with explicit patient
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
    Then the step function will return 200
    And the response will be JSON
    And the total number of records is 0 with a type of searchset


    Examples:
      | identifier | patient_identifier |
      | 9730676054 | 9730676658         | # Proxy is deceased
      | 9730676070 | 9730676674         | # Proxy is restricted
      | 9730676135 | 9730676755         | # Patient is deceased
      | 9730676186 | 9730676836         | # Patient is restricted
      | 9730676240 | 9730676895         | # Related person is not MTH
      | 9730676046 | 9730676631         | # Patient is deceased - Proxy has multiple relationships


  Scenario Outline: Confirm invalid relationships with one identifier only
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
    Then the step function will return 200
    And the response will be JSON
    And the total number of records is 0 with a type of searchset

    Examples:
      | identifier |
      | 9730424640 | # Related person is not MTH
      | 9730423164 | # No relationship exists
