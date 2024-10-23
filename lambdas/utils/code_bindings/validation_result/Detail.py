# coding: utf-8
import pprint
import re  # noqa: F401

import six

from lambdas.utils.code_bindings.validation_result.Detail_metadata import (  # noqa: F401,E501
    Detail_metadata,
)
from lambdas.utils.code_bindings.validation_result.Detail_sensitive import (  # noqa: F401,E501
    Detail_sensitive,
)
from lambdas.utils.code_bindings.validation_result.Detail_standard import (  # noqa: F401,E501
    Detail_standard,
)


class Detail(object):
    _types = {
        "metadata": "Detail_metadata",
        "sensitive": "Detail_sensitive",
        "standard": "Detail_standard",
    }

    _attribute_map = {
        "metadata": "metadata",
        "sensitive": "sensitive",
        "standard": "standard",
    }

    def __init__(self, metadata=None, sensitive=None, standard=None):  # noqa: E501
        self._metadata = None
        self._sensitive = None
        self._standard = None
        self.metadata = metadata
        self.sensitive = sensitive
        self.standard = standard

    @property
    def metadata(self):
        return self._metadata

    @metadata.setter
    def metadata(self, metadata):
        self._metadata = metadata

    @property
    def sensitive(self):
        return self._sensitive

    @sensitive.setter
    def sensitive(self, sensitive):
        self._sensitive = sensitive

    @property
    def standard(self):
        return self._standard

    @standard.setter
    def standard(self, standard):
        self._standard = standard

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
        if issubclass(Detail, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self):
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        return self.to_str()

    def __eq__(self, other):
        if not isinstance(other, Detail):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other
