# Event Bridge Code Bindings

## How to Update Code Bindings
1. Update the schema found in the './event-schemas' folder at the root of the repo. This is in the JSONSchema Draft 4 format, any other version of JSON Schema is not supported by AWS Event Bridge. This can be changed to the OpenAPI3 standard in the future if necessary.
2. Re-deploy the common terraform stack to overwrite existing event schema on AWS with the new schema.
3. Using the AWS console go to the EventBridge service, scroll down to Schema Registry.
4. Look for the registry called '{workspace}-business_events_schema_registry'.
5. Click on the schema you have just deployed and click 'Download Code Bindings'
6. Replace the code bindings in the appropriate folder inside 'lambdas/untils/code_bindings'
7. Fix imports for all the code binding files from
```python
import schema.validation_result....
```
to
```python
import lambdas.utils.code_bindings.validation_result....
```
8. Find and fix unused imports in the bindings using python vulture
9. Format the bindings code using black formatter

## How to Create new Code Bindings for new events
(read how to update first)

1. Like step 1 from updating the bindings, create the schema and put it in the appropriate folder.
2. Re-deploy the common stack, *there is no need to change the terraform code*, it will pick up any schema inside the './event-schemas' folder
3. Using the AWS console go to the EventBridge service, scroll down to Schema Registry.
4. Follow steps 4 through 9 from the 'How to update code bindings' section.
5. Update the publish utility inside 'lambdas/utils/event_utilities/event_publisher.py' by adding a new method to publish the schema you have just created code bindings for.


## Troubleshooting AWS not creating code bindings

If AWS cannot create code bindings for python (or any other language), make sure the JSONDraft4  schema you deployed does not make use of the '#ref' inside the definitions block to reference items defined in the same definitions block.
