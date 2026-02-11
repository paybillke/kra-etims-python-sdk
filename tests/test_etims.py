import random
import os
import sys
import json
import tempfile
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

# Import your SDK classes (you must implement these separately)
from kra_etims_sdk.oauth import AuthOClient
from kra_etims_sdk.oclient import EtimsOClient
from kra_etims_sdk.exceptions import ApiException, AuthenticationException, ValidationException

# Helper functions
def abort(msg: str) -> None:
    print(f"\n❌ {msg}")
    sys.exit(1)

def header_line(title: str) -> None:
    print(f"\n{'=' * 70}\n{title}\n{'=' * 70}")

def last_req_dt(modifier_days: int = -7) -> str:
    """Returns YYYYMMDDHHMMSS string for N days ago"""
    dt = datetime.now() + timedelta(days=modifier_days)
    return dt.strftime("%Y%m%d%H%M%S")


# ---------------------------- Validate Env ----------------------------
required_envs = ['KRA_CONSUMER_KEY', 'KRA_CONSUMER_SECRET', 'KRA_TIN', 'DEVICE_SERIAL']
for env in required_envs:
    if not os.getenv(env):
        abort(f"Missing environment variable: {env}")

# ---------------------------- Config ----------------------------
config = {
    'env': 'sbx',  # 'prod' for production
    'cache_file': os.path.join(tempfile.gettempdir(), 'kra_etims_token.json'),
    'auth': {
        'sbx': {
            'consumer_key': os.getenv('KRA_CONSUMER_KEY'),
            'consumer_secret': os.getenv('KRA_CONSUMER_SECRET'),
        },
        'prod': {
            'consumer_key': os.getenv('KRA_CONSUMER_KEY'),
            'consumer_secret': os.getenv('KRA_CONSUMER_SECRET'),
        }
    },
    'http': {'timeout': 30},
    'oscu': {
        'tin': os.getenv('KRA_TIN'),
        'bhf_id': os.getenv('KRA_BHF_ID') or '01',
        'device_serial': os.getenv('DEVICE_SERIAL'),
        'cmc_key': os.getenv('CMC_KEY') or '',
    }
}

# ---------------------------- Bootstrap SDK ----------------------------
auth = AuthOClient(config)
etims = EtimsOClient(config, auth)

# ---------------------------- STEP 1: AUTH ----------------------------
header_line('STEP 1: AUTHENTICATION')
try:
    auth.forget_token()
    token = auth.token(force=True)
    print(f"✅ Token OK: {token[:25]}...")
except AuthenticationException as e:
    abort(f"Auth failed: {e}")

# ---------------------------- STEP 2: OSCU INITIALIZATION (Optional) ----------------------------
# Uncomment if needed
# header_line('STEP 2: OSCU INITIALIZATION')
# try:
#     init_data = etims.select_init_osdc_info({
#         'tin': config['oscu']['tin'],
#         'bhfId': config['oscu']['bhf_id'],
#         'dvcSrlNo': config['oscu']['device_serial'],
#     })
#     cmc_key = init_data.get('cmcKey')
#     if not cmc_key:
#         abort(init_data.get('resultMsg', 'Missing cmcKey'))
#     config['oscu']['cmc_key'] = cmc_key
# except ApiException as e:
#     abort(f"OSCU Init failed: {e}")

# ---------------------------- STEP 3: CODE LIST SEARCH ----------------------------
header_line('STEP 3: CODE LIST SEARCH')
try:
    codes = etims.select_code_list({'lastReqDt': last_req_dt()})
    cls_list = codes.get('clsList', [])
    print(f"Code Classes found: {len(cls_list)}")
    for code in cls_list:
        print(f"- Class: {code['cdCls']} ({code['cdClsNm']})")
        for detail in code.get('dtlList', []):
            print(f"    - Detail Code: {detail['cd']} ({detail['cdNm']})")
except ApiException as e:
    print(f"Code List search failed: {e}")

# ---------------------------- STEP 4: CUSTOMER SEARCH ----------------------------
header_line('STEP 4: CUSTOMER SEARCH')
try:
    customers = etims.select_customer({'custmTin': 'A123456789Z'})
    if customers.get('resultCd') == '000':
        cust_list = customers.get('data', {}).get('custList', [])
        print(f"Customers found: {len(cust_list)}")
        for cust in cust_list:
            print(f"- TIN: {cust['tin']}")
            print(f"  Name: {cust['taxprNm']}")
            print(f"  Status: {cust['taxprSttsCd']}")
            print(f"  County: {cust['prvncNm']}")
            print(f"  Sub-County: {cust['dstrtNm']}")
            print(f"  Tax Locality: {cust['sctrNm']}")
            print(f"  Location Desc: {cust['locDesc']}\n")
    else:
        print(f"Result Message: {customers.get('resultMsg')}")
