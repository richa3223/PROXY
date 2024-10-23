"""Extendeds FHIRServer client that allows headers sent via request_join to be extended."""

import uuid

from fhirclient.server import FHIRServer


class PDSFHIRClient(FHIRServer):
    """Extendeds FHIRServer client that allows headers sent via request_join to be extended."""

    _headers = {"Accept": "application/json", "X-Request-ID": str(uuid.uuid4())}

    @property
    def headers(self) -> dict:
        """Dictionary of headers that will be included with every request"""
        return self._headers

    def request_json(self, path: str, nosign=False):
        """Perform a request for JSON data against the server's base with the
        given relative path.

        Overrides the base function to add additional headers

        :param str path: The path to append to `base_uri`
        :param bool nosign: If set to True, the request will not be signed
        :throws: Exception on HTTP status >= 400
        :returns: Decoded JSON response
        """

        res = self._get(path, self.headers, nosign)

        return res.json()
