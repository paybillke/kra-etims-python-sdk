from typing import List, Optional
from decimal import Decimal
from typing_extensions import Annotated
from pydantic import (
    BaseModel,
    Field,
    conint,
    condecimal,
    StringConstraints,
    model_validator,
    field_validator,
    AfterValidator,
)
import re


# =========================================================
# COMMON CONSTRAINED TYPES (aligned with PHP)
# =========================================================

TIN = Annotated[str, StringConstraints(min_length=11, max_length=11, pattern=r"^[A-Z0-9]{11}$")]
BHF_ID = Annotated[str, StringConstraints(min_length=2, max_length=2)]
YN = Annotated[str, StringConstraints(pattern=r"^[YN]$")]
DT14 = Annotated[str, StringConstraints(pattern=r"^\d{14}$")]  # yyyyMMddHHmmss
DT8 = Annotated[str, StringConstraints(pattern=r"^\d{8}$")]    # yyyyMMdd
CODE_5 = Annotated[str, StringConstraints(min_length=1, max_length=5, pattern=r"^[A-Z0-9]{1,5}$")]
CODE_10 = Annotated[str, StringConstraints(min_length=1, max_length=10, pattern=r"^[A-Z0-9]{1,10}$")]
AMOUNT_18_2 = Annotated[Decimal, Field(ge=0, max_digits=18, decimal_places=2)]
AMOUNT_13_2 = Annotated[Decimal, Field(ge=0, max_digits=13, decimal_places=2)]
RATE_7_2 = Annotated[Decimal, Field(ge=0, le=100, max_digits=7, decimal_places=2)]  # Tax rates capped at 100%
RATE_5_2 = Annotated[Decimal, Field(ge=0, le=100, max_digits=5, decimal_places=2)]  # Discount rate
RATE_3_INT = Annotated[int, Field(ge=0, le=100)]  # Insurance rate as integer percentage
FLEX_DATE = Annotated[str, StringConstraints(min_length=8, max_length=14)]

# =========================================================
# NESTED MODELS FOR SAVE TRNS SALES OSDC REQUEST
# =========================================================

class TrnsSalesSaveWrReceipt(BaseModel):
    """Receipt information sub-object (TrnsSalesSaveWrReceipt)"""
    custTin: Optional[TIN] = None
    custMblNo: Optional[Annotated[str, StringConstraints(max_length=20)]] = None
    rcptPbctDt: DT14  # Required per spec
    trdeNm: Optional[Annotated[str, StringConstraints(max_length=20)]] = None
    adrs: Optional[Annotated[str, StringConstraints(max_length=200)]] = None
    topMsg: Optional[Annotated[str, StringConstraints(max_length=20)]] = None
    btmMsg: Optional[Annotated[str, StringConstraints(max_length=20)]] = None
    prchrAcptcYn: YN  # Required per spec

class TrnsSalesSaveWrItem(BaseModel):
    """Individual item in sales transaction (TrnsSalesSaveWrItem)"""
    itemSeq: conint(ge=1, le=999)  # 3-digit sequence
    itemClsCd: Optional[CODE_10] = None
    itemCd: Annotated[str, StringConstraints(min_length=1, max_length=20)]
    itemNm: Annotated[str, StringConstraints(min_length=1, max_length=200)]
    bcd: Optional[Annotated[str, StringConstraints(max_length=20)]] = None
    pkgUnitCd: CODE_5  # Required per spec (see 4.5)
    pkg: AMOUNT_13_2
    qtyUnitCd: CODE_5  # Required per spec (see 4.6)
    qty: AMOUNT_13_2
    prc: AMOUNT_18_2
    splyAmt: AMOUNT_18_2
    dcRt: RATE_5_2
    dcAmt: AMOUNT_18_2
    isrccCd: Optional[CODE_10] = None
    isrccNm: Optional[Annotated[str, StringConstraints(max_length=100)]] = None
    isrcRt: Optional[RATE_3_INT] = None
    isrcAmt: Optional[AMOUNT_18_2] = None
    taxTyCd: CODE_5  # Required per spec (see 4.1)
    taxblAmt: AMOUNT_18_2
    taxAmt: AMOUNT_18_2  # Matches JSON sample key "taxAmt" (not "totTaxAmt" from table)
    totAmt: AMOUNT_18_2

    @model_validator(mode="after")
    def validate_amounts(self) -> 'TrnsSalesSaveWrItem':
        """Business rule: totAmt should equal splyAmt - dcAmt + taxAmt"""
        calculated = self.splyAmt - self.dcAmt + self.taxAmt
        if abs(calculated - self.totAmt) > Decimal("0.01"):
            raise ValueError(
                f"Item total mismatch: splyAmt({self.splyAmt}) - dcAmt({self.dcAmt}) + taxAmt({self.taxAmt}) = {calculated} ≠ totAmt({self.totAmt})"
            )
        return self

