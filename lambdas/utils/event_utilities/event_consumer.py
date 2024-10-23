"""Consume events published to the event bus"""

from typing import Callable, Type, TypeVar

T = TypeVar("T")
UnmarshallFunc = Callable[[dict, Type[T]], T]


def unmarshall(event: dict, func: UnmarshallFunc, event_binding: Type[T]) -> T:
    """Unmarshall an event into an event binding with the passed unmarshaller function.

    Assumes `event` contains `detail`, `detail-type` and `source` items. If one a value
    is missing then it will be added as `None`. Only these items are passed within the
    `event` passed into `func` with updated names for compatibility with event schemas
    event bindings.

    Args:
        event (dict): The event to be unmarshalled.
        func (UnmarshallFunc): The unmarshall function.
        event_binding (T): The desired binding class to unmarshall into.

    Returns:
        T: The unmarshalled `event` as the `event_binding` type.
    """
    event = {
        "Detail": event.get("detail"),
        "DetailType": event.get("detail-type"),
        "Source": event.get("source"),
    }
    return func(event, event_binding)
