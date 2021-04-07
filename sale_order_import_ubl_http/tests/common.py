# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
import contextlib
import os

from odoo.tests.common import SavepointCase

from odoo.addons.website.tools import MockRequest


class TestSaleOrderImportCommon(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.file_model = cls.env["sale.order.ubl.import.file"]
        path = os.path.join(
            os.path.dirname(__file__), "examples", "UBL-Order-2.0-Example.xml",
        )
        with open(path, "rb") as file:
            cls.test_file_data = file.read()
        cls.test_file = cls.file_model._quick_create(
            cls.test_file_data, "import_ubl_from_http"
        )
        cls.api_user = cls.env.ref("sale_order_import_ubl_http.user_endpoint")
        cls.api_key = cls.env["auth.api.key"].create(
            {"name": "UBL import test", "user_id": cls.api_user.id}
        )

    def _search_files(self, domain=None):
        return self.file_model.with_context(active_test=False).search(domain or [])

    @contextlib.contextmanager
    def _get_mocked_request(self, httprequest=None, extra_headers=None, data=None):
        with MockRequest(self.env) as mocked_request:
            mocked_request.httprequest = httprequest or mocked_request.httprequest
            headers = {}
            headers.update(extra_headers or {})
            mocked_request.httprequest.headers = headers
            mocked_request.httprequest.content_type = "application/xml"
            mocked_request.httprequest.get_data = lambda: data or b""
            mocked_request.auth_api_key_id = self.api_key.id
            yield mocked_request
