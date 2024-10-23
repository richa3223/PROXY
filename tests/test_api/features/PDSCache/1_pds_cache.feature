
Feature: Cache PDS Response
     @NPA-3199
    Scenario Outline: No cached PDS response available
        Given a unique value is created for query parameter
        And base url is https://mock.validated-relationships-service-dev.national.nhs.uk/FHIR/R4/Patient
        When client makes a http GET request to cache for patient <patient_id> and resource <resource> with unique query param
        Then cache returns 200 status
        And the response includes X-Cache-Status header with a value MISS
        And X-Cache-Key header is present in response
        Examples:
        | patient_id          | resource              |
        | 9730676399          | empty_value           |
        | 9730676399          | RelatedPerson         |


    Scenario Outline: PDS response is cached
        Given a unique value is created for query parameter
        And base url is https://mock.validated-relationships-service-dev.national.nhs.uk/FHIR/R4/Patient
        When client makes a http GET request to cache for patient <patient_id> and resource <resource> with unique query param
        Then cache returns 200 status
        And X-Cache-Key header is present in response
        Then the response includes X-Cache-Status header with a value MISS
        When client makes a http GET request to cache for patient <patient_id> and resource <resource> with unique query param
        Then cache returns 200 status
        Then the response includes X-Cache-Status header with a value HIT
        And X-Cache-Key header is present in response
        Examples:
        | patient_id          | resource             |
        | 9730676399          | empty_value           |
        | 9730676399          | RelatedPerson         |


    Scenario Outline: when cache is invalidated for a response
        Given a unique value is created for query parameter
        And base url is https://mock.validated-relationships-service-dev.national.nhs.uk/FHIR/R4/Patient
        When client makes a http GET request to cache for patient <patient_id> and resource <resource> with unique query param
        Then cache returns 200 status
        Then the response includes X-Cache-Status header with a value MISS
        And X-Cache-Key header is present in response
        Given the dynamodb record will be cleared for X-Cache-Key
        When client makes a http GET request to cache for patient <patient_id> and resource <resource> with unique query param
        Then cache returns 200 status
        And the response includes X-Cache-Status header with a value MISS
        And X-Cache-Key header is present in response
        Examples:
        | patient_id          | resource             |
        | 9730676399          | empty_value           |
        | 9730676399          | RelatedPerson         |


    Scenario Outline: when response from PDS Non 2xx, it shouldn't be added to cache
        Given a unique value is created for query parameter
        And base url is https://mock.validated-relationships-service-dev.national.nhs.uk/FHIR/R4/Patient
        When client makes a http GET request to cache for patient <patient_id> and resource <resource> with unique query param
        Then cache returns 400 status
        And the response includes X-Cache-Status header with a value MISS
        And X-Cache-Key header is present in response
        Examples:
        | patient_id          | resource             |
        | 9730676407          | empty_value           |
        | 9730676407          | RelatedPerson         |
