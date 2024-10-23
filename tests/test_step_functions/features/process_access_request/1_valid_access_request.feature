Feature: Process Access request for the process_access_request_state_machine step function

  Scenario: Confirm access request is processed correctly
    Given a state machine input JSON:
        {
            "version": "0",
            "id": "f9c3556a-9d40-b8d3-f95d-9ddacf9af61d",
            "detail-type": "Event from aws:dynamodb",
            "source": "Pipe main-DynamoDBStreamToEventBridge-pipe",
            "account": "723625676534",
            "time": "2024-06-27T12:20:23Z",
            "region": "eu-west-2",
            "resources": [],
            "detail": {
                "eventId": "588b42c9b84b8030615b67aa710f53c3",
                "eventType": "ACCESS_REQUEST_CREATED",
                "referenceCode": "Value_TBC"
            }
        }
    And a create access request is created using questionnaire_response_prn.json
    When the standard step function process-access-request-state-machine is called
    And the test will wait for step function to complete
    Then the dynamodb record will have a status of ACCESS_REQUEST_READY_FOR_AUTHORISATION
    And the step function will succeed
    And the response will be JSON


  Scenario: Confirm when dynamo db item does not exist an error is raised
    Given a state machine input JSON:
        {
            "version": "0",
            "id": "f9c3556a-9d40-b8d3-f95d-9ddacf9af61d",
            "detail-type": "Event from aws:dynamodb",
            "source": "Pipe main-DynamoDBStreamToEventBridge-pipe",
            "account": "723625676534",
            "time": "2024-06-27T12:20:23Z",
            "region": "eu-west-2",
            "resources": [],
            "detail": {
                "eventId": "588b42c9b84b8030615b67aa710f53c3",
                "eventType": "ACCESS_REQUEST_CREATED",
                "referenceCode": "DOES_NOT_EXIST_1111"
            }
        }
    When the standard step function process-access-request-state-machine is called
    And the test will wait for step function to complete
    Then the step function will fail with cause "Failed to retrieve record from dynamodb."


  Scenario Outline: When related PDS records do not exist
    Given a state machine input JSON:
        {
            "version": "0",
            "id": "f9c3556a-9d40-b8d3-f95d-9ddacf9af61d",
            "detail-type": "Event from aws:dynamodb",
            "source": "Pipe main-DynamoDBStreamToEventBridge-pipe",
            "account": "723625676534",
            "time": "2024-06-27T12:20:23Z",
            "region": "eu-west-2",
            "resources": [],
            "detail": {
                "eventId": "588b42c9b84b8030615b67aa710f53c3",
                "eventType": "ACCESS_REQUEST_CREATED",
                "referenceCode": "Value_TBC"
            }
        }
    And a create access request is created using questionnaire_response_invalid_nhs_numbers.json
    When the standard step function process-access-request-state-machine is called
    And the test will wait for step function to complete
    Then the step function will fail with cause "Failed to successfully retrieve patient information."

  Scenario: When relationship is 'PRN' then validate realtionship is run
    Given a state machine input JSON:
        {
            "version": "0",
            "id": "f9c3556a-9d40-b8d3-f95d-9ddacf9af61d",
            "detail-type": "Event from aws:dynamodb",
            "source": "Pipe main-DynamoDBStreamToEventBridge-pipe",
            "account": "723625676534",
            "time": "2024-06-27T12:20:23Z",
            "region": "eu-west-2",
            "resources": [],
            "detail": {
                "eventId": "588b42c9b84b8030615b67aa710f53c3",
                "eventType": "ACCESS_REQUEST_CREATED",
                "referenceCode": "Value_TBC"
            }
        }
    And a create access request is created using questionnaire_response_prn.json
    When the standard step function process-access-request-state-machine is called
    And the test will wait for step function to complete
    Then the dynamodb record will have a status of ACCESS_REQUEST_READY_FOR_AUTHORISATION
    And the step function will succeed
    And the validate-relationships-state-machine step function has not been run
    And the response will be JSON

  Scenario Outline: When relationship is NOT 'PRN' then validate realtionship is not run
    Given a state machine input JSON:
        {
            "version": "0",
            "id": "f9c3556a-9d40-b8d3-f95d-9ddacf9af61d",
            "detail-type": "Event from aws:dynamodb",
            "source": "Pipe main-DynamoDBStreamToEventBridge-pipe",
            "account": "723625676534",
            "time": "2024-06-27T12:20:23Z",
            "region": "eu-west-2",
            "resources": [],
            "detail": {
                "eventId": "588b42c9b84b8030615b67aa710f53c3",
                "eventType": "ACCESS_REQUEST_CREATED",
                "referenceCode": "Value_TBC"
            }
        }
    And a create access request is created using questionnaire_response_personal.json
    When the standard step function process-access-request-state-machine is called
    And the test will wait for step function to complete
    Then the dynamodb record will have a status of ACCESS_REQUEST_READY_FOR_AUTHORISATION
    And the step function will succeed
    And the validate-relationships-state-machine step function has not been run
    And the response will be JSON
