from pydantic import ValidationError
from .schemas import *
from .exceptions import ValidationException


SCHEMAS = {
    # INIT
    "initialization": Initialization,

    # BASIC DATA
    "codeList": CodeList,
    "itemClsList": CodeList,
    "bhfList": BhfList,
    "noticeList": NoticeList,
    "taxpayerInfo": TaxpayerInfo,
    "customerList": CustomerList,

    # PURCHASE
    "purchaseTrns": PurchaseTrns,
    "purchaseTransaction": PurchaseTransaction,

    # SALES
    "salesTrns": SalesTrns,
    "selectSalesTrns": SelectSalesTrns,
    "salesTransaction": SalesTransaction,

    # STOCK
    "moveList": MoveList,
    "stockMaster": StockMaster,
    "stockIO": StockIO,

    # BRANCH
    "branchInsurance": BranchInsurance,
    "branchUserAccount": BranchUserAccount,
    "customerInfo": CustomerInfo,
}


class Validator:
    def validate(self, data: dict, schema: str) -> dict:
        if schema not in SCHEMAS:
            raise ValueError(f"Validation schema '{schema}' not defined")

        try:
            return SCHEMAS[schema](**data).dict()
        except ValidationError as e:
            raise ValidationException("Validation failed", e.errors())