except ApiException as e:
    print(f"Customer search failed: {e}")

# ---------------------------- STEP 5: NOTICE SEARCH ----------------------------
header_line('STEP 5: NOTICE SEARCH')
try:
    notices = etims.select_notice_list({'lastReqDt': last_req_dt(-30)})
    if notices.get('resultCd') == '000':
        notice_list = notices.get('data', {}).get('noticeList', [])
        print(f"Notices found: {len(notice_list)}")
        for notice in notice_list:
            print(f"- Notice No: {notice['noticeNo']}")
            print(f"  Title: {notice['title']}")
            print(f"  Contents: {notice['cont']}")
            print(f"  Detail URL: {notice['dtlUrl']}")
            print(f"  Registered by: {notice['regrNm']}")
            print(f"  Registration Date: {notice['regDt']}\n")
    else:
        print(f"Result Message: {notices.get('resultMsg')}")
except ApiException as e:
    print(f"Notice search failed: {e}")

# ---------------------------- STEP 6: ITEM CLASS SEARCH ----------------------------
header_line('STEP 6: ITEM CLASS SEARCH')
try:
    item_classes = etims.select_item_classes({'lastReqDt': last_req_dt(-30)})
    if item_classes.get('resultCd') == '000':
        item_cls_list = item_classes.get('data', {}).get('itemClsList', [])
        print(f"Item Classes found: {len(item_cls_list)}")
        for item in item_cls_list:
            print(f"- Item Class Code: {item['itemClsCd']}")
            print(f"  Name: {item['itemClsNm']}")
            print(f"  Level: {item['itemClsLvl']}")
            print(f"  Tax Type Code: {item['taxTyCd']}")
            print(f"  Major Target: {item['mjrTgYn']}")
            print(f"  Use Status: {item['useYn']}\n")
    else:
        print(f"Result Message: {item_classes.get('resultMsg')}")
except ApiException as e:
    print(f"Item Class search failed: {e}")

# ---------------------------- STEP 7: SAVE ITEM ----------------------------
header_line('STEP 7: SAVE ITEM')
try:
    item_data = {
        'itemCd': 'KE1NTXU0000006',
        'itemClsCd': '5059690800',
        'itemTyCd': '1',
        'itemNm': 'test material item3',
        'itemStdNm': None,
        'orgnNatCd': 'KE',
        'pkgUnitCd': 'NT',
        'qtyUnitCd': 'U',
        'taxTyCd': 'B',
        'btchNo': None,
        'bcd': None,
        'dftPrc': 3500,
        'grpPrcL1': 3500,
        'grpPrcL2': 3500,
        'grpPrcL3': 3500,
        'grpPrcL4': 3500,
        'grpPrcL5': None,
        'addInfo': None,
        'sftyQty': None,
        'isrcAplcbYn': 'N',
        'useYn': 'Y',
        'regrId': 'Test',
        'regrNm': 'Test',
        'modrId': 'Test',
        'modrNm': 'Test',
    }
    response = etims.save_item(item_data)
    print("Item Save Response:")
    print(f"Result Code: {response.get('resultCd')}")
    print(f"Result Message: {response.get('resultMsg')}")
    print(f"Result Date: {response.get('resultDt')}")
except ApiException as e:
    print(f"Save Item failed: {e}")

