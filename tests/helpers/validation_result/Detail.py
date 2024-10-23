from dataclasses import dataclass

from .Detail_metadata import Detail_metadata
from .Detail_sensitive import Detail_sensitive
from .Detail_standard import Detail_standard


@dataclass
class Detail:
    metadata: Detail_metadata
    sensitive: Detail_sensitive
    standard: Detail_standard

    def to_dict(self):
        result = {}
        result["metadata"] = self.metadata.to_dict()
        result["sensitive"] = self.sensitive.to_dict()
        result["standard"] = self.standard.to_dict()
        return result