# =========================================================
# MAIN REQUEST MODEL: TrnsSalesSaveWrReq
# =========================================================

class SaveTrnsSalesOsdc(BaseModel):
    """
    Request model for /saveTrnsSalesOsdc endpoint (TrnsSalesSaveWrReq)
    Validates all fields per specification table and JSON sample
    """
    # === REQUIRED FIELDS (per spec table) ===
    tin: TIN
    bhfId: BHF_ID
    cmcKey: Annotated[str, StringConstraints(min_length=1, max_length=255)]
    trdInvcNo: Annotated[str, StringConstraints(min_length=1, max_length=50)]
    invcNo: Annotated[str, StringConstraints(pattern=r"^\d{1,38}$")]  # Numeric string, 1-38 digits
    orgInvcNo: Annotated[str, StringConstraints(pattern=r"^\d{1,38}$")]
    rcptTyCd: CODE_5  # Required (see 4.9 Sale Receipt Type)
    salesSttsCd: CODE_5  # Required (see 4.11 Transaction Progress)
    cfmDt: DT14  # yyyyMMddHHmmss
    salesDt: DT8  # yyyyMMdd
    totItemCnt: conint(ge=0, le=9999999999)  # 10-digit max
    taxblAmtA: AMOUNT_18_2
    taxblAmtB: AMOUNT_18_2
    taxblAmtC: AMOUNT_18_2
    taxblAmtD: AMOUNT_18_2
    taxblAmtE: AMOUNT_18_2
    taxRtA: RATE_7_2
    taxRtB: RATE_7_2
    taxRtC: RATE_7_2
    taxRtD: RATE_7_2
    taxRtE: RATE_7_2
    taxAmtA: AMOUNT_18_2
    taxAmtB: AMOUNT_18_2
    taxAmtC: AMOUNT_18_2
    taxAmtD: AMOUNT_18_2
    taxAmtE: AMOUNT_18_2
    totTaxblAmt: AMOUNT_18_2
    totTaxAmt: AMOUNT_18_2
    totAmt: AMOUNT_18_2
    prchrAcptcYn: YN
    regrId: Annotated[str, StringConstraints(min_length=1, max_length=20)]
    regrNm: Annotated[str, StringConstraints(min_length=1, max_length=60)]
    modrId: Annotated[str, StringConstraints(min_length=1, max_length=20)]
    modrNm: Annotated[str, StringConstraints(min_length=1, max_length=60)]
    receipt: TrnsSalesSaveWrReceipt
    itemList: List[TrnsSalesSaveWrItem]
    
    # === OPTIONAL FIELDS ===
    custTin: Optional[TIN] = None
    custNm: Optional[Annotated[str, StringConstraints(min_length=1, max_length=60)]] = None
    pmtTyCd: Optional[CODE_5] = None  # (see 4.10 Payment Method)
    stockRlsDt: Optional[DT14] = None
    cnclReqDt: Optional[DT14] = None
    cnclDt: Optional[DT14] = None
    rfdDt: Optional[DT14] = None
    rfdRsnCd: Optional[CODE_5] = None  # (see 4.16 Credit Note Reason)
    remark: Optional[Annotated[str, StringConstraints(max_length=400)]] = None

    @field_validator('invcNo', 'orgInvcNo')
    @classmethod
    def validate_invoice_numbers(cls, v: str) -> str:
        """Ensure invoice numbers don't have leading zeros unless value is zero"""
        if v != "0" and v.startswith("0"):
            raise ValueError("Invoice numbers must not have leading zeros")
        return v

    @model_validator(mode="after")
    def validate_date_logic(self) -> 'SaveTrnsSalesOsdc':
        """Validate date relationships"""
        # salesDt (8-digit) must be prefix of cfmDt (14-digit)
        if self.cfmDt[:8] != self.salesDt:
            raise ValueError(f"cfmDt ({self.cfmDt}) must start with salesDt ({self.salesDt})")
        
        # Optional dates must be >= salesDt if present
        for dt_field in ['stockRlsDt', 'cnclReqDt', 'cnclDt', 'rfdDt']:
            dt_val = getattr(self, dt_field)
            if dt_val and dt_val[:8] < self.salesDt:
                raise ValueError(f"{dt_field} ({dt_val}) cannot be before salesDt ({self.salesDt})")
        return self

    @model_validator(mode="after")
    def validate_amount_aggregates(self) -> 'SaveTrnsSalesOsdc':
        """Validate header amounts match item list aggregates and tax calculations"""
        if not self.itemList:
            raise ValueError("itemList cannot be empty when totItemCnt > 0")
        
        # Validate item count
        if len(self.itemList) != self.totItemCnt:
            raise ValueError(f"totItemCnt ({self.totItemCnt}) must match actual itemList length ({len(self.itemList)})")
        
        # Calculate aggregates from items
        calc_taxbl = sum(item.taxblAmt for item in self.itemList)
        calc_tax = sum(item.taxAmt for item in self.itemList)
        calc_tot = sum(item.totAmt for item in self.itemList)
        
        # Validate against header totals (with rounding tolerance)
        tolerance = Decimal("0.01")
        if abs(calc_taxbl - self.totTaxblAmt) > tolerance:
            raise ValueError(f"Header totTaxblAmt ({self.totTaxblAmt}) ≠ sum of item taxblAmt ({calc_taxbl})")
        if abs(calc_tax - self.totTaxAmt) > tolerance:
            raise ValueError(f"Header totTaxAmt ({self.totTaxAmt}) ≠ sum of item taxAmt ({calc_tax})")
        if abs(calc_tot - self.totAmt) > tolerance:
            raise ValueError(f"Header totAmt ({self.totAmt}) ≠ sum of item totAmt ({calc_tot})")
        
        # Validate tax component sums (A-E)
        taxbl_components = (
            self.taxblAmtA + self.taxblAmtB + self.taxblAmtC + 
            self.taxblAmtD + self.taxblAmtE
        )
        if abs(taxbl_components - self.totTaxblAmt) > tolerance:
            raise ValueError(
                f"Sum of taxblAmtA-E ({taxbl_components}) must equal totTaxblAmt ({self.totTaxblAmt})"
            )
        
        tax_components = (
            self.taxAmtA + self.taxAmtB + self.taxAmtC + 
            self.taxAmtD + self.taxAmtE
        )
        if abs(tax_components - self.totTaxAmt) > tolerance:
            raise ValueError(
                f"Sum of taxAmtA-E ({tax_components}) must equal totTaxAmt ({self.totTaxAmt})"
            )
        return self

    @model_validator(mode="after")
    def validate_cancelation_logic(self) -> 'SaveTrnsSalesOsdc':
        """Validate cancelation/date dependencies"""
        if self.salesSttsCd == "03":  # Assuming "03" = Canceled (per common patterns)
            if not self.cnclDt:
                raise ValueError("cnclDt is required when salesSttsCd indicates canceled status")
            if not self.cnclReqDt:
                raise ValueError("cnclReqDt is required when salesSttsCd indicates canceled status")
        elif any([self.cnclReqDt, self.cnclDt]):
            raise ValueError(
                "cnclReqDt/cnclDt should only be provided when salesSttsCd indicates cancellation"
            )
        return self

