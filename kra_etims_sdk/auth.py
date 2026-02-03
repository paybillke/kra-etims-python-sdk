import base64, json, time, os, requests
from .exceptions import AuthenticationException


class AuthClient:
    def __init__(self, config: dict):
        self.config = config
        self.cache_file = config.get("cache_file", "/tmp/kra_etims_token.json")

    def token(self, force=False):
        if not force:
            cached = self._read_cache()
            if cached and time.time() < cached["expires_at"]:
                return cached["access_token"]

        token = self._fetch_token()
        self._write_cache(token)
        return token["access_token"]

    def forget_token(self):
        if os.path.exists(self.cache_file):
            os.unlink(self.cache_file)

    def _fetch_token(self):
        env = self.config["env"]
        auth = self.config["auth"][env]

        url = f"{auth['token_url']}?grant_type=client_credentials"
        headers = {
            "Authorization": "Basic " + base64.b64encode(
                f"{auth['consumer_key']}:{auth['consumer_secret']}".encode()
            ).decode(),
            "Accept": "application/json"
        }

        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code != 200:
            raise AuthenticationException(r.text, r.status_code)

        data = r.json()
        if "access_token" not in data:
            raise AuthenticationException("Invalid token response")

        return {
            "access_token": data["access_token"],
            "expires_at": time.time() + int(data.get("expires_in", 3600)) - 60,
        }

    def _read_cache(self):
        if not os.path.exists(self.cache_file):
            return None
        with open(self.cache_file) as f:
            return json.load(f)

    def _write_cache(self, data):
        with open(self.cache_file, "w") as f:
            json.dump(data, f)
