# Create Access Request

Returns a FHIR Operation Outcome resource when given a FHIR Questionnaire Response resource.

## Parameters

The lambda requires the following inputs

| Parameter name | Data type | Purpose               |
| -------------- | --------- | --------------------- |
| headers        | dict      | Headers passed to API |
| body           | string    | Body of the request   |

## Outputs

The lambda is expected to return the following

| Output path | Data type | Purpose                                 |
| ----------- | --------- | --------------------------------------- |
| statusCode  | int       | The HTTP status code for the operation. |
| body        | string    | The FHIR Operation Outcome resource.    |


## Local Testing

The following is a code sample of a python script that will allow the lambda to be run.

```python

environ["DYNAMODB_TABLE_NAME"] = ""
from lambdas.create_access_request.main import lambda_handler

headers = {
    "Content-Type": "application/fhir+json",
}
input = {'body': '{"resourceType":"QuestionnaireResponse","status":"completed","authored":"2024-03-24T16:32:12.363Z","source":{"type":"RelatedPerson","identifier":{"value":"9730675988","system":"https://fhir.nhs.uk/Id/nhs-number"}},"questionnaire":"Questionnaire/example-questionnaire","item":[{"linkId":"proxy_details","text":"Proxy details","item":[{"linkId":"nhs_number","text":"NHS Number","answer":[{"valueString":"9730675988"}]},{"linkId":"relationship","text":"Relationship","answer":[{"valueCoding":{"system":"http://terminology.hl7.org/CodeSystem/v3-RoleCode","code":"Personal","display":"???"}}]}]},{"linkId":"patient_details","text":"Patient details","item":[{"linkId":"nhs_number","text":"NHS Number","answer":[{"valueString":"9730676445"}]},{"linkId":"first_name","text":"First Name","answer":[{"valueString":"Joanna"}]},{"linkId":"last_name","text":"Last name","answer":[{"valueString":"FILSON"}]},{"linkId":"date_of_birth","text":"Date of Birth","answer":[{"valueDate":"2011-02-28"}]},{"linkId":"postcode","text":"Postcode","answer":[{"valueString":"DN19 7SU"}]}]},{"linkId":"requested_services","text":"Requested services","answer":[{"valueCoding":{"system":"http://terminology.hl7.org/CodeSystem/consentaction","code":"appointments","display":"???"}},{"valueCoding":{"system":"http://terminology.hl7.org/CodeSystem/consentaction","code":"medicines","display":"???"}},{"valueCoding":{"system":"http://terminology.hl7.org/CodeSystem/consentaction","code":"records","display":"???"}},{"valueCoding":{"system":"http://terminology.hl7.org/CodeSystem/consentaction","code":"demographics","display":"???"}}]}]}', 'headers': {'accesstoken.auth_level': 'P9', 'accesstoken.auth_user_id': '9730675929', 'correlationId': '15cabfa8-ece5-4cd7-975c-bef3952aba82', 'originalRequestUrl': 'https://internal-dev.api.service.nhs.uk/validated-relationships/FHIR/R4/QuestionnaireResponse', 'requestId': '1c66b74d-6a50-4473-a786-be43207c68d1'}}

result = lambda_handler(input, None)

print("--- ***** ---")
print("Questionnaire Response result:")
print("Response Status Code: " + str(result['statusCode']))
print("Response Body: " + str(result['body']))
```

## Deployment

This lambda function is deployed to AWS using Terraform CI / CD pipeline.
