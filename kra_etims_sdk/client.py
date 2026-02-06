from .base_client import BaseClient
from .validator import Validator


class EtimsClient(BaseClient):
    def __init__(self, config: dict, auth):
        super().__init__(config, auth)
        self.validator = Validator()

    def _validate(self, data: dict, schema: str) -> dict:
        return self.validator.validate(data, schema)

    # -----------------------------
    # INITIALIZATION
    # -----------------------------
    def select_init_osdc_info(self, data: dict) -> dict:
        return self.post("selectInitOsdcInfo", self._validate(data, "initialization"))

    # -----------------------------
    # CODE LISTS
    # -----------------------------
    def select_code_list(self, data: dict) -> dict:
        return self.post("selectCodeList", self._validate(data, "lastReqOnly"))

    # -----------------------------
    # CUSTOMER / BRANCH
    # -----------------------------
    def select_customer(self, data: dict) -> dict:
        return self.post("selectCustomer", self._validate(data, "custSearchReq"))

    def select_branches(self, data: dict) -> dict:
        return self.post("selectBhfList", self._validate(data, "lastReqOnly"))

    def save_branch_customer(self, data: dict) -> dict:
        return self.post("saveBhfCustomer", self._validate(data, "branchCustomer"))

    def save_branch_user(self, data: dict) -> dict:
        return self.post("saveBhfUser", self._validate(data, "branchUser"))

    def save_branch_insurance(self, data: dict) -> dict:
        return self.post("saveBhfInsurance", self._validate(data, "branchInsurance"))

    # -----------------------------
    # ITEM
    # -----------------------------
    def select_item_classes(self, data: dict) -> dict:
        return self.post("selectItemClsList", self._validate(data, "lastReqOnly"))

    def select_items(self, data: dict) -> dict:
        return self.post("selectItemList", self._validate(data, "lastReqOnly"))

    def save_item(self, data: dict) -> dict:
        return self.post("saveItem", self._validate(data, "saveItem"))

    def save_item_composition(self, data: dict) -> dict:
        return self.post("SaveItemComposition", self._validate(data, "itemComposition"))

    # -----------------------------
    # IMPORTED ITEMS
    # -----------------------------
    def select_imported_items(self, data: dict) -> dict:
        return self.post("selectImportItemList", self._validate(data, "lastReqOnly"))

    def update_imported_item(self, data: dict) -> dict:
        return self.post("updateImportItem", self._validate(data, "importItemUpdate"))

    # -----------------------------
    # PURCHASES
    # -----------------------------
    def select_purchases(self, data: dict) -> dict:
        return self.post("selectTrnsPurchaseSalesList", self._validate(data, "lastReqOnly"))

    def save_purchase(self, data: dict) -> dict:
        return self.post("insertTrnsPurchase", self._validate(data, "insertTrnsPurchase"))

    def save_sales_transaction(self, data: dict) -> dict:
        return self.post("TrnsSalesSaveWrReq", self._validate(data, "lastReqOnly"))

    # -----------------------------
    # STOCK
    # -----------------------------
    def select_stock_movement(self, data: dict) -> dict:
        return self.post("selectStockMoveList", self._validate(data, "lastReqOnly"))

    def save_stock_io(self, data: dict) -> dict:
        return self.post("insertStockIO", self._validate(data, "saveStockIO"))

    def save_stock_master(self, data: dict) -> dict:
        return self.post("saveStockMaster", self._validate(data, "stockMaster"))

    # -----------------------------
    # NOTICES
    # -----------------------------
    def select_notice_list(self, data: dict) -> dict:
        return self.post("selectNoticeList", self._validate(data, "lastReqOnly"))
