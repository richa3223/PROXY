# coding: utf-8
import pprint
import re  # noqa: F401

import six


class Detail_sensitive(object):

    _types = {"patient_identifier": "str", "proxy_identifier": "str"}

    _attribute_map = {
        "patient_identifier": "patient-identifier",
        "proxy_identifier": "proxy-identifier",
    }

    def __init__(self, patient_identifier=None, proxy_identifier=None):  # noqa: E501
        self._patient_identifier = None
        self._proxy_identifier = None
        self.patient_identifier = patient_identifier
        self.proxy_identifier = proxy_identifier

    @property
    def patient_identifier(self):

        return self._patient_identifier

    @patient_identifier.setter
    def patient_identifier(self, patient_identifier):

        self._patient_identifier = patient_identifier

    @property
    def proxy_identifier(self):

        return self._proxy_identifier

    @proxy_identifier.setter
    def proxy_identifier(self, proxy_identifier):

        self._proxy_identifier = proxy_identifier

    def to_dict(self):
        result = {}

        for attr, _ in six.iteritems(self._types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(
                    map(lambda x: x.to_dict() if hasattr(x, "to_dict") else x, value)
                )
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(
                    map(
                        lambda item: (
                            (item[0], item[1].to_dict())
                            if hasattr(item[1], "to_dict")
                            else item
                        ),
                        value.items(),
                    )
                )
            else:
                result[attr] = value
        if issubclass(Detail_sensitive, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self):
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        return self.to_str()

    def __eq__(self, other):
        if not isinstance(other, Detail_sensitive):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other
