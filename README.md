<p align="center">
  <a href="https://paybill.ke" target="_blank">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://paybill.ke/logo-wordmark--dark.png">
      <img src="https://paybill.ke/logo-wordmark--light.png" width="180" alt="Paybill Kenya Logo">
    </picture>
  </a>
</p>

# KRA eTIMS OSCU Integration SDK (Python)

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)
![Pydantic](https://img.shields.io/badge/Pydantic-v2-3a56c5?logo=pydantic)
![License](https://img.shields.io/badge/License-MIT-green)
![KRA eTIMS](https://img.shields.io/badge/KRA-eTIMS_OSCU-0066CC)
![Postman Compliant](https://img.shields.io/badge/Postman-Compliant-FF6C37?logo=postman)
![Pytest Tested](https://img.shields.io/badge/Tests-Pytest-3776AB?logo=pytest)

A production-ready **Python SDK** for integrating with the Kenya Revenue Authority (KRA) **eTIMS OSCU** (Online Sales Control Unit) API. Built to match the official Postman collection specifications with strict header compliance, token management, and comprehensive Pydantic validation.

> ⚠️ **Critical Note**: This SDK implements the **new OSCU specification** (KRA-hosted), *not* the VSCU eTIMS API. OSCU requires device registration, headers, and `cmcKey` lifecycle management.

## Author
**Bartile Emmanuel**  
📧 ebartile@gmail.com | 📱 +254757807150  
*Lead Developer, Paybill Kenya*

---

## Table of Contents
- [Introduction to eTIMS OSCU](#introduction-to-etims-oscu)
- [OSCU Integration Journey](#oscu-integration-journey)
- [Critical Requirements](#critical-requirements)
- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage Guide](#usage-guide)
- [API Reference](#api-reference)
- [Field Validation Rules](#field-validation-rules)
- [Error Handling](#error-handling)
- [Troubleshooting](#troubleshooting)
- [Automated Testing Requirements](#automated-testing-requirements)
- [KYC Documentation Checklist](#kyc-documentation-checklist)
- [Go-Live Process](#go-live-process)
- [Support](#support)
- [License](#license)
- [Attribution](#attribution)

---

## Introduction to eTIMS OSCU

KRA's **Electronic Tax Invoice Management System (eTIMS)** uses **OSCU** (Online Sales Control Unit) – a KRA-hosted software module that validates and signs tax invoices in real-time before issuance. Unlike VSCU, OSCU requires:

- Pre-registered device serial numbers (`dvcSrlNo`)
- Communication key (`cmcKey`) lifecycle management
- Strict payload schema compliance per KRA specifications

### OSCU vs VSCU eTIMS

| Feature | OSCU (This SDK) | VSCU eTIMS |
|---------|-----------------|--------------|
| **Hosting** | KRA-hosted (cloud) | Self-hosted (on-premise) |
| **Device Registration** | Mandatory pre-registration | Not required |
| **Authentication** | Bearer token | Basic auth only |
| **Communication Key** | `cmcKey` required after init | Not applicable |
| **API Base URL** | `sbx.kra.go.ke/etims-oscu/api/v1` | `etims-api-sbx.kra.go.ke` |
| **Header Requirements** | Strict 6-header compliance | Minimal headers |

### Receipt Types & Labels Matrix

Each receipt is formed from a combination of receipt type and transaction type:

| RECEIPT TYPE | TRANSACTION TYPE | RECEIPT LABEL | DESCRIPTION |
|--------------|------------------|---------------|-------------|
| NORMAL       | SALES            | NS            | Standard tax invoice for customers |
| NORMAL       | CREDIT NOTE      | NC            | Refund/return invoice |
| COPY         | SALES            | CS            | Reprint with "Copy" watermark |
| COPY         | CREDIT NOTE      | CC            | Reprint of credit note |
| TRAINING     | SALES            | TS            | Training mode (no tax impact) |
| TRAINING     | CREDIT NOTE      | TC            | Training credit note |
| PROFORMA     | SALES            | PS            | Quote/proforma invoice |

### Tax Category Codes

KRA requires tax breakdown across 5 categories in all sales/purchase transactions:

| Code | Description | Standard Rate | Notes |
|------|-------------|---------------|-------|
| **A** | VAT Standard | 16% | Most goods/services |
| **B** | VAT Special | 8% / 14% | Petroleum products, etc. |
| **C** | Zero-rated | 0% | Exports, humanitarian aid |
| **D** | Exempt | 0% | Financial services, education |
| **E** | Non-taxable | 0% | Insurance, residential rent |

> 💡 **Critical**: All 15 tax fields required in payloads:  
> `taxblAmtA/B/C/D/E`, `taxRtA/B/C/D/E`, `taxAmtA/B/C/D/E`

---

## OSCU Integration Journey

KRA mandates a strict 6-phase integration process before production deployment:

```mermaid
flowchart TD
    A[1. Sign Up & Device Registration] --> B[2. Discovery & Simulation]
    B --> C[3. Automated App Testing]
    C --> D[4. KYC Documentation]
    D --> E[5. Verification Meeting]
    E --> F[6. Go-Live Deployment]
```

### Phase 1: Sign Up & Device Registration
1. Register on [eTIMS Taxpayer Sandbox Portal](https://etims-sbx.kra.go.ke)
2. Submit Service Request → Select "eTIMS" → Choose "OSCU" type
3. Await SMS confirmation of OSCU approval
4. **Critical**: Device serial number (`dvcSrlNo`) is provisioned during this phase

### Phase 2: Discovery & Simulation
- Create application on [GavaConnect Developer Portal](https://developer.go.ke)
- Obtain sandbox credentials:
  - Consumer Key/Secret (for token generation)
  - Approved device serial number (`dvcSrlNo`)

### Phase 3: Automated App Testing
- Run integration tests against sandbox environment
- **Critical**: Upload test artifacts within **1 hour** of test completion:
  - Item creation screenshot
  - Invoice generation screenshot
  - Sample invoice copy (PDF/print)
  - Credit note copy (PDF/print)

### Phase 4: KYC Documentation
**Third-Party Integrators Must Submit**:
- [ ] eTIMS Bio Data Form (completed)
- [ ] Certificate of Incorporation / Business Registration + CR12
- [ ] Valid Business Permit
- [ ] National IDs of directors/partners/sole proprietor
- [ ] Company Tax Compliance Certificate (valid)
- [ ] Proof of 3+ qualified technical staff (CVs + certifications)
- [ ] Notarized solvency declaration
- [ ] Technology Architecture document (TIS ↔ eTIMS integration diagram)

**Self-Integrators Only Need**:
- [ ] Items 1, 5, 6, and 8 from above list

### Phase 5: Verification Meeting
- Schedule demo via Developer Portal
- Demonstrate:
  - Invoice data database structure
  - Credit note database structure
  - Complete invoice format (with OSCU signatures)
  - Item creation workflow
  - Stock management integration
- Address KRA feedback within 48 hours if failed

### Phase 6: Go-Live Deployment
- Execute SLA with KRA (third-party integrators only)
- Receive production keys via Developer Portal
- Deploy to production environment
- Monitor compliance for first 30 days

---

## Critical Requirements

Before integration, you **MUST** complete these prerequisites:

### 1. Device Registration (MANDATORY)
- Register OSCU device via [eTIMS Taxpayer Sandbox Portal](https://sbx.kra.go.ke)
- Obtain **approved device serial number** (`dvcSrlNo`)
- ⚠️ **Dynamic/unregistered device serials fail with `resultCd: 901`** ("It is not valid device")

### 2. Communication Key Lifecycle
```python
# 1. Initialize FIRST (returns cmcKey)
response = etims.select_init_osdc_info({
    "tin": config.oscu["tin"],
    "bhfId": config.oscu["bhf_id"],
    "dvcSrlNo": "dvcv1130",  # KRA-approved serial
})

# 2. Extract cmcKey (sandbox returns at root level)
cmc_key = response.get("cmcKey") or response.get("data", {}).get("cmcKey")

# 3. Update config IMMEDIATELY
config.oscu["cmc_key"] = cmc_key

# 4. Recreate client with updated config (critical!)
etims = EtimsClient(config, auth)

# 5. ALL subsequent requests require cmcKey in headers
etims.select_code_list(...)
```

### 3. Invoice Numbering Rules
- **MUST be sequential integers** (1, 2, 3...) – **NOT strings** (`INV001`)
- Must be unique per branch office (`bhfId`)
- Cannot be reused even after cancellation
- KRA rejects non-integer invoice numbers with `resultCd: 500`

### 4. Date Format Specifications
| Field | Format | Example | Validation Rule |
|-------|--------|---------|-----------------|
| `salesDt`, `pchsDt`, `ocrnDt` | `YYYYMMDD` | `20260131` | Cannot be future date |
| `cfmDt`, `stockRlsDt`, `rcptPbctDt` | `YYYYMMDDHHmmss` | `20260131143022` | Must be current/past |
| `lastReqDt` | `YYYYMMDDHHmmss` | `20260130143022` | Cannot be future date; max 7 days old |

---

## Features

✅ **Postman Collection Compliance**  
- 100% header, path, and payload alignment with official KRA Postman collection  
- Correct nested paths (`/insert/stockIO`, `/save/stockMaster`)  
- All 8 functional categories implemented  

✅ **Strict Header Management**  
| Endpoint Type | Required Headers | Initialization Exception |
|---------------|------------------|--------------------------|
| **Initialization** | `Authorization` | ❌ NO `tin`/`bhfId`/`cmcKey` |
| **All Other Endpoints** | `Authorization`, `tin`, `bhfId`, `cmcKey` | ✅ Full header set |

✅ **Token Lifecycle Management**  
- Automatic token caching with 60-second buffer  
- Transparent token refresh on 401 errors  
- File-based cache with configurable location  

✅ **Comprehensive Validation**  
- Pydantic v2 schemas matching KRA specifications  
- Field-level validation with human-readable errors  
- Date format enforcement (`YYYYMMDDHHmmss`)  
- Tax category validation (A/B/C/D/E)  

✅ **Production Ready**  
- SSL verification enabled by default  
- Timeout configuration (default: 30s)  
- Environment-aware (sandbox/production)  
- Detailed error diagnostics with KRA fault strings  

---

## Installation

```bash
pip install kra-etims-sdk
# OR with dev dependencies
pip install "kra-etims-sdk[dev]"
```

### Requirements
- Python 3.9+
- `requests` (≥2.31)
- `pydantic` (≥2.0)
- `typing-extensions` (for Python <3.10)

---

## Configuration

```python
from kra_etims_sdk import KraEtimsConfig
import os

config = KraEtimsConfig(
    env="sandbox",  # "sandbox" | "production"
    cache_file="./.kra_token.json",
    
    auth={
        "sandbox": {
            "token_url": "https://sbx.kra.go.ke/v1/token/generate".strip(),
            "consumer_key": os.environ["KRA_CONSUMER_KEY"],
            "consumer_secret": os.environ["KRA_CONSUMER_SECRET"],
        },
        "production": {
            "token_url": "https://kra.go.ke/v1/token/generate".strip(),
            "consumer_key": os.environ["KRA_PROD_CONSUMER_KEY"],
            "consumer_secret": os.environ["KRA_PROD_CONSUMER_SECRET"],
        }
    },
    
    api={
        "sandbox": {"base_url": "https://sbx.kra.go.ke/etims-oscu/api/v1".strip()},
        "production": {"base_url": "https://api.developer.go.ke/etims-oscu/api/v1".strip()}
    },
    
    oscu={
        "tin": os.environ["KRA_TIN"],
        "bhf_id": os.environ["KRA_BHF_ID"],
        "cmc_key": "",  # Set AFTER initialization
    },
    
    endpoints={
        # INITIALIZATION (ONLY endpoint without tin/bhfId/cmcKey headers)
        "selectInitOsdcInfo": "/selectInitOsdcInfo",
        
        # DATA MANAGEMENT
        "selectCodeList": "/selectCodeList",
        "selectItemClsList": "/selectItemClass",
        "selectBhfList": "/branchList",
        "selectTaxpayerInfo": "/selectTaxpayerInfo",
        "selectCustomerList": "/selectCustomerList",
        "selectNoticeList": "/selectNoticeList",
        
        # BRANCH MANAGEMENT
        "branchInsuranceInfo": "/branchInsuranceInfo",
        "branchUserAccount": "/branchUserAccount",
        "branchSendCustomerInfo": "/branchSendCustomerInfo",
        
        # ITEM MANAGEMENT
        "saveItem": "/saveItem",
        "itemInfo": "/itemInfo",
        
        # PURCHASE MANAGEMENT
        "selectPurchaseTrns": "/getPurchaseTransactionInfo",
        "sendPurchaseTransactionInfo": "/sendPurchaseTransactionInfo",
        
        # SALES MANAGEMENT
        "sendSalesTransaction": "/sendSalesTransaction",
        "selectSalesTrns": "/selectSalesTransactions",
        "selectInvoiceDetail": "/selectInvoiceDetail",
        
        # STOCK MANAGEMENT (NESTED PATHS - CRITICAL)
        "insertStockIO": "/insert/stockIO",    # ← slash in path
        "saveStockMaster": "/save/stockMaster",  # ← slash in path
        "selectMoveList": "/selectStockMoveLists",
    },
    
    http={"timeout": 30}
)
```

> 💡 **Production URL Note**:  
> Production base URL is `https://api.developer.go.ke/etims-oscu/api/v1` (NOT `kra.go.ke`)

---

## Usage Guide

### Step 1: Initialize SDK
```python
from kra_etims_sdk import AuthClient, EtimsClient
from kra_etims_sdk.exceptions import ApiException, ValidationException

auth = AuthClient(config)
etims = EtimsClient(config, auth)
```

### Step 2: Authenticate (Get Access Token)
```python
try:
    # Force fresh token (optional - cache used by default)
    token = auth.token(force_refresh=True)
    print(f"✅ Token acquired: {token[:20]}...")
except AuthenticationException as e:
    print(f"❌ Authentication failed: {e}")
    exit(1)
```

### Step 3: OSCU Initialization (Critical Step)
```python
try:
    # ⚠️ MUST use KRA-approved device serial (NOT dynamic!)
    # Common sandbox test value (if pre-provisioned by KRA):
    
    response = etims.select_init_info({
        "tin": config.oscu["tin"],
        "bhfId": config.oscu["bhf_id"],
        "dvcSrlNo": config.oscu["device_serial"],
    })

    # Extract cmcKey (sandbox returns at root level)
    cmc_key = response.get("cmcKey") or response.get("data", {}).get("cmcKey")
    if not cmc_key:
        raise RuntimeError("cmcKey not found in response")

    # Update config IMMEDIATELY
    config.oscu["cmc_key"] = cmc_key
    
    # Recreate client with updated config (critical!)
    etims = EtimsClient(config, auth)
    
    print(f"✅ OSCU initialized. cmcKey: {cmc_key[:15]}...")

except ApiException as e:
    if e.error_code == "901":
        print("❌ DEVICE NOT VALID (resultCd 901)")
        print("   → Device serial not registered with KRA")
        print("   → Contact timsupport@kra.go.ke for approved serial")
        print("   → Common sandbox test value: 'dvcv1130' (may work if pre-provisioned)")
        exit(1)
    raise
```

### Step 4: Business Operations (Postman-Compliant Payload)
```python
from datetime import datetime, timedelta

def kra_date(days_offset=0):
    """Generate KRA-compliant date strings"""
    d = datetime.now() + timedelta(days=days_offset)
    return d.strftime("%Y%m%d%H%M%S")  # YYYYMMDDHHmmss

# Fetch code list (demonstrates header injection)
try:
    codes = etims.select_code_list({
        "tin": config.oscu["tin"],
        "bhfId": config.oscu["bhf_id"],
        "lastReqDt": kra_date(-7),  # NOT future date
    })
    print(f"✅ Retrieved {len(codes.get('itemList', []))} codes")
except Exception as e:
    print(f"❌ Code list fetch failed: {e}")

# Send sales transaction (FULL Postman payload structure)
try:
    response = etims.send_sales_transaction({
        "invcNo": 1,  # INTEGER (sequential) - NOT string!
        "custTin": "A123456789Z",
        "custNm": "Test Customer",
        "salesTyCd": "N",  # N=Normal, R=Return
        "rcptTyCd": "R",   # R=Receipt
        "pmtTyCd": "01",   # 01=Cash
        "salesSttsCd": "01",  # 01=Completed
        "cfmDt": kra_date(),     # YYYYMMDDHHmmss
        "salesDt": kra_date()[:8],  # YYYYMMDD (NO time)
        "totItemCnt": 1,
        # TAX BREAKDOWN (ALL 15 FIELDS REQUIRED)
        "taxblAmtA": 0.00, "taxblAmtB": 0.00, "taxblAmtC": 81000.00,
        "taxblAmtD": 0.00, "taxblAmtE": 0.00,
        "taxRtA": 0.00, "taxRtB": 0.00, "taxRtC": 0.00,
        "taxRtD": 0.00, "taxRtE": 0.00,
        "taxAmtA": 0.00, "taxAmtB": 0.00, "taxAmtC": 0.00,
        "taxAmtD": 0.00, "taxAmtE": 0.00,
        "totTaxblAmt": 81000.00,
        "totTaxAmt": 0.00,
        "totAmt": 81000.00,
        "regrId": "Admin", "regrNm": "Admin",
        "modrId": "Admin", "modrNm": "Admin",
        "itemList": [{
            "itemSeq": 1,
            "itemCd": "KE2NTBA00000001",  # Must exist in KRA system
            "itemClsCd": "1000000000",
            "itemNm": "Brand A",
            "barCd": "",  # Nullable but REQUIRED field
            "pkgUnitCd": "NT",
            "pkg": 1,     # Package quantity
            "qtyUnitCd": "BA",
            "qty": 90.0,
            "prc": 1000.00,
            "splyAmt": 81000.00,
            "dcRt": 10.0,   # Discount rate %
            "dcAmt": 9000.00,  # Discount amount
            "taxTyCd": "C",    # C = Zero-rated/Exempt
            "taxblAmt": 81000.00,
            "taxAmt": 0.00,
            "totAmt": 81000.00,  # splyAmt - dcAmt + taxAmt
        }],
    })
    
    print(f"✅ Sales transaction sent (resultCd: {response['resultCd']})")
    print(f"Receipt Signature: {response['data']['rcptSign']}")

except ValidationException as e:
    print("❌ Validation failed:")
    for err in e.errors:
        field = err.get('loc', [])[0] if err.get('loc') else 'unknown'
        print(f"  • {field}: {err.get('msg', 'validation error')}")

except ApiException as e:
    print(f"❌ KRA API Error ({e.error_code}): {e}")
    if e.details and 'resultMsg' in e.details:
        print(f"KRA Message: {e.details['resultMsg']}")
```

---

## API Reference

### Functional Categories (8 Total)

| Category | Purpose | Endpoints |
|----------|---------|-----------|
| **Initialization** | Device registration & cmcKey acquisition | `select_init_info` |
| **Data Management** | Retrieve standard codes & master data | `select_code_list`, `select_item_cls_list`, `select_bhf_list`, `select_taxpayer_info`, `select_customer_list`, `select_notice_list` |
| **Branch Management** | Manage branch offices & users | `branch_insurance_info`, `branch_user_account`, `branch_send_customer_info` |
| **Item Management** | Item master data | `save_item`, `item_info` |
| **Purchase Management** | Purchase transactions | `select_purchase_trns`, `send_purchase_transaction_info` |
| **Sales Management** | Sales transactions & invoices | `send_sales_transaction`, `select_sales_trns`, `select_invoice_detail` |
| **Stock Management** | Inventory movements & stock levels | `insert_stock_io`, `save_stock_master`, `select_move_list` |

### Core Classes

| Class | Purpose |
|-------|---------|
| `AuthClient` | Token generation, caching (60s buffer), and refresh management |
| `BaseClient` | HTTP request handling, header management, error unwrapping |
| `EtimsClient` | Business endpoint methods (all 8 functional categories) |
| `Validator` | Payload validation against KRA schemas (Pydantic v2) |

---

## Field Validation Rules (From Postman Collection)

| Field | Validation Rule | Error if Violated |
|-------|-----------------|-------------------|
| `dvcSrlNo` | Must be pre-registered with KRA | `resultCd: 901` "It is not valid device" |
| `lastReqDt` | Cannot be future date; max 7 days old | `resultCd: 500` "Check request body" |
| `salesDt` | Must be `YYYYMMDD` format; not future | `resultCd: 500` |
| `cfmDt` | Must be `YYYYMMDDHHmmss` format | `resultCd: 500` |
| `invcNo` | Must be sequential integer (not string) | `resultCd: 500` |
| `taxTyCd` | Must be A/B/C/D/E | `resultCd: 500` |
| `itemCd` | Must exist in KRA system (for transactions) | `resultCd: 500` |
| `pkg` | Must be ≥ 1 | `resultCd: 500` |
| `qty` | Must be > 0.001 | `resultCd: 500` |
| `dcRt` | Cannot be negative | `resultCd: 500` |

---

## Error Handling

### Exception Types

| Exception | When Thrown | Example |
|-----------|-------------|---------|
| `AuthenticationException` | Token generation fails | Invalid consumer key/secret |
| `ApiException` | KRA business error (`resultCd !== '0000'`) | `resultCd: 500` (invalid payload) |
| `ValidationException` | Payload fails schema validation | Missing required field |

### Handling Pattern
```python
try:
    response = etims.send_sales_transaction(payload)
    
except ValidationException as e:
    print("❌ Validation failed:")
    for error in e.errors:
        field = error.get('loc', [])[0] if error.get('loc') else 'unknown'
        print(f"  • {field}: {error.get('msg', 'validation error')}")

except ApiException as e:
    print(f"❌ KRA API Error ({e.error_code}): {e}")
    
    # Get full KRA response for debugging
    if e.details and 'resultMsg' in e.details:
        print(f"KRA Message: {e.details['resultMsg']}")
    
    # Handle specific error codes
    if e.error_code == "901":
        print("→ Device serial not registered with KRA")
    elif e.error_code == "902":
        print("→ cmcKey expired - reinitialize OSCU")
    elif e.error_code == "500":
        print("→ Invalid payload - check date formats/tax fields")

except AuthenticationException as e:
    print(f"❌ Authentication failed: {e}")
    
    # Attempt token refresh
    try:
        auth.token(force_refresh=True)
        # Retry operation...
    except Exception as ex:
        print(f"Token refresh failed: {ex}")
```

### Comprehensive KRA Error Codes

| Code | Meaning | Solution |
|------|---------|----------|
| `0000` | Success | ✅ Operation completed |
| `901` | "It is not valid device" | Use KRA-approved device serial |
| `902` | "Invalid cmcKey" | Re-initialize OSCU to get fresh cmcKey |
| `500` | "Check request body" | Validate payload against Postman schema |
| `501` | "Mandatory information missing" | Check required fields per endpoint |
| `502` | "Invalid format" | Fix date formats / data types |
| `503` | "Data not found" | Verify TIN/branch/item exists in KRA system |
| `504` | "Duplicate data" | Use unique invoice number |
| `505` | "Data relationship error" | Check parent-child relationships |
| `401` | "Unauthorized" | Check token validity header |
| `429` | "Rate limit exceeded" | Implement request throttling (max 100 req/min) |

---

## Troubleshooting

### ❌ "It is not valid device" (resultCd: 901)

**Cause**: Device serial not registered with KRA sandbox  
**Solution**:
1. Email `timsupport@kra.go.ke` with subject:  
   `"Request for OSCU Sandbox Test Credentials - [Your Company Name] - PIN: [Your PIN]"`
2. Use **static** approved serial (e.g., `dvcv1130`) – never generate dynamically
3. Verify TIN/branch ID match registered device

### ❌ "Invalid cmcKey" (resultCd: 902)

**Cause**: cmcKey expired or not set in config  
**Solution**:
```python
# After initialization:
config.oscu["cmc_key"] = extracted_cmc_key
etims = EtimsClient(config, auth)  # MUST recreate client
```

### ❌ Trailing spaces in URLs

**Cause**: Copy-paste errors from documentation  
**Solution**: Always use `.strip()` on URLs:
```python
"token_url": "https://sbx.kra.go.ke/v1/token/generate  ".strip(),
```

### ❌ Invoice number rejected

**Cause**: Using string prefix (`INV001`) instead of integer  
**Solution**: Use sequential integers starting from 1:
```python
"invcNo": 1,  # ✅ Correct
# NOT "INV001" ❌
```

---

## Automated Testing Requirements

KRA mandates successful completion of automated tests before verification:

### Test Execution Flow
1. Run integration tests against sandbox environment
2. System validates:
   - Token generation
   - OSCU initialization
   - Code list retrieval
   - Item creation
   - Sales transaction with full tax breakdown
   - Invoice retrieval
3. Upon success, system provides **1-hour window** to upload artifacts

### Required Artifacts (Upload Within 1 Hour)
| Artifact | Format | Requirements |
|----------|--------|--------------|
| Item Creation Screenshot | PNG/JPEG | Must show item code, tax category, price |
| Invoice Generation Screenshot | PNG/JPEG | Must show OSCU signatures, QR code |
| Invoice Copy | PDF | Full invoice with all KRA-mandated fields |
| Credit Note Copy | PDF | Must show original invoice reference |

> ⚠️ **Failure to upload within 1 hour** = Test invalidated → Must re-run entire test suite

---

## KYC Documentation Checklist

### Third-Party Integrators (All Required)
- [ ] eTIMS Bio Data Form (completed with director details)
- [ ] Certificate of Incorporation + CR12 (or Business Registration Certificate)
- [ ] Valid Business Permit (current year)
- [ ] National IDs of all directors/partners
- [ ] Company Tax Compliance Certificate (valid for current year)
- [ ] Proof of 3+ qualified technical staff:
  - CVs showing Python/Java/C# experience
  - Certifications (e.g., AWS, Azure, KRA eTIMS training)
  - Employment contracts showing system administration duties
- [ ] Notarized solvency declaration (signed by director + notary public)
- [ ] Technology Architecture document:
  - System diagram showing TIS ↔ OSCU data flow
  - Database schema for invoice storage
  - Security measures (encryption, access controls)
  - Disaster recovery plan

### Self-Integrators (Minimal Set)
- [ ] eTIMS Bio Data Form
- [ ] Company Tax Compliance Certificate
- [ ] National ID of sole proprietor/director
- [ ] Technology Architecture document (simplified)

---

## Go-Live Process

### For Third-Party Integrators
1. Upon KYC approval, receive SLA template via Developer Portal
2. Complete SLA with company details and authorized signatory
3. Email signed SLA to `timsupport@kra.go.ke` with subject:  
   `"SLA Execution with KRA - [Your Company Name]"`
4. Await KRA approval (5-7 business days)
5. Receive production keys via Developer Portal:
   - Production consumer key/secret
6. Deploy to production environment (`api.developer.go.ke`)
7. Monitor compliance for first 30 days (KRA conducts spot checks)

### For Self-Integrators
1. Receive interim approval letter after KYC verification
2. Receive production keys via Developer Portal
3. Deploy directly to production environment
4. No SLA execution required

> 💡 **Production URL**: `https://api.developer.go.ke/etims-oscu/api/v1`  
> ⚠️ **Never use sandbox credentials in production** – KRA monitors environment separation strictly

---

## Support

### KRA Official Support Channels
| Purpose | Contact | Expected Response |
|---------|---------|-------------------|
| Sandbox credentials & device registration | `timsupport@kra.go.ke` | 1-3 business days |
| API technical issues & Postman collection | `apisupport@kra.go.ke` | 24-48 hours |
| Developer Portal access issues | `apisupport@kra.go.ke` | 24 hours |
| Verification meeting scheduling | Developer Portal UI | Instant (self-service) |
| SLA execution queries | `timsupport@kra.go.ke` | 3-5 business days |

### SDK Support
- **GitHub Issues**: [github.com/paybillke/kra-etims-python-sdk/issues](https://github.com/paybillke/kra-etims-python-sdk/issues)
- **Email**: ebartile@gmail.com (for integration guidance)
- **Emergency Hotline**: +254757807150 (business hours only)

> ℹ️ **Disclaimer**: This SDK is not officially endorsed by Kenya Revenue Authority. Always verify integration requirements with KRA before production deployment. KRA may update API specifications without notice – monitor [GavaConnect Portal](https://developer.go.ke) for updates.

---

## License

MIT License

Copyright © 2024-2026 Bartile Emmanuel / Paybill Kenya

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## Attribution

This SDK was developed by **Bartile Emmanuel** for Paybill Kenya to simplify KRA eTIMS OSCU integration for Kenyan businesses. Special thanks to KRA for providing comprehensive API documentation and Postman collections.

> 🇰🇪 **Proudly Made in Kenya** – Supporting digital tax compliance for East Africa's largest economy.  
> *Tested on KRA Sandbox • Built with Python • Pydantic v2 Validation • Production Ready*