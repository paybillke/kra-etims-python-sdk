import requests
from .exceptions import ApiException, AuthenticationException


class BaseOClient:
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
        'saveItemComposition': '/saveItemComposition',

        # BRANCH / CUSTOMER
        'selectBhfList': '/selectBhfList',
        'saveBhfCustomer': '/saveBhfCustomer',
        'saveBhfUser': '/saveBhfUser',
        'saveBhfInsurance': '/saveBhfInsurance',

        # IMPORTED ITEMS
        'selectImportItemList': '/selectImportItemList',
        'updateImportItem': '/updateImportItem',

        # SALES / PURCHASES
        'saveTrnsSalesOsdc': '/saveTrnsSalesOsdc',
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

    def base_url(self) -> str:
        env = self.config.get("env")

        if env == "sbx":
            url = "https://etims-api-sbx.kra.go.ke/etims-api"
        else:
            url = "https://etims-api.kra.go.ke/etims-api"

        return url.rstrip("/").strip()
    
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

        result_cd = json_data.get("resultCd")
        result_msg = json_data.get("resultMsg", "Unknown API response")

        # ---------------------------------
        # HTTP-level handling
        # ---------------------------------
        if response.status_code == 401:
            raise AuthenticationException("Unauthorized: Invalid or expired token")

        if not (200 <= response.status_code < 300):
            fault_msg = json_data.get("fault", {}).get("faultstring", response.text)
            raise ApiException(fault_msg, response.status_code)

        # ---------------------------------
        # Business-level handling
        # ---------------------------------
        if result_cd is None:
            return json_data  # Some endpoints may not return resultCd

        if result_cd == "000" or result_cd == "001":
            return json_data  # ✅ Success

        # Client errors (891–899)
        if "891" <= result_cd <= "899":
            raise ApiException(f"Client Error ({result_cd}): {result_msg}", 400)

        # Server errors (900+)
        if result_cd >= "900":
            raise ApiException(f"Server Error ({result_cd}): {result_msg}", 500)

        # Fallback business error
        raise ApiException(f"Business Error ({result_cd}): {result_msg}", 400)
