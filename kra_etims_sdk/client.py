from .base_client import BaseClient
from .validator import Validator


class EtimsClient(BaseClient):

    def __init__(self, config: dict, auth):
        super().__init__(config, auth)
        self.validator = Validator()

    def _validate(self, data: dict, schema: str) -> dict:
        return self.validator.validate(data, schema)

    def select_init_osdc_info(self, data: dict) -> dict:
        """
        Initialize the OSCU device with KRA.
        Returns cmcKey and device information.
        """
        return self.post("selectInitOsdcInfo", self._validate(data, "initialization"))

    # -----------------------------
    # BASIC DATA ENDPOINTS
    # -----------------------------
    def select_code_list(self, data: dict) -> dict:
        return self.post("selectCodeList", self._validate(data, "codeList"))

    def select_item_cls_list(self, data: dict) -> dict:
        return self.post("selectItemClsList", self._validate(data, "itemClsList"))

    def select_bhf_list(self, data: dict) -> dict:
        return self.post("selectBhfList", self._validate(data, "bhfList"))

    def select_notice_list(self, data: dict) -> dict:
        return self.post("selectNoticeList", self._validate(data, "noticeList"))

    def select_taxpayer_info(self, data: dict) -> dict:
        return self.post("selectTaxpayerInfo", self._validate(data, "taxpayerInfo"))

    def select_customer_list(self, data: dict) -> dict:
        return self.post("selectCustomerList", self._validate(data, "customerList"))

    # -----------------------------
    # PURCHASE ENDPOINTS
    # -----------------------------
    def select_purchase_trns(self, data: dict) -> dict:
        return self.post("selectPurchaseTrns", self._validate(data, "purchaseTrns"))

    def send_purchase_transaction_info(self, data: dict) -> dict:
        return self.post(
            "sendPurchaseTransactionInfo",
            self._validate(data, "purchaseTransaction"),
        )

    # -----------------------------
    # SALES ENDPOINTS
    # -----------------------------
    def send_sales_trns(self, data: dict) -> dict:
        return self.post("sendSalesTrns", self._validate(data, "salesTrns"))

    def send_sales_transaction(self, data: dict) -> dict:
        return self.post(
            "sendSalesTransaction",
            self._validate(data, "salesTransaction"),
        )

    def select_sales_trns(self, data: dict) -> dict:
        return self.post("selectSalesTrns", self._validate(data, "selectSalesTrns"))

    # -----------------------------
    # STOCK ENDPOINTS
    # -----------------------------
    def select_move_list(self, data: dict) -> dict:
        return self.post("selectMoveList", self._validate(data, "moveList"))

    def save_stock_master(self, data: dict) -> dict:
        return self.post("saveStockMaster", self._validate(data, "stockMaster"))

    def insert_stock_io(self, data: dict) -> dict:
        return self.post("insertStockIO", self._validate(data, "stockIO"))

    # -----------------------------
    # BRANCH / MANAGEMENT ENDPOINTS
    # -----------------------------
    def branch_insurance_info(self, data: dict) -> dict:
        return self.post(
            "branchInsuranceInfo",
            self._validate(data, "branchInsurance"),
        )

    def branch_user_account(self, data: dict) -> dict:
        return self.post(
            "branchUserAccount",
            self._validate(data, "branchUserAccount"),
        )

    def branch_send_customer_info(self, data: dict) -> dict:
        return self.post(
            "branchSendCustomerInfo",
            self._validate(data, "customerInfo"),
        )

    # -----------------------------
    # ITEM / MASTER DATA
    # -----------------------------
    def save_item(self, data: dict) -> dict:
        return self.post("saveItem", self._validate(data, "item"))
