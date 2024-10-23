Feature: Handle include parameter for the validate_relationship_state_machine
  Scenario Outline: Confirm valid relationships returned for a specific mother (_include=RelatedPerson:patient)
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
    Then the step function will return 200
    And the response will be JSON
    And the link to self matches originalRequestUrl
    And the entry in the response will contain <number_of_children> resources of resourceType 'Patient'
    And for each of the <number_of_children> entries 'search.mode' is 'include'
    And the entry in the response will contain <number_of_children> resources of resourceType 'RelatedPerson'
    And the 'RelatedPerson' entries 'resource.patient.identifier.value' matches <patient_identifiers>
    And for each of the <number_of_children> entries 'search.mode' is 'match'
    And the total number of records is '<total_records>'
    And the 'RelatedPerson' entries 'resource.identifier[0].value' matches <identifier>
    And the 'Patient' entries 'resource.identifier[0].value' matches <patient_identifiers>
    And the 'RelatedPerson' relationship.coding array contains only a MTH code entry

    Examples:
      | identifier                                               | patient_identifiers                                                          | number_of_children | total_records |
      | 9730675929                                               | 9730676399                                                                   | 1                  | 2             |
      | 9730675988                                               | 9730676445,9730676518                                                        | 2                  | 4             |
      | https%3A%2F%2Ffhir.nhs.uk%2FId%2Fnhs-number%7C9730675988 | 9730676445,9730676518                                                        | 2                  | 4             |
      | 9731974830                                               | 9731974857                                                                   | 1                  | 2             | # 1 to 1 relationship no period object in child's relationship to mother record
      | 9730676046                                               | 9730676569,9730676593,9730676585,9730676615,9730676577,9730676607,9730676623 | 7                  | 14            | # 1 to 8 relationships (7 are valid)

  Scenario Outline: Confirm valid relationships returned for a specific mother and child (_include=RelatedPerson:patient)
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
    Then the step function will return 200
    And the response will be JSON
    And the link to self matches originalRequestUrl
    And the entry in the response will contain <number_of_children> resources of resourceType 'Patient'
    And for each of the <number_of_children> entries 'search.mode' is 'include'
    And the entry in the response will contain <number_of_children> resources of resourceType 'RelatedPerson'
    And the 'RelatedPerson' entries 'resource.patient.identifier.value' matches <patient_identifier>
    And for each of the <number_of_children> entries 'search.mode' is 'match'
    And the total number of records is '<total_records>'
    And the 'RelatedPerson' entries 'resource.identifier[0].value' matches <identifier>
    And the 'Patient' entries 'resource.identifier[0].value' matches <patient_identifier>
    And the 'RelatedPerson' relationship.coding array contains only a MTH code entry

    Examples:
      | identifier                                               | patient_identifier | number_of_children | total_records |
      | 9730675929                                               | 9730676399         | 1                  | 2             |
      | https%3A%2F%2Ffhir.nhs.uk%2FId%2Fnhs-number%7C9730675988 | 9730676445         | 1                  | 2             |
      | 9731974830                                               | 9731974857         | 1                  | 2             | # 1 to 1 relationship no period object in child's relationship to mother record
      | 9730676046                                               | 9730676623         | 1                  | 2             |
