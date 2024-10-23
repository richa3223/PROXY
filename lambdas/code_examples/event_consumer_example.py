from lambdas.utils.code_bindings.validation_result import Event as ValidationResult
from lambdas.utils.code_bindings.validation_result import (
    Marshaller as ValidationResultMarshaller,
)
from lambdas.utils.event_utilities.event_consumer import unmarshall


def log_unmarshalled_validation_result(event) -> str:
    validation_result = unmarshall(
        event,
        ValidationResultMarshaller.unmarshall,
        ValidationResult,
    )
    return repr(validation_result)


def lambda_handler(event: dict, context: dict) -> str:
    return log_unmarshalled_validation_result(event)
