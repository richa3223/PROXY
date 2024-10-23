from dataclasses import dataclass


@dataclass
class Detail_standard:
    proxy_identifier_type: str
    relationship_type: str
    validation_result_info: str

    def to_dict(self):
        result = {}
        result["proxy-identifier-type"] = self.proxy_identifier_type
        result["relationship-type"] = self.relationship_type
        result["validation-result-info"] = self.validation_result_info
        return result
