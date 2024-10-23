# coding: utf-8
import pprint
import re  # noqa: F401

import six

from lambdas.utils.code_bindings.validation_result.Detail import (  # noqa: F401,E501
    Detail,
)


class Event(object):

    _types = {
        "Detail": "Detail",
        "DetailType": "str",
        "EventBusName": "str",
        "Source": "str",
    }

    _attribute_map = {
        "Detail": "Detail",
        "DetailType": "DetailType",
        "EventBusName": "EventBusName",
        "Source": "Source",
    }

    def __init__(
        self, Detail=None, DetailType=None, EventBusName=None, Source=None
    ):  # noqa: E501
        self._Detail = None
        self._DetailType = None
        self._EventBusName = None
        self._Source = None
        self.Detail = Detail
        self.DetailType = DetailType
        self.EventBusName = EventBusName
        self.Source = Source

    @property
    def Detail(self):

        return self._Detail

    @Detail.setter
    def Detail(self, Detail):

        self._Detail = Detail

    @property
    def DetailType(self):

        return self._DetailType

    @DetailType.setter
    def DetailType(self, DetailType):

        self._DetailType = DetailType

    @property
    def EventBusName(self):

        return self._EventBusName

    @EventBusName.setter
    def EventBusName(self, EventBusName):

        self._EventBusName = EventBusName

    @property
    def Source(self):

        return self._Source

    @Source.setter
    def Source(self, Source):

        self._Source = Source

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
        if issubclass(Event, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self):
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        return self.to_str()

    def __eq__(self, other):
        if not isinstance(other, Event):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other
