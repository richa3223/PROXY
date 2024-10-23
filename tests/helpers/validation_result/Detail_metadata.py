from dataclasses import dataclass
from typing import TypedDict


@dataclass
class Detail_metadata:
    client_key: str
    correlation_id: str
    created: str
    request_id: str

    def to_dict(self):
        result = {}
        result["client-key"] = self.client_key
        result["correlation-id"] = self.correlation_id
        result["created"] = self.created
        result["request-id"] = self.request_id
        return result