# =========================================================
# RESPONSE MODELS: TrnsSalesSaveWrRes
# =========================================================

class TrnsSalesSaveWrResData(BaseModel):
    """Response data payload (TrnsSalesSaveWrResData)"""
    curRcptNo: conint(ge=0, le=9999999999)  # 10-digit max
    totRcptNo: conint(ge=0, le=9999999999)
    intrlData: Annotated[str, StringConstraints(min_length=26, max_length=26)]
    rcptSign: Annotated[str, StringConstraints(min_length=16, max_length=16)]
    sdcDateTime: DT14  # yyyyMMddHHmmss

class TrnsSalesSaveWrRes(BaseModel):
    """Full response object (TrnsSalesSaveWrRes)"""
    resultCd: Annotated[str, StringConstraints(min_length=3, max_length=3)]
    resultMsg: Annotated[str, StringConstraints(max_length=500)]
    resultDt: DT14
    data: Optional[TrnsSalesSaveWrResData] = None

    @field_validator('resultCd')
    @classmethod
    def validate_result_code(cls, v: str) -> str:
        """Basic validation: success code is '000' per sample"""
        if v != "000" and not v.isdigit():
            raise ValueError("resultCd must be numeric (e.g., '000' for success)")
        return v

# =========================================================
# INITIALIZATION
# =========================================================

