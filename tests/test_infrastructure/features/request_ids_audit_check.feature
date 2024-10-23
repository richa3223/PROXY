Feature: Correlation ID and Request ID validation

  Scenario: Confirm a valid request IDs persist through from API call to audit events bucket
    Given the Relationship Validation Service API is available
    And the client is authenticated with 9730675929
    And the X-Request-ID and X-Correlation-ID headers are set to UUIDs
    When the client calls /FHIR/R4/RelatedPerson with identifier 9730675929 and patient:identifier 9730676399
    Then the Relationship Validation Service will return 200
    And the response will be JSON
    And the request will match the API Spec
    And the response will match the API Spec
    And the patient_identifier 9730676399 is returned in the patient record 0
    And the identifier 9730675929 and relationship_id 47CD795E are returned in the related person 0
    And the total number of records is 1 with a type of searchset
    Then after 120 seconds have passed
    And the request has been logged to the Audit Service using the main-queryable_data_glue_crawler
    And an entry with the specified X-Request-ID id can be found in the 'main_audit_main_dev_queryable_audit_events_bucket' column request-id
    And an entry with the specified X-Correlation-ID id can be found in the 'main_audit_main_dev_queryable_audit_events_bucket' column correlation-id
    And all sensitive values are redacted
    And the request has been logged to the Audit Service using the main-sensitive_data_glue_crawler
    And an entry with the specified X-Request-ID id can be found in the 'main_audit_main_dev_sensitive_audit_events_bucket' column request-id
    And an entry with the specified X-Correlation-ID id can be found in the 'main_audit_main_dev_sensitive_audit_events_bucket' column correlation-id
    And all sensitive values are redacted
