# coding: utf-8
import pprint
import re  # noqa: F401

import six


class Detail_standard(object):

    _types = {
        "proxy_identifier_type": "str",
        "relationship_type": "str",
        "validation_result_info": "object",
    }

    _attribute_map = {
        "proxy_identifier_type": "proxy-identifier-type",
        "relationship_type": "relationship-type",
        "validation_result_info": "validation-result-info",
    }

    def __init__(
        self,
        proxy_identifier_type=None,
        relationship_type=None,
        validation_result_info=None,
    ):  # noqa: E501
        self._proxy_identifier_type = None
        self._relationship_type = None
        self._validation_result_info = None
        self.proxy_identifier_type = proxy_identifier_type
        self.relationship_type = relationship_type
        self.validation_result_info = validation_result_info

    @property
    def proxy_identifier_type(self):

        return self._proxy_identifier_type

    @proxy_identifier_type.setter
    def proxy_identifier_type(self, proxy_identifier_type):

        self._proxy_identifier_type = proxy_identifier_type

    @property
    def relationship_type(self):

        return self._relationship_type

    @relationship_type.setter
    def relationship_type(self, relationship_type):

        self._relationship_type = relationship_type

    @property
    def validation_result_info(self):

        return self._validation_result_info

    @validation_result_info.setter
    def validation_result_info(self, validation_result_info):

        self._validation_result_info = validation_result_info

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
        if issubclass(Detail_standard, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self):
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        return self.to_str()

    def __eq__(self, other):
        if not isinstance(other, Detail_standard):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other
