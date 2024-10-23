Feature: OAuth and Authentication

  Scenario Outline: Authentication server responses based on different verification level NHS numbers
    Given the keycloak server is available
    And the authentication server is available
    When the client authenticates as <identifier>
    Then the id token contains a <verification_level> verification level
    And the authentication server will return <response>

    Examples:
      | identifier | verification_level | response |
      | 9912003071 | P9                 | 200      |
      | 9912003072 | P5                 | 401      |
      | 9912003073 | P0                 | 401      |


  Scenario Outline: Confirm invalid or missing auth tokens are handled appropriately
    Given the Relationship Validation Service API is available
    And the client is authenticated with 9730675929
    And the X-Request-ID and X-Correlation-ID headers are set to UUIDs
    And the header Authorization is set to <header_value>
    When the client calls /FHIR/R4/RelatedPerson with identifier 9730675929 and patient:identifier 9730676399
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

  Scenario: Confirm auth token NHS number and query parameter identifier mismatch returns 403 FORBIDDEN
    Given the Relationship Validation Service API is available
    And the client is authenticated with 9730675929
    And the X-Request-ID and X-Correlation-ID headers are set to UUIDs
    When the client calls /FHIR/R4/RelatedPerson with identifier 9730675988 and patient:identifier 9730676445
    Then the Relationship Validation Service will return 403
    And the response will be JSON
    And the response will match the API Spec
    And the diagnostics Access denied to resource. is present in the response
    And the system, version, severity and resourceType are correct in the response
    And the error code FORBIDDEN is present in the response
    And the code forbidden is present in the response
    And the display Access Denied is present in the response
