Feature: Relationship Validation for the validate_relationship_state_machine step function
  Scenario Outline: Confirm a valid relationship between a specific mother and child (No _include parameter)
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
    And the link to self matches originalRequestUrl
    And the total number of records is <total> with a type of searchset
    #And the full url values are populated occurring <total> times
    And the patient_identifier <patient_identifier> is returned in the patient record <patient_index>
    And the identifier <identifier> and relationship_id <relationship_id> are returned in the related person <related_index>
    And the 'RelatedPerson' relationship.coding array contains only a MTH code entry

    Examples:
      | identifier                                               | patient_identifier                                       | relationship_id | patient_index | related_index | total |
      | 9730675929                                               | 9730676399                                               | 47CD795E        | 0             | 0             | 1     |   # 1 to 1 relationship
      | 9730675988                                               | 9730676445                                               | BE974742        | 0             | 0             | 1     |   # 1 to 2 relationship
      | https%3A%2F%2Ffhir.nhs.uk%2FId%2Fnhs-number%7C9730675929 | 9730676399                                               | 47CD795E        | 0             | 0             | 1     |   # identifier as url e.g. "https://fhir.nhs.uk/Id/nhs-number/9730675929"
      | 9730675929                                               | https%3A%2F%2Ffhir.nhs.uk%2FId%2Fnhs-number%7C9730676399 | 47CD795E        | 0             | 0             | 1     |   # patient_identifier as url
      | https%3A%2F%2Ffhir.nhs.uk%2FId%2Fnhs-number%7C9730675929 | https%3A%2F%2Ffhir.nhs.uk%2FId%2Fnhs-number%7C9730676399 | 47CD795E        | 0             | 0             | 1     |   # identifier and patient_identifier as url
      | 9731974830                                               | 9731974857                                               | WCtlt           | 0             | 0             | 1     |   # 1 to 1 relationship no period object in child's relationship to mother record
      | 9730676046                                               | 9730676585                                               | 7A31B8E7        | 0             | 0             | 1     |   # 1 to 8 relationships


Scenario Outline: Confirm a valid relationship between a specific mother (No _include parameter)
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
    And the link to self matches originalRequestUrl
    And the total number of records is <total> with a type of searchset
    #And the full url values are populated occurring <total> times
    And the patient_identifier <patient_identifiers> is returned in the patient record <patient_index>
    And the identifier <identifier> and relationship_id <relationship_id> are returned in the related person <related_index>
    And the 'RelatedPerson' relationship.coding array contains only a MTH code entry

    Examples:
      | identifier                                               | patient_identifiers                                                          | relationship_id                                                | patient_index | related_index | total |
      | 9730675929                                               | 9730676399                                                                   | 47CD795E                                                       | 0             | 0             | 1     | # 1 to 1 relationship
      | 9730675988                                               | 9730676445,9730676518                                                        | BE974742,A3CC67E2                                              | 0,1           | 0,1           | 2     | # 1 to 2 relationship
      | https%3A%2F%2Ffhir.nhs.uk%2FId%2Fnhs-number%7C9730675988 | 9730676445,9730676518                                                        | BE974742,A3CC67E2                                              | 0,1           | 0,1           | 2     | # identifier as url e.g. "https://fhir.nhs.uk/Id/nhs-number/9730675988"
      | 9731974830                                               | 9731974857                                                                   | WCtlt                                                          | 0             | 0             | 1     | # 1 to 1 relationship no period object in child's relationship to mother record
      | 9730676046                                               | 9730676569,9730676593,9730676585,9730676615,9730676577,9730676607,9730676623 | DB3C2B03,629986D9,7A31B8E7,8182FC3E,C09748AA,A79C0DEF,78C0A3C3 | 0,1,2,3,4,5,6 | 0,1,2,3,4,5,6 | 7     | # 1 to 8 relationships (7 are valid)