class Initialization(BaseModel):
    tin: TIN
    bhfId: BHF_ID
    dvcSrlNo: Annotated[str, StringConstraints(min_length=1)]  # no max in PHP


# =========================================================
# COMMON REQUESTS
# =========================================================

class LastReqOnly(BaseModel):
    lastReqDt: DT14


class CustSearchReq(BaseModel):
    custmTin: TIN


# =========================================================
# BRANCH MANAGEMENT
# =========================================================

class BranchCustomer(BaseModel):
    custNo: Annotated[str, StringConstraints(min_length=1)]
    custTin: TIN
    custNm: Annotated[str, StringConstraints(min_length=1)]
    useYn: YN
    regrId: Annotated[str, StringConstraints(min_length=1)]
    regrNm: Annotated[str, StringConstraints(min_length=1)]
    modrId: Optional[str] = None
    modrNm: Optional[str] = None


class BranchUser(BaseModel):
    userId: Annotated[str, StringConstraints(min_length=1)]
    userNm: Annotated[str, StringConstraints(min_length=1)]
    pwd: Annotated[str, StringConstraints(min_length=1)]
    useYn: YN
    regrId: Annotated[str, StringConstraints(min_length=1)]
    regrNm: Annotated[str, StringConstraints(min_length=1)]
    modrId: Optional[str] = None
    modrNm: Optional[str] = None


class BranchInsurance(BaseModel):
    isrccCd: Annotated[str, StringConstraints(min_length=1)]
    isrccNm: Annotated[str, StringConstraints(min_length=1)]
    isrcRt: condecimal(ge=0)
    useYn: YN
    regrId: Annotated[str, StringConstraints(min_length=1)]
    regrNm: Annotated[str, StringConstraints(min_length=1)]
    modrId: Optional[str] = None
    modrNm: Optional[str] = None


# =========================================================
# ITEM
# =========================================================

class SaveItem(BaseModel):
    itemCd: Annotated[str, StringConstraints(min_length=1)]
    itemClsCd: Annotated[str, StringConstraints(min_length=1)]
    itemTyCd: Annotated[str, StringConstraints(min_length=1)]
    itemNm: Annotated[str, StringConstraints(min_length=1)]
    itemStdNm: Optional[Annotated[str, ...]] = None  # string or null
    orgnNatCd: Annotated[str, StringConstraints(min_length=2, max_length=5)]
    pkgUnitCd: Annotated[str, StringConstraints(min_length=1)]
    qtyUnitCd: Annotated[str, StringConstraints(min_length=1)]
    taxTyCd: Annotated[str, StringConstraints(min_length=1)]
    dftPrc: condecimal(ge=0)
    grpPrcL1: Optional[condecimal()] = None
    grpPrcL2: Optional[condecimal()] = None
    grpPrcL3: Optional[condecimal()] = None
    grpPrcL4: Optional[condecimal()] = None
    grpPrcL5: Optional[condecimal()] = None
    btchNo: Optional[Annotated[str, ...]] = None  # string or null
    bcd: Optional[Annotated[str, ...]] = None     # string or null
    addInfo: Optional[Annotated[str, ...]] = None # string or null
    sftyQty: Optional[condecimal()] = None
    isrcAplcbYn: YN
    useYn: YN
    regrId: Annotated[str, StringConstraints(min_length=1)]
    regrNm: Annotated[str, StringConstraints(min_length=1)]
    modrId: Annotated[str, StringConstraints(min_length=1)]  # REQUIRED in PHP
    modrNm: Annotated[str, StringConstraints(min_length=1)]  # REQUIRED in PHP


class ItemComposition(BaseModel):
    itemCd: Annotated[str, StringConstraints(min_length=1)]
    cpstItemCd: Annotated[str, StringConstraints(min_length=1)]
    cpstQty: condecimal(gt=0)  # min(0.001) → gt=0 covers it
    regrId: Annotated[str, StringConstraints(min_length=1)]
    regrNm: Annotated[str, StringConstraints(min_length=1)]
    modrId: Optional[str] = None
    modrNm: Optional[str] = None


