from typing import List, Optional
from typing_extensions import Annotated

from pydantic import (
    BaseModel,
    Field,
    conint,
    condecimal,
    StringConstraints,
)

# =========================================================
# COMMON CONSTRAINED TYPES (Pydantic v2 style)
# =========================================================

TIN = Annotated[str, StringConstraints(min_length=1, max_length=20)]
BHF = Annotated[str, StringConstraints(min_length=1, max_length=20)]

YN = Annotated[str, StringConstraints(pattern="^[YN]$")]

DT14 = Annotated[str, StringConstraints(pattern=r"^\d{14}$")]  # YYYYMMDDHHmmss
DT8 = Annotated[str, StringConstraints(pattern=r"^\d{8}$")]    # YYYYMMDD


# =========================================================
# INITIALIZATION
# =========================================================

class Initialization(BaseModel):
    tin: TIN
    bhfId: BHF
    dvcSrlNo: Annotated[str, StringConstraints(min_length=1, max_length=50)]


# =========================================================
# BASIC LIST REQUESTS
# =========================================================

class CodeList(BaseModel):
    tin: TIN
    bhfId: BHF
    lastReqDt: DT14


class BhfList(BaseModel):
    lastReqDt: DT14


class NoticeList(BaseModel):
    tin: TIN
    bhfId: BHF
    lastReqDt: DT14


class TaxpayerInfo(BaseModel):
    tin: TIN
    bhfId: BHF
    lastReqDt: DT14


class CustomerList(BaseModel):
    tin: TIN
    bhfId: BHF
    lastReqDt: DT14


# =========================================================
# BRANCH MANAGEMENT
# =========================================================

class BranchInsurance(BaseModel):
    isrccCd: str
    isrccNm: str
    isrcRt: condecimal(ge=0)
    useYn: YN
    regrNm: str
    regrId: str


class BranchUserAccount(BaseModel):
    userId: str
    userNm: str
    pwd: str
    useYn: YN
    regrNm: str
    regrId: str


class CustomerInfo(BaseModel):
    custNo: str
    custTin: str
    custNm: str
    useYn: YN
    regrNm: str
    regrId: str


# =========================================================
# PURCHASE
# =========================================================

class PurchaseTrns(BaseModel):
    tin: TIN
    bhfId: BHF
    lastReqDt: DT14


class PurchaseItem(BaseModel):
    itemSeq: conint(ge=1)
    itemCd: str
    itemNm: str
    qty: condecimal(gt=0)
    prc: condecimal(ge=0)
    splyAmt: condecimal(ge=0)
    taxTyCd: Annotated[str, StringConstraints(pattern="^[A-E]$")]
    taxblAmt: condecimal(ge=0)
    taxAmt: condecimal(ge=0)
    totAmt: condecimal(ge=0)


class PurchaseTransaction(BaseModel):
    invcNo: conint(ge=1)
    spplrTin: str
    spplrNm: str
    pchsDt: DT8
    totItemCnt: conint(ge=1)
    totTaxblAmt: condecimal(ge=0)
    totTaxAmt: condecimal(ge=0)
    totAmt: condecimal(ge=0)
    regrId: str
    regrNm: str
    itemList: List[PurchaseItem]


# =========================================================
# SALES
# =========================================================

class SalesItem(BaseModel):
    itemSeq: conint(ge=1)
    itemCd: str
    itemClsCd: str
    itemNm: str
    qty: condecimal(gt=0)
    prc: condecimal(ge=0)
    splyAmt: condecimal(ge=0)
    taxTyCd: Annotated[str, StringConstraints(pattern="^[A-E]$")]
    taxblAmt: condecimal(ge=0)
    taxAmt: condecimal(ge=0)
    totAmt: condecimal(ge=0)


class SalesTrns(BaseModel):
    tin: TIN
    bhfId: BHF
    lastReqDt: DT14


class SelectSalesTrns(BaseModel):
    tin: TIN
    bhfId: BHF
    lastReqDt: DT14


class SalesTransaction(BaseModel):
    invcNo: conint(ge=1)
    custTin: str
    custNm: str

    salesTyCd: Annotated[str, StringConstraints(pattern="^[NR]$")]
    rcptTyCd: Annotated[str, StringConstraints(pattern="^[RPC]$")]
    pmtTyCd: Annotated[str, StringConstraints(pattern=r"^\d{2}$")]
    salesSttsCd: Annotated[str, StringConstraints(pattern="^(01|02|03)$")]

    cfmDt: DT14
    salesDt: DT8

    totItemCnt: conint(ge=1)
    totTaxblAmt: condecimal(ge=0)
    totTaxAmt: condecimal(ge=0)
    totAmt: condecimal(ge=0)

    regrId: str
    regrNm: str

    itemList: List[SalesItem]


# =========================================================
# STOCK
# =========================================================

class MoveList(BaseModel):
    tin: TIN
    bhfId: BHF
    lastReqDt: DT14


class StockMaster(BaseModel):
    itemCd: str
    itemNm: str
    useYn: YN
    regrId: str
    regrNm: str


class StockIO(BaseModel):
    itemCd: str
    qty: condecimal(gt=0)
    ioTyCd: Annotated[str, StringConstraints(pattern="^[IO]$")]
    regrId: str
    regrNm: str
