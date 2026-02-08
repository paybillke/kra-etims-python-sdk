import requests
from .exceptions import ApiException, AuthenticationException


class BaseClient:
    endpoints = {
        # INITIALIZATION
        'selectInitOsdcInfo': '/selectInitOsdcInfo',

        # CODE LIST
        'selectCodeList': '/selectCodeList',

        # CUSTOMER
        'selectCustomer': '/selectCustomer',

        # NOTICE
        'selectNoticeList': '/selectNoticeList',

        # ITEM
        'selectItemClsList': '/selectItemClsList',
        'selectItemList': '/selectItemList',
        'saveItem': '/saveItem',
        'SaveItemComposition': '/saveItemComposition',

        # BRANCH / CUSTOMER
        'selectBhfList': '/selectBhfList',
        'saveBhfCustomer': '/saveBhfCustomer',
        'saveBhfUser': '/saveBhfUser',
        'saveBhfInsurance': '/saveBhfInsurance',

        # IMPORTED ITEMS
        'selectImportItemList': '/selectImportItemList',
        'updateImportItem': '/updateImportItem',

        # SALES / PURCHASES
        'TrnsSalesSaveWrReq': '/saveTrnsSalesOsdc',
        'selectTrnsPurchaseSalesList': '/selectTrnsPurchaseSalesList',
        'insertTrnsPurchase': '/insertTrnsPurchase',

        # STOCK
        'selectStockMoveList': '/selectStockMoveList',
        'insertStockIO': '/insertStockIO',
        'saveStockMaster': '/saveStockMaster',
    }

    def __init__(self, config, auth):
        self.config = config
        self.auth = auth

    def base_url(self):
        env = self.config["env"]
        return self.config["api"][env]["base_url"].rstrip("/")

    def timeout(self):
        return self.config.get("http", {}).get("timeout", 30)

    def endpoint(self, key: str):
        if key.startswith("/"):
            raise ApiException(f"Endpoint key expected, path given [{key}]. Pass endpoint keys only.", 500)

        if key not in self.endpoints:
            raise ApiException(f"Endpoint [{key}] not configured", 500)

        return self.endpoints[key]

    def get(self, endpoint_key, params=None):
        return self._send("GET", endpoint_key, params or {})

    def post(self, endpoint_key, data=None):
        return self._send("POST", endpoint_key, data or {})

    def _send(self, method, endpoint_key, data):
        endpoint = self.endpoint(endpoint_key)
        response = self._request(method, endpoint, data)

        if self._is_token_expired(response):
            self.auth.forget_token()
            self.auth.token(force=True)
            response = self._request(method, endpoint, data)

        return self._unwrap(response)

    def _request(self, method, endpoint, data):
        url = self.base_url() + endpoint
        headers = self._headers(endpoint)

        if method.upper() == "GET" and data:
            response = requests.get(url, params=data, headers=headers, timeout=self.timeout())
        else:
            response = requests.request(
                method.upper(),
                url,
                json=data,
                headers=headers,
                timeout=self.timeout()
            )

        return response

    def _headers(self, endpoint):
        if endpoint.endswith("/selectInitOsdcInfo"):
            return {
                "Authorization": f"Bearer {self.auth.token()}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }

        return {
            "Authorization": f"Bearer {self.auth.token()}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "tin": self.config.get("oscu", {}).get("tin", ""),
            "bhfId": self.config.get("oscu", {}).get("bhf_id", ""),
            "cmcKey": self.config.get("oscu", {}).get("cmc_key", ""),
        }

    def _is_token_expired(self, response):
        if response.status_code == 401:
            return True
        try:
            fault = response.json().get("fault", {}).get("faultstring", "")
            return "access token expired" in fault.lower() or "invalid token" in fault.lower()
        except Exception:
            return False

    def _unwrap(self, response):
        try:
            json_data = response.json()
        except Exception:
            raise ApiException(response.text, response.status_code)

        # KRA business error
        if json_data.get("resultCd") and json_data["resultCd"] != "000":
            raise ApiException(
                json_data.get("resultMsg", "KRA business error"),
                400,
                json_data.get("resultCd"),
                json_data
            )

        # HTTP errors
        if 200 <= response.status_code < 300:
            return json_data

        if response.status_code == 401:
            raise AuthenticationException("Unauthorized: Invalid or expired token")

        return json_data
