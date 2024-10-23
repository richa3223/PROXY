Feature: Provide OperationOutcome when an internal server error occurs

  Scenario: VRS is under load
    Given the VRS relationship lookup endpoint is in a 408 failure mode
    And the client is authenticated with 9730675929
    And the X-Request-ID and X-Correlation-ID headers are set to UUIDs
    When an identifier 9730675929 is used to call /FHIR/R4/RelatedPerson
    Then the Relationship Validation Service will return 408

  Scenario: VRS is not working
    Given the VRS is in a failure mode
    And the client is authenticated with 9730675929
    And the X-Request-ID and X-Correlation-ID headers are set to UUIDs
    When an identifier 9730675929 is used to call /FHIR/R4/RelatedPerson
    Then the Relationship Validation Service will return 500
    And the diagnostics Internal Server Error - Failed to generate response is present in the response
    And the system, version, severity and resourceType are correct in the response
    And the error code SERVER_ERROR is present in the response
    And the code invalid is present in the response
    And the display Failed to generate response is present in the response
  # Comment: the VRS is taken out of failure mode automatically by pytest fixture

  Scenario: PDS API is not working
    Given the PDS API is in a failure mode
    And the client is authenticated with 9730675929
    And the X-Request-ID and X-Correlation-ID headers are set to UUIDs
    When an identifier 9730675929 is used to call /FHIR/R4/RelatedPerson
    Then the Relationship Validation Service will return 500
    And the diagnostics Internal Server Error - Failed to generate response is present in the response
    And the system, version, severity and resourceType are correct in the response
    And the error code SERVER_ERROR is present in the response
    And the code invalid is present in the response
    And the display Failed to generate response is present in the response
# Comment: the PDS API is taken out of failure mode automatically by pytest fixture