# =========================================================
# IMPORTED ITEM
# =========================================================

class ImportItemUpdate(BaseModel):
    taskCd: Annotated[str, StringConstraints(min_length=1)]
    dclDe: Annotated[str, StringConstraints(min_length=8, max_length=14)]
    itemSeq: conint(ge=1)
    hsCd: Annotated[str, StringConstraints(min_length=1, max_length=17)]
    itemClsCd: Annotated[str, StringConstraints(min_length=1, max_length=10)]
    itemCd: Annotated[str, StringConstraints(min_length=1, max_length=20)]
    imptItemSttsCd: Annotated[str, StringConstraints(min_length=1)]
    modrId: Annotated[str, StringConstraints(min_length=1)]
    modrNm: Annotated[str, StringConstraints(min_length=1)]
    remark: Optional[str] = None


# =========================================================
# STOCK
# =========================================================

class StockMaster(BaseModel):
    itemCd: Annotated[str, StringConstraints(min_length=1, max_length=20)]
    rsdQty: condecimal(ge=0)  # Remaining quantity
    regrId: Annotated[str, StringConstraints(min_length=1, max_length=20)]
    regrNm: Annotated[str, StringConstraints(min_length=1, max_length=60)]
    modrId: Annotated[str, StringConstraints(min_length=1, max_length=20)]
    modrNm: Annotated[str, StringConstraints(min_length=1, max_length=60)]


# Purchase Transaction Item (for insertTrnsPurchase)
class InsertTrnsPurchaseItem(BaseModel):
    itemSeq: conint(ge=1)
    itemCd: Annotated[str, StringConstraints(min_length=1, max_length=20)]
    itemClsCd: Annotated[str, StringConstraints(min_length=1, max_length=10)]
    itemNm: Annotated[str, StringConstraints(min_length=1, max_length=200)]
    bcd: Optional[Annotated[str, StringConstraints(max_length=20)]] = None
    spplrItemClsCd: Optional[Annotated[str, StringConstraints(max_length=10)]] = None
    spplrItemCd: Optional[Annotated[str, StringConstraints(max_length=20)]] = None
    spplrItemNm: Optional[Annotated[str, StringConstraints(max_length=200)]] = None
    pkgUnitCd: Annotated[str, StringConstraints(max_length=5)]
    pkg: condecimal()
    qtyUnitCd: Annotated[str, StringConstraints(max_length=5)]
    qty: condecimal()
    prc: condecimal()
    splyAmt: condecimal()
    dcRt: condecimal()
    dcAmt: condecimal()
    taxblAmt: condecimal()
    taxTyCd: Annotated[str, StringConstraints(max_length=5)]
    taxAmt: condecimal()
    totAmt: condecimal()
    itemExprDt: Optional[FLEX_DATE] = None  # 8–14 digits


class InsertTrnsPurchase(BaseModel):
    spplrTin: Optional[Annotated[str, StringConstraints(min_length=11, max_length=11)]] = None
    invcNo: conint(ge=0)
    orgInvcNo: conint(ge=0)
    spplrBhfId: Optional[Annotated[str, StringConstraints(min_length=2, max_length=2)]] = None
    spplrNm: Optional[Annotated[str, StringConstraints(max_length=60)]] = None
    spplrInvcNo: Optional[conint(ge=0)] = None
    regTyCd: Annotated[str, StringConstraints(min_length=1, max_length=5)]
    pchsTyCd: Annotated[str, StringConstraints(min_length=1, max_length=5)]
    rcptTyCd: Annotated[str, StringConstraints(min_length=1, max_length=5)]
    pmtTyCd: Annotated[str, StringConstraints(min_length=1, max_length=5)]
    pchsSttsCd: Annotated[str, StringConstraints(min_length=1, max_length=5)]
    cfmDt: Optional[FLEX_DATE] = None
    wrhsDt: Optional[FLEX_DATE] = None
    cnclReqDt: Optional[FLEX_DATE] = None
    cnclDt: Optional[FLEX_DATE] = None
    rfdDt: Optional[FLEX_DATE] = None
    pchsDt: Optional[FLEX_DATE] = None
    totItemCnt: conint(ge=0)
    taxblAmtA: condecimal()
    taxblAmtB: condecimal()
    taxblAmtC: condecimal()
    taxblAmtD: condecimal()
    taxblAmtE: condecimal()
    taxRtA: condecimal()
    taxRtB: condecimal()
    taxRtC: condecimal()
    taxRtD: condecimal()
    taxRtE: condecimal()
    taxAmtA: condecimal()
    taxAmtB: condecimal()
    taxAmtC: condecimal()
    taxAmtD: condecimal()
    taxAmtE: condecimal()
    totTaxblAmt: condecimal()
    totTaxAmt: condecimal()
    totAmt: condecimal()
    remark: Optional[Annotated[str, StringConstraints(max_length=400)]] = None
    regrId: Annotated[str, StringConstraints(max_length=20)]
    regrNm: Annotated[str, StringConstraints(max_length=60)]
    modrId: Annotated[str, StringConstraints(max_length=20)]
    modrNm: Annotated[str, StringConstraints(max_length=60)]
    itemList: List[InsertTrnsPurchaseItem]


