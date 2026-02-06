from typing import List, Optional
from typing_extensions import Annotated
from pydantic import (
    BaseModel,
    Field,
    conint,
    condecimal,
    StringConstraints,
    AfterValidator,
)
import re


# =========================================================
# COMMON CONSTRAINED TYPES (aligned with PHP)
# =========================================================

TIN = Annotated[str, StringConstraints(min_length=1, max_length=20)]
BHF_ID = Annotated[str, StringConstraints(min_length=1, max_length=10)]  # Fixed: was 20

YN = Annotated[str, StringConstraints(pattern=r"^[YN]$")]

# YYYYMMDDHHMMSS (exactly 14 digits)
DT14 = Annotated[str, StringConstraints(pattern=r"^\d{14}$")]

# Flexible date: 8 to 14 digits (used in purchase/sales dates)
FLEX_DATE = Annotated[str, StringConstraints(min_length=8, max_length=14)]

# Exactly 8-digit date (YYYYMMDD)
DT8 = Annotated[str, StringConstraints(pattern=r"^\d{8}$")]


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
    "initialization": Initialization,

    # COMMON
    "lastReqOnly": LastReqOnly,
    "custSearchReq": CustSearchReq,

    # BRANCH
    "branchCustomer": BranchCustomer,
    "branchUser": BranchUser,
    "branchInsurance": BranchInsurance,

    # ITEM
    "saveItem": SaveItem,
    "itemComposition": ItemComposition,

    # IMPORTED ITEM
    "importItemUpdate": ImportItemUpdate,

    # STOCK
    "stockMaster": StockMaster,
    "insertTrnsPurchase": InsertTrnsPurchase,
    "saveStockIO": SaveStockIO,
}
