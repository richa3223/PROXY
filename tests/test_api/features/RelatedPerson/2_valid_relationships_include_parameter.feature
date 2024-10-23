Feature: Handle include parameter

  Scenario Outline: Confirm valid relationships returned for a specific mother (_include=RelatedPerson:patient)
    Given the Relationship Validation Service API is available
    And the client is authenticated with <identifier>
    And the X-Request-ID and X-Correlation-ID headers are set to UUIDs
    And the '_include' parameter is present with a value of 'RelatedPerson:patient'
    When an identifier <identifier> is used to call /FHIR/R4/RelatedPerson
    Then the Relationship Validation Service will return 200
    And the response will be JSON
    And the request will match the API Spec
    And the response will match the API Spec
    And the link to self matches the request URL
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
    Given the Relationship Validation Service API is available
    And the client is authenticated with <identifier>
    And the X-Request-ID and X-Correlation-ID headers are set to UUIDs
    And the '_include' parameter is present with a value of 'RelatedPerson:patient'
    When the client calls /FHIR/R4/RelatedPerson with identifier <identifier> and patient:identifier <patient_identifier>
    Then the Relationship Validation Service will return 200
    And the response will be JSON
    And the request will match the API Spec
    And the response will match the API Spec
    And the link to self matches the request URL
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
