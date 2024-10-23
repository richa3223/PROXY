# coding: utf-8
import pprint
import re  # noqa: F401

import six


class Detail_metadata(object):
    _types = {
        "client_key": "str",
        "correlation_id": "str",
        "created": "str",
        "request_id": "str",
    }

    _attribute_map = {
        "client_key": "client-key",
        "correlation_id": "correlation-id",
        "created": "created",
        "request_id": "request-id",
    }

    def __init__(
        self, client_key=None, correlation_id=None, created=None, request_id=None
    ):  # noqa: E501
        self._client_key = None
        self._correlation_id = None
        self._created = None
        self._request_id = None
        self.client_key = client_key
        self.correlation_id = correlation_id
        self.created = created
        self.request_id = request_id

    @property
    def client_key(self):
        return self._client_key

    @client_key.setter
    def client_key(self, client_key):
        self._client_key = client_key

    @property
    def correlation_id(self):
        return self._correlation_id

    @correlation_id.setter
    def correlation_id(self, correlation_id):
        self._correlation_id = correlation_id

    @property
    def created(self):
        return self._created

    @created.setter
    def created(self, created):
        self._created = created

    @property
    def request_id(self):
        return self._request_id

    @request_id.setter
    def request_id(self, request_id):
        self._request_id = request_id

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
        if issubclass(Detail_metadata, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self):
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        return self.to_str()

    def __eq__(self, other):
        if not isinstance(other, Detail_metadata):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other
