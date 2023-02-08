"""Digest Auth Request"""

import logging
import hashlib
import re
import requests
from requests import Response

from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


class DigestAuthRequest:
    """Create HTTP requests usig digest authorization.
    For some reason the HTTPDigestAuth from requests.auth does
    not work with Fronius Solarnet. That's why this class was created."""

    _host: str
    _username: str
    _password: str
    _auth_data: dict[str, str]

    def __init__(self, host: str, username: str, password: str, hass: HomeAssistant):
        self._host = host
        self._username = username
        self._password = password
        self._auth_data = None
        self._hass = hass

    async def get(self, digest_uri: str, headers: dict[str, str] = None) -> Response:
        """GET request"""
        url = f"{self._host}{digest_uri}"

        response = None

        if self._auth_data is not None:
            headers = {
                "Authorization": create_auth_header(
                    "GET", self._auth_data, digest_uri, self._username, self._password
                )
            }

        def first_request():
            _LOGGER.debug("GET %s with headers=%s", url, headers)
            response = requests.get(url, headers=headers)
            return response

        response = await self._hass.async_add_executor_job(first_request)

        if response.status_code == 401:
            self._auth_data = parse_auth_data_from_response(response)
            headers = {
                "Authorization": create_auth_header(
                    "GET", self._auth_data, digest_uri, self._username, self._password
                )
            }

            def second_request():
                _LOGGER.debug("GET %s with headers=%s", url, headers)
                response = requests.get(url, headers=headers)
                return response

            response = await self._hass.async_add_executor_job(second_request)

        if response.status_code != 200:
            request_string = f"GET {url}"
            raise Exception(
                f"Request {request_string} failed with "
                f"status code {response.status_code} "
                f"and response {response.text}"
            )

        return response

    # TODO: Refactor to one shared "request" method for GET and POST
    async def post_json(
        self, digest_uri: str, headers: dict[str, str] = None, payload: object = None
    ) -> Response:
        """POST request with JSON data"""
        url = f"{self._host}{digest_uri}"

        response = None

        if self._auth_data is not None:
            headers = {
                "Authorization": create_auth_header(
                    "POST", self._auth_data, digest_uri, self._username, self._password
                )
            }

        def first_request():
            _LOGGER.debug("POST %s with headers=%s", url, headers)
            response = requests.post(url, headers=headers, json=payload)
            return response

        response = await self._hass.async_add_executor_job(first_request)

        if response.status_code == 401:
            self._auth_data = parse_auth_data_from_response(response)
            headers = {
                "Authorization": create_auth_header(
                    "POST", self._auth_data, digest_uri, self._username, self._password
                )
            }

            def second_request():
                _LOGGER.debug("POST %s with headers=%s", url, headers)
                response = requests.post(url, headers=headers, json=payload)
                return response

            response = await self._hass.async_add_executor_job(second_request)

        if response.status_code != 200:
            request_string = f"GET {url}"
            raise Exception(
                f"Request {request_string} failed with "
                f"status code {response.status_code} "
                f"and response {response.text}"
            )

        return response


def create_auth_header(
    method: str,
    auth_data: dict[str, str],
    digest_uri: str,
    username: str,
    password: str,
) -> str:
    """Create headers for digest auth request"""

    realm = auth_data["realm"]
    algorithm = auth_data["algorithm"]
    nonce = auth_data["nonce"]
    qop = auth_data["qop"]
    nonce_count = "00000001"
    cnonce = "NaN"

    if algorithm == "MD5":
        ha1 = hashlib.md5(f"{username}:{realm}:{password}".encode()).hexdigest()
        ha2 = hashlib.md5(f"{method}:{digest_uri}".encode()).hexdigest()
        response = hashlib.md5(
            f"{ha1}:{nonce}:{nonce_count}:{cnonce}:{qop}:{ha2}".encode()
        ).hexdigest()
        auth_header = (
            f"Digest "
            f"username={username}, "
            f"realm={realm}, "
            f"nonce={nonce}, "
            f"uri={digest_uri}, "
            f"response={response}, "
            f"qop={qop}, "
            f"nc={nonce_count}, "
            f"cnonce={cnonce}"
        )
    else:
        raise Exception(f'Algorithm "{algorithm}" not supported')
    return auth_header


def parse_auth_data_from_response(response) -> dict[str, str]:
    """Extract auth data from response"""
    auth_data = {}
    auth_data_string = response.headers["X-WWW-Authenticate"]
    auth_data["realm"] = parse_parameter_from_auth_data("realm", auth_data_string)
    auth_data["algorithm"] = parse_parameter_from_auth_data(
        "algorithm", auth_data_string
    )
    auth_data["nonce"] = parse_parameter_from_auth_data("nonce", auth_data_string)
    auth_data["qop"] = parse_parameter_from_auth_data("qop", auth_data_string)
    return auth_data


def parse_parameter_from_auth_data(parameter: str, auth_data_string: str) -> str:
    """Extract a parameter from an auth data string"""
    regex_pattern = f"{parameter}=[^,]+"
    result = re.findall(regex_pattern, auth_data_string)
    value = result[0].replace(parameter, "").replace("=", "").replace('"', "")
    return value
