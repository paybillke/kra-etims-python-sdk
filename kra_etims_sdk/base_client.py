import requests
from .exceptions import ApiException, AuthenticationException


class BaseClient:
    def __init__(self, config, auth):
        self.config = config
        self.auth = auth

    def base_url(self):
        return self.config["api"][self.config["env"]]["base_url"].rstrip("/")

    def endpoint(self, key):
        if key not in self.config["endpoints"]:
            raise ApiException(f"Endpoint [{key}] not configured", 500)
        return self.config["endpoints"][key]

    def post(self, endpoint_key, data):
        return self._send("POST", endpoint_key, data)

    def _send(self, method, endpoint_key, data):
        endpoint = self.endpoint(endpoint_key)
        response = self._request(method, endpoint, data)

        if response.status_code == 401:
            self.auth.forget_token()
            self.auth.token(force=True)
            response = self._request(method, endpoint, data)

        return self._unwrap(response)

    def _request(self, method, endpoint, data):
        url = self.base_url() + endpoint
        headers = self._headers(endpoint)
        return requests.request(method, url, json=data, headers=headers, timeout=30)

    def _headers(self, endpoint):
        if endpoint.endswith("/initialize"):
            return {
                "Authorization": f"Bearer {self.auth.token()}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }

        return {
            "Authorization": f"Bearer {self.auth.token()}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "tin": self.config["oscu"]["tin"],
            "bhfId": self.config["oscu"]["bhf_id"],
            "cmcKey": self.config["oscu"]["cmc_key"],
        }

    def _unwrap(self, response):
        try:
            json = response.json()
        except Exception:
            raise ApiException(response.text, response.status_code)

        if json.get("resultCd") and json["resultCd"] != "0000":
            raise ApiException(json.get("resultMsg"), 400, json["resultCd"], json)

        if response.status_code == 401:
            raise AuthenticationException("Unauthorized")

        return json