# ---------------------------- STEP 8: ITEM SEARCH ----------------------------
header_line('STEP 8: ITEM SEARCH')
try:
    items = etims.select_items({'lastReqDt': last_req_dt(-30)})
    item_list = items.get('data', {}).get('itemList', [])
    print(f"Items found: {len(item_list)}")
    for item in item_list:
        print(f"- Item Code: {item['itemCd']}")
        print(f"  Name: {item['itemNm']}")
        print(f"  Classification Code: {item['itemClsCd']}")
        print(f"  Type Code: {item['itemTyCd']}")
        print(f"  Standard Name: {item['itemStdNm']}")
        print(f"  Origin: {item['orgnNatCd']}")
        print(f"  Packaging Unit: {item['pkgUnitCd']}")
        print(f"  Quantity Unit: {item['qtyUnitCd']}")
        print(f"  Tax Type: {item['taxTyCd']}")
        print(f"  Batch No: {item['btchNo']}")
        print(f"  Registered Branch: {item['regBhfId']}")
        print(f"  Barcode: {item['bcd']}")
        print(f"  Default Price: {item['dftPrc']}")
        print(f"  Group Prices: L1={item['grpPrcL1']}, L2={item['grpPrcL2']}, L3={item['grpPrcL3']}, L4={item['grpPrcL4']}, L5={item['grpPrcL5']}")
        print(f"  Additional Info: {item['addInfo']}")
        print(f"  Safety Quantity: {item['sftyQty']}")
        print(f"  Insurance Applicable: {item['isrcAplcbYn']}")
        print(f"  KRA Modify Flag: {item['rraModYn']}")
        print(f"  Use Status: {item['useYn']}\n")
except ApiException as e:
    print(f"Item search failed: {e}")

# ---------------------------- STEP 9: BRANCH SEARCH ----------------------------
header_line('STEP 9: BRANCH SEARCH')
try:
    branches = etims.select_branches({'lastReqDt': last_req_dt(-30)})
    bhf_list = branches.get('data', {}).get('bhfList', [])
    print(f"Branches found: {len(bhf_list)}")
    for branch in bhf_list:
        print(f"- Branch ID: {branch['bhfId']}")
        print(f"  Name: {branch['bhfNm']}")
        print(f"  Status Code: {branch['bhfSttsCd']}")
        print(f"  County: {branch['prvncNm']}")
        print(f"  Sub-County: {branch['dstrtNm']}")
        print(f"  Locality: {branch['sctrNm']}")
        print(f"  Location: {branch['locDesc']}")
        print(f"  Manager Name: {branch['mgrNm']}")
        print(f"  Manager Phone: {branch['mgrTelNo']}")
        print(f"  Manager Email: {branch['mgrEmail']}")
        print(f"  Head Office: {branch['hqYn']}\n")
except ApiException as e:
    print(f"Branch search failed: {e}")

# ---------------------------- STEP 10: SAVE BRANCH CUSTOMER ----------------------------
header_line('STEP 10: SAVE BRANCH CUSTOMER')
try:
    customer_data = {
        'custNo': '999991113',
        'custTin': 'A123456789Z',
        'custNm': 'Taxpayer1113',
        'adrs': None,
        'telNo': None,
        'email': None,
        'faxNo': None,
        'useYn': 'Y',
        'remark': None,
        'regrId': 'Test',
        'regrNm': 'Test',
        'modrId': 'Test',
        'modrNm': 'Test',
    }
    response = etims.save_branch_customer(customer_data)
    if response.get('resultCd') == '000':
        print("✅ Branch customer saved successfully")
    else:
        abort(f"Failed to save branch customer: {response.get('resultMsg', 'Unknown error')}")
except ApiException as e:
    print(f"Branch customer save failed: {e}")

# ---------------------------- STEP 11: SAVE BRANCH USER ----------------------------
header_line('STEP 11: SAVE BRANCH USER')
try:
    user_data = {
        'tin': config['oscu']['tin'],
        'bhfId': config['oscu']['bhf_id'],
        'cmcKey': config['oscu']['cmc_key'],
        'userId': 'userId3',
        'userNm': 'User Name3',
        'pwd': '12341234',
        'adrs': None,
        'cntc': None,
        'authCd': None,
        'remark': None,
        'useYn': 'Y',
        'regrId': 'Test',
        'regrNm': 'Test',
        'modrId': 'Test',
        'modrNm': 'Test',
    }
    response = etims.save_branch_user(user_data)
    if response.get('resultCd') == '000':
        print("✅ Branch user saved successfully")
    else:
        abort(f"Failed to save branch user: {response.get('resultMsg', 'Unknown error')}")
except ApiException as e:
    print(f"Branch user save failed: {e}")

