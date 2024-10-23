from dataclasses import dataclass

from .Detail import Detail


@dataclass
class Event:
    Detail: Detail
    DetailType: str
    EventBusName: str
    Source: str

    def to_dict(self):
        result = {}
        result["Detail"] = self.Detail.to_dict()
        result["DetailType"] = self.DetailType
        result["EventBusName"] = self.EventBusName
        result["Source"] = self.Source
        return result
