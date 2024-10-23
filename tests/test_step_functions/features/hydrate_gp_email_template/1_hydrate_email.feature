Feature: Hydrate GP email template

    Background:
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
                    "eventType": "ACCESS_REQUEST_READY_FOR_AUTHORISATION",
                    "referenceCode": "Value_TBC"
                }
            }
        And an access request ready for authorisation record is created using questionnaire_response.json

    Scenario: Confirm email is generated correctly (AC1)
        When the step function hydrate-gp-email-template-state-machine is called
        Then the step function will return 200
        And the dynamodb record is updated to GP_AUTHORISATION_REQUEST_CREATED
        And the hydrated email template is is saved to s3
    @NPA-3247
    Scenario: Missing GP email template (AC1)
        Given the email template does not exist
        When the step function hydrate-gp-email-template-state-machine is called
        Then email hydration will fail
    @NPA-3247
    Scenario: Missing email address (AC2)
        Given the ODS code does not exist
        When the step function hydrate-gp-email-template-state-machine is called
        Then email hydration will fail
    @NPA-3248 @skip
    Scenario Outline: Deal with unpopulated data elements (AC1)
        Given a <field> provided by <source> is <missing>
        When the step function hydrate-gp-email-template-state-machine is called
        Then the step function will return 200
        And the dynamodb record is updated to GP_AUTHORISATION_REQUEST_CREATED
        And in the hydrated email the <field> will appear as <unknown>
    Examples:
        |source                |field              | path                                  | missing | unknown     |
        |PDS                   |Patient Address    | address[0].line                       | NULL    | <unknown>   |
        |PDS                   |Patient Address    | address[0].line                       | MISSING | <unknown>   |
        |QuestionnaireResponse |Patient First Name | item[1].item[1].answer[0].valueString | NULL    | <unknown>   |
        |QuestionnaireResponse |Patient First Name | item[1].item[1].answer[0].valueString | MISSING | <unknown>   |
        |QuestionnaireResponse |Patient NHS Number | item[1].item[0].answer[0].valueString | NULL    | <unknown>   |
        |QuestionnaireResponse |Patient NHS Number | item[1].item[0].answer[0].valueString | MISSING | <unknown>   |