# ---------------------------- STEP 12: SAVE BRANCH INSURANCE ----------------------------
header_line('STEP 12: SAVE BRANCH INSURANCE')
try:
    insurance_data = {
        'tin': config['oscu']['tin'],
        'bhfId': config['oscu']['bhf_id'],
        'cmcKey': config['oscu']['cmc_key'],
        'isrccCd': 'ISRCC01',
        'isrccNm': 'ISRCC NAME',
        'isrcRt': 20,
        'useYn': 'Y',
        'regrId': 'Test',
        'regrNm': 'Test',
        'modrId': 'Test',
        'modrNm': 'Test',
    }
    response = etims.save_branch_insurance(insurance_data)
    if response.get('resultCd') == '000':
        print("✅ Branch insurance saved successfully")
    else:
        abort(f"Failed to save branch insurance: {response.get('resultMsg', 'Unknown error')}")
except ApiException as e:
    print(f"Branch insurance save failed: {e}")

# ---------------------------- STEP 14: IMPORT ITEM UPDATE ----------------------------
header_line('STEP 14: IMPORT ITEM UPDATE')
try:
    import_data = {
        'taskCd': '2231943',
        'dclDe': '20191217',
        'itemSeq': 1,
        'hsCd': '1231531231',
        'itemClsCd': '5022110801',
        'itemCd': 'KE1NTXU0000001',
        'imptItemSttsCd': '1',
        'remark': 'Updated remark',
        'modrId': 'Test',
        'modrNm': 'Test',
    }
    response = etims.update_imported_item(import_data)
    if response.get('resultCd') == '000':
        print("✅ Import item updated successfully")
    else:
        abort(f"Failed to update import item: {response.get('resultMsg', 'Unknown error')}")
except ApiException as e:
    print(f"Import item update failed: {e}")

# ---------------------------- STEP 16: PURCHASE TRANSACTION SAVE ----------------------------
header_line('STEP 16: PURCHASE TRANSACTION SAVE')
try:
    purchase_data = {
        'invcNo': 1,
        'orgInvcNo': 0,
        'spplrTin': 'A123456789Z',
        'spplrBhfId': None,
        'spplrNm': None,
        'spplrInvcNo': None,
        'regTyCd': 'M',
        'pchsTyCd': 'N',
        'rcptTyCd': 'P',
        'pmtTyCd': '01',
        'pchsSttsCd': '02',
        'cfmDt': '20200127210300',
        'pchsDt': '20200127',
        'wrhsDt': None,
        'cnclReqDt': None,
        'cnclDt': None,
        'rfdDt': None,
        'totItemCnt': 2,
        'taxblAmtA': 0,
        'taxblAmtB': 10500,
        'taxblAmtC': 0,
        'taxblAmtD': 0,
        'taxblAmtE': 0,
        'taxRtA': 0,
        'taxRtB': 18,
        'taxRtC': 0,
        'taxRtD': 0,
        'taxRtE': 0,
        'taxAmtA': 0,
        'taxAmtB': 1890,
        'taxAmtC': 0,
        'taxAmtD': 0,
        'taxAmtE': 0,
        'totTaxblAmt': 10500,
        'totTaxAmt': 1890,
        'totAmt': 10500,
        'remark': None,
        'regrId': 'Test',
        'regrNm': 'Test',
        'modrId': 'Test',
        'modrNm': 'Test',
        'itemList': [
            {
                'itemSeq': 1,
                'itemCd': 'KE1NTXU0000001',
                'itemClsCd': '5059690800',
                'itemNm': 'test item 1',
                'bcd': None,
                'spplrItemClsCd': None,
                'spplrItemCd': None,
                'spplrItemNm': None,
                'pkgUnitCd': 'NT',
                'pkg': 2,
                'qtyUnitCd': 'U',
                'qty': 2,
                'prc': 3500,
                'splyAmt': 7000,
                'dcRt': 0,
                'dcAmt': 0,
                'taxblAmt': 7000,
                'taxTyCd': 'B',
                'taxAmt': 1260,
                'totAmt': 7000,
                'itemExprDt': None,
            },
            {
                'itemSeq': 2,
                'itemCd': 'KE1NTXU0000002',
                'itemClsCd': '5022110801',
                'itemNm': 'test item 2',
                'bcd': None,
                'spplrItemClsCd': None,
                'spplrItemCd': None,
                'spplrItemNm': None,
                'pkgUnitCd': 'NT',
                'pkg': 1,
                'qtyUnitCd': 'U',
                'qty': 1,
                'prc': 3500,
                'splyAmt': 3500,
                'dcRt': 0,
                'dcAmt': 0,
                'taxblAmt': 3500,
                'taxTyCd': 'B',
                'taxAmt': 630,
                'totAmt': 3500,
                'itemExprDt': None,
            }
        ]
    }
    response = etims.save_purchase(purchase_data)
    if response.get('resultCd') == '000':
        print("✅ Purchase transaction saved successfully")
    else:
        abort(f"Failed to save purchase transaction: {response.get('resultMsg', 'Unknown error')}")
