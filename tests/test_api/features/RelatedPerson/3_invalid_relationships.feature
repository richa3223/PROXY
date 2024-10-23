Feature: Invalid Relationships

  Scenario Outline: Confirm an invalid relationship with explicit patient
    Given the Relationship Validation Service API is available
    And the client is authenticated with <identifier>
    And the X-Request-ID and X-Correlation-ID headers are set to UUIDs
    When the client calls /FHIR/R4/RelatedPerson with identifier <identifier> and patient:identifier <patient_identifier>
    Then the Relationship Validation Service will return 200
    And the response will be JSON
    And the request will match the API Spec
    And the response will match the API Spec
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
    Given the Relationship Validation Service API is available
    And the client is authenticated with <identifier>
    And the X-Request-ID and X-Correlation-ID headers are set to UUIDs
    When an identifier <identifier> is used to call /FHIR/R4/RelatedPerson
    Then the Relationship Validation Service will return 200
    And the response will be JSON
    And the request will match the API Spec
    And the response will match the API Spec
    And the total number of records is 0 with a type of searchset

    Examples:
      | identifier |
      | 9730424640 | # Related person is not MTH
      | 9730423164 | # No relationship exists
