Feature: Operation Outcome Tests

  Scenario Outline: Check invalid URL returns a 404 for specific mother and child
    Given the Relationship Validation Service API is available
    And the client is authenticated with <identifier>
    And the X-Request-ID and X-Correlation-ID headers are set to UUIDs
    When the client calls <path> with identifier <identifier> and patient:identifier 9730676399
    Then the Relationship Validation Service will return 404
    And the response will be JSON
    And the system, version, severity and resourceType are correct in the response
    And the error code INVALIDATED_RESOURCE is present in the response
    And the code processing is present in the response
    And the display Resource that has been marked as invalid was requested - invalid resources cannot be retrieved is present in the response

    Examples:
      | identifier | path                           |
      | 9730675929 | %2FRelatedPerson               |
      | 9730675929 | %2Ffhir%2Fr4%2Frelatedperson   |
      | 9730675929 | %2FFHIR%2FR4%2FRelatedPersons  |
      | 9730675929 | %2FFHIR%2FR4%2F RelatedPersons |


  Scenario Outline: Check invalid URL returns a 404 for specific mother
    Given the Relationship Validation Service API is available
    And the client is authenticated with <identifier>
    And the X-Request-ID and X-Correlation-ID headers are set to UUIDs
    When an identifier <identifier> is used to call <path>
    Then the Relationship Validation Service will return 404
    And the response will be JSON
    And the system, version, severity and resourceType are correct in the response
    And the error code INVALIDATED_RESOURCE is present in the response
    And the code processing is present in the response
    And the display Resource that has been marked as invalid was requested - invalid resources cannot be retrieved is present in the response

    Examples:
      | identifier | path                           |
      | 9730675929 | %2FRelatedPerson               |
      | 9730675929 | %2Ffhir%2Fr4%2Frelatedperson   |
      | 9730675929 | %2FFHIR%2FR4%2FRelatedPersons  |
      | 9730675929 | %2FFHIR%2FR4%2F RelatedPersons |


  Scenario Outline: Check missing and invalid headers
    Given the Relationship Validation Service API is available
    And the client is authenticated with 9730675929
    And the X-Request-ID and X-Correlation-ID headers are set to UUIDs
    And the header <header_key> is set to <header_value>
    When the client calls /FHIR/R4/RelatedPerson with identifier 9730675929 and patient:identifier 9730676399
    Then the Relationship Validation Service will return <status_code>
    And the response will be JSON
    And the response will match the API Spec
    And the diagnostics <diagnostics> is present in the response
    And the system, version, severity and resourceType are correct in the response
    And the error code <error_code> is present in the response
    And the code <code> is present in the response
    And the display <display> is present in the response

    Examples:
      | header_key       | header_value                    | status_code | diagnostics                                                  | error_code  | code    | display                                   |
      | X-Request-ID     | missing key                     | 400         | Invalid request with error - X-Request-ID header not found.  | BAD_REQUEST | invalid | Required header parameter(s) are missing. | # missing X-Request-ID key
      | X-Request-ID     | empty value                     | 400         | Invalid request with error - X-Request-ID header not found.  | BAD_REQUEST | invalid | Required header parameter(s) are missing. | # empty X-Request-ID value
      | X-Request-ID     | invalid X-Request-ID header     | 400         | Invalid request with error - X-Request-ID header invalid     | BAD_REQUEST | invalid | Required header parameter(s) are invalid. | # invalid X-Request-ID value
      | X-Request-ID     | 1000 characters                 | 400         | Invalid request with error - X-Request-ID header invalid     | BAD_REQUEST | invalid | Required header parameter(s) are invalid. | # invalid 1000 chars X-Request-ID value
      | X-Request-ID     | null                            | 400         | Invalid request with error - X-Request-ID header not found.  | BAD_REQUEST | invalid | Required header parameter(s) are missing. | # null X-Request-ID value
      | X-Correlation-ID | invalid X-Correlation-ID header | 400         | Invalid request with error - X-Correlation-ID header invalid | BAD_REQUEST | invalid | Required header parameter(s) are invalid. | # invalid X-Correlation-ID key
      | X-Correlation-ID | 1000 characters                 | 400         | Invalid request with error - X-Correlation-ID header invalid | BAD_REQUEST | invalid | Required header parameter(s) are invalid. | # invalid 1000 X-Correlation-ID key


  Scenario Outline: Optional X-Correlation-ID header for valid relationships between a specific mother and child (No _include parameter)
    Given the Relationship Validation Service API is available
    And the client is authenticated with <identifier>
    And the X-Request-ID and X-Correlation-ID headers are set to UUIDs
    And the header X-Correlation-ID is set to <header_value>
    When the client calls /FHIR/R4/RelatedPerson with identifier <identifier> and patient:identifier <patient_identifier>
    Then the Relationship Validation Service will return 200
    And the response will be JSON
    And the response will match the API Spec
    And the link to self matches the request URL
    And the total number of records is <total> with a type of searchset
    And the full url values are populated occurring <total> times
    And the patient_identifier <patient_identifier> is returned in the patient record <patient_index>
    And the identifier <identifier> and relationship_id <relationship_id> are returned in the related person <related_index>
    And the 'RelatedPerson' relationship.coding array contains only a MTH code entry

    Examples:
      | header_value | identifier | patient_identifier | relationship_id | patient_index | related_index | total |
      | missing key  | 9730675988 | 9730676445         | BE974742        | 0             | 0             | 1     |  # missing X-Correlation-ID
      | empty value  | 9730675988 | 9730676445         | BE974742        | 0             | 0             | 1     |  # empty X-Correlation-ID
      | null         | 9730675988 | 9730676445         | BE974742        | 0             | 0             | 1     |  # null X-Correlation-ID


  Scenario Outline: Optional X-Correlation-ID header for valid relationships returned for a specific mother (No _include parameter)
    Given the Relationship Validation Service API is available
    And the client is authenticated with <identifier>
    And the X-Request-ID and X-Correlation-ID headers are set to UUIDs
    And the header X-Correlation-ID is set to <header_value>
    When an identifier <identifier> is used to call /FHIR/R4/RelatedPerson
    Then the Relationship Validation Service will return 200
    And the response will be JSON
    And the response will match the API Spec
    And the link to self matches the request URL
    And the total number of records is <total> with a type of searchset
    And the full url values are populated occurring <total> times
    And the patient_identifier <patient_identifiers> is returned in the patient record <patient_index>
    And the identifier <identifier> and relationship_id <relationship_id> are returned in the related person <related_index>
    And the 'RelatedPerson' relationship.coding array contains only a MTH code entry

    Examples:
      | header_value | identifier | patient_identifiers   | relationship_id   | patient_index | related_index | total |
      | missing key  | 9730675988 | 9730676445,9730676518 | BE974742,A3CC67E2 | 0,1           | 0,1           | 2     | # missing X-Correlation-ID
      | empty value  | 9730675988 | 9730676445,9730676518 | BE974742,A3CC67E2 | 0,1           | 0,1           | 2     | # empty X-Correlation-ID
      | null         | 9730675988 | 9730676445,9730676518 | BE974742,A3CC67E2 | 0,1           | 0,1           | 2     | # null X-Correlation-ID


  Scenario Outline: Optional X-Correlation-ID header for valid relationships returned for a specific mother (_include=RelatedPerson:patient)
    Given the Relationship Validation Service API is available
    And the client is authenticated with <identifier>
    And the X-Request-ID and X-Correlation-ID headers are set to UUIDs
    And the header X-Correlation-ID is set to <header_value>
    And the '_include' parameter is present with a value of 'RelatedPerson:patient'
    When an identifier <identifier> is used to call /FHIR/R4/RelatedPerson
    Then the Relationship Validation Service will return 200
    And the response will be JSON
    And the response will match the API Spec
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
      | header_value | identifier | patient_identifiers   | number_of_children | total_records |
      | missing key  | 9730675988 | 9730676445,9730676518 | 2                  | 4             | # missing X-Correlation-ID
      | empty value  | 9730675988 | 9730676445,9730676518 | 2                  | 4             | # empty X-Correlation-ID
      | null         | 9730675988 | 9730676445,9730676518 | 2                  | 4             | # null X-Correlation-ID


  Scenario Outline: Optional X-Correlation-ID header for valid relationships returned for a specific mother and child (_include=RelatedPerson:patient)
    Given the Relationship Validation Service API is available
    And the client is authenticated with <identifier>
    And the X-Request-ID and X-Correlation-ID headers are set to UUIDs
    And the header X-Correlation-ID is set to <header_value>
    And the '_include' parameter is present with a value of 'RelatedPerson:patient'
    When the client calls /FHIR/R4/RelatedPerson with identifier <identifier> and patient:identifier <patient_identifier>
    Then the Relationship Validation Service will return 200
    And the response will be JSON
    And the response will match the API Spec
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
      | header_value | identifier | patient_identifier | number_of_children | total_records |
      | missing key  | 9730675929 | 9730676399         | 1                  | 2             | # missing X-Correlation-ID
      | empty value  | 9730675929 | 9730676399         | 1                  | 2             | # empty X-Correlation-ID
      | null         | 9730675929 | 9730676399         | 1                  | 2             | # null X-Correlation-ID


  Scenario Outline: Check invalid identifier and patient identifier query parameter requests (No _include parameter)
    Given the Relationship Validation Service API is available
    And the client is authenticated with 9730675988
    And the X-Request-ID and X-Correlation-ID headers are set to UUIDs
    When the client calls /FHIR/R4/RelatedPerson with identifier <identifier> and patient:identifier <patient_identifier>
    Then the Relationship Validation Service will return <status_code>
    And the request will match the API Spec
    And the response will be JSON
    And the response will match the API Spec
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
    Given the Relationship Validation Service API is available
    And the client is authenticated with 9730675929
    And the X-Request-ID and X-Correlation-ID headers are set to UUIDs
    When an identifier <identifier> is used to call /FHIR/R4/RelatedPerson
    Then the Relationship Validation Service will return <status_code>
    And the request will match the API Spec
    And the response will be JSON
    And the response will match the API Spec
    And the diagnostics <diagnostics> is present in the response
    And the system, version, severity and resourceType are correct in the response
    And the error code <error_code> is present in the response
    And the code <code> is present in the response
    And the display <display> is present in the response

    Examples:
      | identifier                                                  | status_code | diagnostics                                                    | error_code                | code    | display                           |
      | https%3A%2F%2Ffhir.nhs.uk%2FId%2Fnhs-number%2F%7C9730675929 | 400         | The identifier system is not valid.                            | INVALID_IDENTIFIER_SYSTEM | invalid | Invalid identifier system         | # malformed identifier value identifier system


  Scenario Outline: Check invalid identifier and patient identifier query parameter requests (with _include parameter)
    Given the Relationship Validation Service API is available
    And the client is authenticated with 9730675988
    And the X-Request-ID and X-Correlation-ID headers are set to UUIDs
    And the '_include' parameter is present with a value of 'RelatedPerson:patient'
    When the client calls /FHIR/R4/RelatedPerson with identifier <identifier> and patient:identifier <patient_identifier>
    Then the Relationship Validation Service will return <status_code>
    And the request will match the API Spec
    And the response will be JSON
    And the response will match the API Spec
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
    Given the Relationship Validation Service API is available
    And the client is authenticated with 9730675929
    And the X-Request-ID and X-Correlation-ID headers are set to UUIDs
    And the '_include' parameter is present with a value of 'RelatedPerson:patient'
    When an identifier <identifier> is used to call /FHIR/R4/RelatedPerson
    Then the Relationship Validation Service will return <status_code>
    And the request will match the API Spec
    And the response will be JSON
    And the response will match the API Spec
    And the diagnostics <diagnostics> is present in the response
    And the system, version, severity and resourceType are correct in the response
    And the error code <error_code> is present in the response
    And the code <code> is present in the response
    And the display <display> is present in the response

    Examples:
      | identifier                                                  | status_code | diagnostics                                                    | error_code                | code    | display                           |
      | https%3A%2F%2Ffhir.nhs.uk%2FId%2Fnhs-number%2F%7C9730675929 | 400         | The identifier system is not valid.                            | INVALID_IDENTIFIER_SYSTEM | invalid | Invalid identifier system         | # malformed identifier value identifier system


  Scenario Outline: Confirm invalid include value returns zero resources for a specific mother and child (_include=RelatedPerson:NotAPatient)
    Given the Relationship Validation Service API is available
    And the client is authenticated with <identifier>
    And the X-Request-ID and X-Correlation-ID headers are set to UUIDs
    And the '_include' parameter is present with a value of 'RelatedPerson:NotAPatient'
    When the client calls /FHIR/R4/RelatedPerson with identifier <identifier> and patient:identifier <patient_identifier>
    Then the Relationship Validation Service will return 200
    And the response will be JSON
    And the request will match the API Spec
    And the response will match the API Spec
    And the entry in the response will contain 0 resources of resourceType 'Patient'
    And the entry in the response will contain <number_of_children> resources of resourceType 'RelatedPerson'
    And the total number of records is '<number_of_children>'
    And the 'RelatedPerson' entries 'resource.identifier[0].value' matches <identifier>


    Examples:
      | identifier                                               | patient_identifier | number_of_children |
      | 9730675929                                               | 9730676399         | 1                  |
      | https%3A%2F%2Ffhir.nhs.uk%2FId%2Fnhs-number%7C9730675988 | 9730676445         | 1                  |

  Scenario Outline: Confirm invalid include value returns zero resources for a specific mother(_include=RelatedPerson:NotAPatient)
    Given the Relationship Validation Service API is available
    And the client is authenticated with <identifier>
    And the X-Request-ID and X-Correlation-ID headers are set to UUIDs
    And the '_include' parameter is present with a value of 'RelatedPerson:NotAPatient'
    When an identifier <identifier> is used to call /FHIR/R4/RelatedPerson
    Then the Relationship Validation Service will return 200
    And the response will be JSON
    And the request will match the API Spec
    And the response will match the API Spec
    And the entry in the response will contain 0 resources of resourceType 'Patient'
    And the entry in the response will contain <number_of_children> resources of resourceType 'RelatedPerson'
    And the total number of records is '<number_of_children>'
    And the 'RelatedPerson' entries 'resource.identifier[0].value' matches <identifier>


    Examples:
      | identifier                                               | number_of_children |
      | 9730675929                                               | 1                  |
      | 9730675988                                               | 2                  |
      | https%3A%2F%2Ffhir.nhs.uk%2FId%2Fnhs-number%7C9730675988 | 2                  |

  Scenario Outline: Call /RelatedPerson with HTTP verbs returning content
    Given the Relationship Validation Service API is available
    And the client is authenticated with <identifier>
    And the X-Request-ID and X-Correlation-ID headers are set to UUIDs
    And the header Content-Type is set to application/fhir+json
    When an identifier <identifier> is used to call /FHIR/R4/RelatedPerson with verb <verb>
    Then the Relationship Validation Service will return <status_code>
    And the response will be JSON
    And the error code METHOD_NOT_ALLOWED is present in the response
    And the display The method is not allowed. is present in the response
    And the diagnostics The method is not allowed for the requested resource. is present in the response
    And the system, version, severity and resourceType are correct in the response

    Examples:
      | identifier | verb    | status_code |
      | 9730675929 | DELETE  | 405         |
      | 9730675929 | OPTIONS | 405         |
      | 9730675929 | PATCH   | 405         |
      | 9730675929 | POST    | 405         |
      | 9730675929 | PUT     | 405         |

  Scenario Outline: Call /RelatedPerson with HTTP verbs returning no content
    Given the Relationship Validation Service API is available
    And the client is authenticated with <identifier>
    And the X-Request-ID and X-Correlation-ID headers are set to UUIDs
    When an identifier <identifier> is used to call /FHIR/R4/RelatedPerson with verb <verb>
    Then the Relationship Validation Service will return <status_code>

    Examples:
      | identifier | verb | status_code |
      | 9730675929 | HEAD | 405         |