except ApiException as e:
    print(f"Purchase transaction save failed: {e}")
except ValidationException as e:
    print("❌ Validation failed:")
    for field, msg in e.details.items():
        print(f"- Field '{field}': {msg}")

# ---------------------------- STEP 18: STOCK IN/OUT SAVE ----------------------------
header_line('STEP 18: STOCK IN/OUT SAVE')
try:
    stock_io_data = {
        'tin': 'A123456789Z',
        'bhfId': '00',
        'sarNo': 2,
        'orgSarNo': 2,
        'regTyCd': 'M',
        'custTin': 'A123456789Z',
        'custNm': None,
        'custBhfId': None,
        'sarTyCd': '11',
        'ocrnDt': '20260106',
        'totItemCnt': 2,
        'totTaxblAmt': 70000,
        'totTaxAmt': 10677.96,
        'totAmt': 70000,
        'remark': None,
        'regrId': 'Test',
        'regrNm': 'Test',
        'modrId': 'Test',
        'modrNm': 'Test',
        'itemList': [
            {
                'itemSeq': 1,
                'itemCd': 'KE1NTXU0000001',
                'itemClsCd': '5059690800',
                'itemNm': 'test item1',
                'bcd': None,
                'pkgUnitCd': 'NT',
                'pkg': 10,
                'qtyUnitCd': 'U',
                'qty': 10,
                'itemExprDt': None,
                'prc': 3500,
                'splyAmt': 35000,
                'totDcAmt': 0,
                'taxblAmt': 35000,
                'taxTyCd': 'B',
                'taxAmt': 5338.98,
                'totAmt': 35000,
            },
            {
                'itemSeq': 2,
                'itemCd': 'KE1NTXU0000002',
                'itemClsCd': '5059690800',
                'itemNm': 'test item2',
                'bcd': None,
                'pkgUnitCd': 'BL',
                'pkg': 10,
                'qtyUnitCd': 'U',
                'qty': 10,
                'itemExprDt': None,
                'prc': 3500,
                'splyAmt': 35000,
                'totDcAmt': 0,
                'taxblAmt': 35000,
                'taxTyCd': 'B',
                'taxAmt': 5338.98,
                'totAmt': 35000,
            }
        ]
    }
    response = etims.save_stock_io(stock_io_data)
    if response.get('resultCd') == '000':
        print("✅ Stock In/Out saved successfully")
    else:
        abort(f"Failed to save Stock In/Out: {response.get('resultMsg', 'Unknown error')}")
except ApiException as e:
    print(f"Stock In/Out request failed: {e}")
except ValidationException as e:
    print("❌ Validation failed:")
    for field, msg in e.details.items():
        print(f"- Field '{field}': {msg}")

# ---------------------------- STEP 19: SAVE STOCK MASTER ----------------------------
header_line('STEP 19: SAVE STOCK MASTER')
try:
    stock_master_data = {
        'tin': 'A123456789Z',
        'bhfId': '00',
        'itemCd': 'KE1NTXU0000002',
        'rsdQty': 10,
        'regrId': 'Test',
        'regrNm': 'Test',
        'modrId': 'Test',
        'modrNm': 'Test',
    }
    response = etims.save_stock_master(stock_master_data)
    if response.get('resultCd') == '000':
        print("✅ Stock Master saved successfully")
    else:
        abort(f"Failed to save Stock Master: {response.get('resultMsg', 'Unknown error')}")
except ApiException as e:
    print(f"Stock Master save failed: {e}")
except ValidationException as e:
    print("❌ Validation failed:")
    for field, msg in e.details.items():
        print(f"- Field '{field}': {msg}")

print("\n🎉 All steps completed successfully!")

