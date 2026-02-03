import os
import sys
from datetime import datetime, timedelta
from pprint import pprint

from kra_etims_sdk.auth import AuthClient
from kra_etims_sdk.client import EtimsClient
from kra_etims_sdk.exceptions import (
    ApiException,
    AuthenticationException,
    ValidationException,
)


# -------------------------------------------------
# HELPERS
# -------------------------------------------------
def header(title: str):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def success(msg: str):
    print(f"✅ {msg}")


def error(msg: str):
    print(f"❌ {msg}")


def warning(msg: str):
    print(f"⚠️  {msg}")


def format_date(days_ago=7) -> str:
    return (datetime.now() - timedelta(days=days_ago)).strftime("%Y%m%d%H%M%S")


# -------------------------------------------------
# CONFIG (MATCHES POSTMAN & PHP)
# -------------------------------------------------
CONFIG = {
    "env": "sbx",

    "cache_file": "/tmp/kra_etims_token.json",

    "auth": {
        "sbx": {
            "token_url": "https://sbx.kra.go.ke/v1/token/generate",
            "consumer_key": os.getenv("KRA_CONSUMER_KEY", "YOUR_SANDBOX_CONSUMER_KEY"),
            "consumer_secret": os.getenv("KRA_CONSUMER_SECRET", "YOUR_SANDBOX_CONSUMER_SECRET"),
        },
        "prod": {
            "token_url": "https://kra.go.ke/v1/token/generate",
            "consumer_key": os.getenv("KRA_PROD_CONSUMER_KEY", ""),
            "consumer_secret": os.getenv("KRA_PROD_CONSUMER_SECRET", ""),
        },
    },

    "api": {
        "sbx": {
            "base_url": "https://sbx.kra.go.ke/etims-oscu/api/v1",
        },
        "prod": {
            "base_url": "https://kra.go.ke/etims-oscu/api/v1",
        },
    },

    "http": {
        "timeout": 30,
    },

    "oscu": {
        "tin": os.getenv("KRA_TIN", "P000000002"),
        "bhf_id": os.getenv("KRA_BHF_ID", "00"),
        "cmc_key": "",
    },

    "endpoints": {
        "initialize": "/initialize",
        "selectCodeList": "/selectCodeList",
        "selectTaxpayerInfo": "/selectTaxpayerInfo",
        "selectNoticeList": "/selectNoticeList",
        "selectCustomerList": "/selectCustomerList",
        "branchInsuranceInfo": "/branchInsuranceInfo",
        "branchUserAccount": "/branchUserAccount",
        "branchSendCustomerInfo": "/branchSendCustomerInfo",
        "sendPurchaseTransactionInfo": "/sendPurchaseTransactionInfo",
        "sendSalesTransaction": "/sendSalesTransaction",
        "insertStockIO": "/insert/stockIO",
        "saveStockMaster": "/save/stockMaster",
    },
}


# -------------------------------------------------
# VALIDATE CONFIG
# -------------------------------------------------
if "YOUR_" in CONFIG["auth"]["sbx"]["consumer_key"]:
    error("Missing KRA sandbox credentials")
    sys.exit(1)


# -------------------------------------------------
# TEST FLOW
# -------------------------------------------------
header("🚀 KRA eTIMS PYTHON SDK TEST")

# STEP 1: AUTH
header("STEP 1: AUTHENTICATION")
try:
    auth = AuthClient(CONFIG)
    auth.forget_token()
    token = auth.token(force=True)
    print(f"Token OK: {token[:30]}...")
    success("Authentication successful")
except AuthenticationException as e:
    error(str(e))
    sys.exit(1)


# STEP 2: INITIALIZATION
header("STEP 2: OSCU INITIALIZATION")
warning("Device serial MUST be pre-registered with KRA")

DEVICE_SERIAL = "dvcv1130"  # 🔴 REPLACE WITH APPROVED SERIAL

try:
    etims = EtimsClient(CONFIG, auth)

    response = etims.initialize({
        "tin": CONFIG["oscu"]["tin"],
        "bhfId": CONFIG["oscu"]["bhf_id"],
        "dvcSrlNo": DEVICE_SERIAL,
    })

    pprint(response)

    cmc_key = response.get("cmcKey") or response.get("data", {}).get("cmcKey")
    if not cmc_key:
        raise RuntimeError("cmcKey missing from initialization response")

    CONFIG["oscu"]["cmc_key"] = cmc_key
    etims = EtimsClient(CONFIG, auth)

    success("Initialization successful")
    print("cmcKey:", cmc_key[:15], "...")
except ApiException as e:
    error(f"Initialization failed: {e}")
    pprint(e.details)
    sys.exit(1)


# STEP 3: CODE LIST
header("STEP 3: FETCH CODE LIST")
try:
    response = etims.select_code_list({
        "tin": CONFIG["oscu"]["tin"],
        "bhfId": CONFIG["oscu"]["bhf_id"],
        "lastReqDt": format_date(),
    })

    count = len(response.get("itemList", []))
    success(f"Retrieved {count} code list items")
except ApiException as e:
    error(str(e))
    sys.exit(1)


# STEP 4: SEND SALES TRANSACTION
header("STEP 4: SEND SALES TRANSACTION")

invoice_no = 1

sales_payload = {
    "invcNo": invoice_no,
    "custTin": "A123456789Z",
    "custNm": "Test Customer",
    "salesTyCd": "N",
    "rcptTyCd": "R",
    "pmtTyCd": "01",
    "salesSttsCd": "01",
    "cfmDt": datetime.now().strftime("%Y%m%d%H%M%S"),
    "salesDt": datetime.now().strftime("%Y%m%d"),
    "totItemCnt": 1,
    "totTaxblAmt": 81000.00,
    "totTaxAmt": 0.00,
    "totAmt": 81000.00,
    "regrId": "Admin",
    "regrNm": "Admin",
    "itemList": [
        {
            "itemSeq": 1,
            "itemCd": "KE2NTBA00000001",
            "itemClsCd": "1000000000",
            "itemNm": "Brand A",
            "qty": 90,
            "prc": 1000,
            "splyAmt": 81000,
            "taxTyCd": "C",
            "taxblAmt": 81000,
            "taxAmt": 0,
            "totAmt": 81000,
        }
    ],
}

try:
    response = etims.send_sales_transaction(sales_payload)
    pprint(response)
    success("Sales transaction sent")
except ValidationException as e:
    error("Validation failed")
    pprint(e.errors)
    sys.exit(1)
except ApiException as e:
    error("API error")
    pprint(e.details)
    sys.exit(1)


header("✅ PYTHON SDK TEST COMPLETED")