# Stock IO Item
class SaveStockIOItem(BaseModel):
    itemSeq: conint(ge=1)
    itemCd: Annotated[str, StringConstraints(min_length=1, max_length=20)]
    itemClsCd: Annotated[str, StringConstraints(min_length=1, max_length=10)]
    itemNm: Annotated[str, StringConstraints(min_length=1, max_length=200)]
    bcd: Optional[Annotated[str, StringConstraints(max_length=20)]] = None
    pkgUnitCd: Annotated[str, StringConstraints(max_length=5)]
    pkg: condecimal()
    qtyUnitCd: Annotated[str, StringConstraints(max_length=5)]
    qty: condecimal()
    itemExprDt: Optional[DT8] = None  # YYYYMMDD only
    prc: condecimal()
    splyAmt: condecimal()
    totDcAmt: condecimal()
    taxblAmt: condecimal()
    taxTyCd: Annotated[str, StringConstraints(max_length=5)]
    taxAmt: condecimal()
    totAmt: condecimal()


class SaveStockIO(BaseModel):
    tin: Annotated[str, StringConstraints(min_length=11, max_length=11)]
    bhfId: Annotated[str, StringConstraints(min_length=2, max_length=2)]
    sarNo: conint(ge=0)
    orgSarNo: conint(ge=0)
    regTyCd: Annotated[str, StringConstraints(min_length=1, max_length=5)]
    custTin: Optional[Annotated[str, StringConstraints(min_length=11, max_length=11)]] = None
    custNm: Optional[Annotated[str, StringConstraints(max_length=100)]] = None
    custBhfId: Optional[Annotated[str, StringConstraints(min_length=2, max_length=2)]] = None
    sarTyCd: Annotated[str, StringConstraints(min_length=1, max_length=5)]
    ocrnDt: DT8  # YYYYMMDD
    totItemCnt: conint(ge=0)
    totTaxblAmt: condecimal()
    totTaxAmt: condecimal()
    totAmt: condecimal()
    remark: Optional[Annotated[str, StringConstraints(max_length=400)]] = None
    regrId: Annotated[str, StringConstraints(max_length=20)]
    regrNm: Annotated[str, StringConstraints(max_length=60)]
    modrId: Annotated[str, StringConstraints(max_length=20)]
    modrNm: Annotated[str, StringConstraints(max_length=60)]
    itemList: List[SaveStockIOItem]


# =========================================================
# VALIDATOR MAP
# =========================================================

from .exceptions import ValidationException

SCHEMAS = {
    # INITIALIZATION
    "selectInitOsdcInfo": Initialization,

    # COMMON
    "lastReqOnly": LastReqOnly,
    "selectCustomer": CustSearchReq,

    # BRANCH
    "saveBhfCustomer": BranchCustomer,
    "saveBhfUser": BranchUser,
    "saveBhfInsurance": BranchInsurance,

    # ITEM
    "saveItem": SaveItem,
    "saveItemComposition": ItemComposition,

    # IMPORTED ITEM
    "importItemUpdate": ImportItemUpdate,

    # STOCK
    "saveStockMaster": StockMaster,
    "insertTrnsPurchase": InsertTrnsPurchase,
    "insertStockIO": SaveStockIO,
    "saveTrnsSalesOsdc": SaveTrnsSalesOsdc
}