# ---------------------------- STEP 20: SAVE SALES TRANSACTION ----------------------------
header_line('STEP 20: SAVE SALES TRANSACTION')
try:
    # Prepare sales transaction data matching specification
    sales_data = {
        "tin": "A123456789Z",
        "bhfId": "00",
        "cmcKey": "COMM_KEY_20260208123456",
        "trdInvcNo": "TRD_INV_20260208_001",
        "invcNo": str(random.randint(1, 1000)),
        "orgInvcNo": "0",
        "custTin": "A123456789Z",
        "custNm": "Test Customer",
        "rcptTyCd": "S",  # Sale receipt type
        "pmtTyCd": "01",  # Cash payment
        "salesSttsCd": "02",  # Completed
        "cfmDt": "20260208143000",  # yyyyMMddHHmmss
        "salesDt": "20260208",  # yyyyMMdd
        "stockRlsDt": "20260208143000",
        "cnclReqDt": None,
        "cnclDt": None,
        "rfdDt": None,
        "rfdRsnCd": None,
        "totItemCnt": 2,
        "taxblAmtA": 0.00,
        "taxblAmtB": 10500.00,
        "taxblAmtC": 0.00,
        "taxblAmtD": 0.00,
        "taxblAmtE": 0.00,
        "taxRtA": 0.00,
        "taxRtB": 18.00,
        "taxRtC": 0.00,
        "taxRtD": 0.00,
        "taxRtE": 0.00,
        "taxAmtA": 0.00,
        "taxAmtB": 1602.00,
        "taxAmtC": 0.00,
        "taxAmtD": 0.00,
        "taxAmtE": 0.00,
        "totTaxblAmt": 10500.00,
        "totTaxAmt": 1602.00,
        "totAmt": 12102.00,
        "prchrAcptcYn": "N",
        "remark": "Test sale transaction",
        "regrId": "Test",
        "regrNm": "Test User",
        "modrId": "Test",
        "modrNm": "Test User",
        "receipt": {
            "custTin": "A123456789Z",
            "custMblNo": "254712345678",
            "rcptPbctDt": "20260208143000",
            "trdeNm": "Test Store",
            "adrs": "123 Main Street, Nairobi",
            "topMsg": "Thank You!",
            "btmMsg": "Visit Again",
            "prchrAcptcYn": "N"
        },
        "itemList": [
            {
                "itemSeq": 1,
                "itemClsCd": "5059690800",
                "itemCd": "KE1NTXU0000001",
                "itemNm": "Test Item 1",
                "bcd": "1234567890123",
                "pkgUnitCd": "NT",
                "pkg": 2.00,
                "qtyUnitCd": "U",
                "qty": 2.00,
                "prc": 3500.00,
                "splyAmt": 7000.00,
                "dcRt": 0.00,
                "dcAmt": 0.00,
                "isrccCd": None,
                "isrccNm": None,
                "isrcRt": None,
                "isrcAmt": None,
                "taxTyCd": "B",
                "taxblAmt": 7000.00,
                "taxAmt": 1068.00,
                "totAmt": 8068.00
            },
            {
                "itemSeq": 2,
                "itemClsCd": "5022110801",
                "itemCd": "KE1NTXU0000002",
                "itemNm": "Test Item 2",
                "bcd": "9876543210987",
                "pkgUnitCd": "NT",
                "pkg": 1.00,
                "qtyUnitCd": "U",
                "qty": 1.00,
                "prc": 3500.00,
                "splyAmt": 3500.00,
                "dcRt": 0.00,
                "dcAmt": 0.00,
                "isrccCd": None,
                "isrccNm": None,
                "isrcRt": None,
                "isrcAmt": None,
                "taxTyCd": "B",
                "taxblAmt": 3500.00,
                "taxAmt": 534.00,
                "totAmt": 4034.00
            }
        ]
    }
    
    # Attempt to save sales transaction
    response = etims.save_sales_transaction(sales_data)
    
    # Validate response
    if response.get('resultCd') == '000':
        print("✅ Sales transaction saved successfully")
        print(f"   Receipt Number: {response.get('data', {}).get('curRcptNo', 'N/A')}")
        print(f"   Total Receipts: {response.get('data', {}).get('totRcptNo', 'N/A')}")
        print(f"   SDC DateTime: {response.get('data', {}).get('sdcDateTime', 'N/A')}")
        print(f"   Receipt Signature: {response.get('data', {}).get('rcptSign', 'N/A')}")
    else:
        abort(f"Failed to save sales transaction: {response.get('resultMsg', 'Unknown error')}")
        
except ApiException as e:
    print(f"❌ Sales transaction save failed (API Error): {e}")
    print(f"   Error Code: {e.code}")
    print(f"   Error Message: {e.message}")
except ValidationException as e:
    print(f"❌ Validation failed: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {type(e).__name__}: {str(e)}")

print("\n" + "="*60)
print("🎉 All steps completed successfully!")
print("="*60)