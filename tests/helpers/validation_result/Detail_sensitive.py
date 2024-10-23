from dataclasses import dataclass


@dataclass
class Detail_sensitive:
    patient_identifier: str
    proxy_identifier: str

    def to_dict(self):
        result = {}
        result["patient-identifier"] = self.patient_identifier
        result["proxy-identifier"] = self.proxy_identifier
        return result
