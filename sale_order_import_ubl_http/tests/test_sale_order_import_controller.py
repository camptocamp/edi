# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
import contextlib
import os

from odoo.tests.common import SavepointCase

from odoo.addons.website.tools import MockRequest

from ..controllers.main import ImportController


class TestSaleOrderImportController(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.api_key = cls.env["auth.api.key"].create(
            {
                "name": "UBL import test",
                "user_id": cls.env.ref("sale_order_import_ubl_http.user_endpoint").id,
            }
        )
        cls.file_model = cls.env["sale.order.ubl.import.file"]

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

    def test_controller_process_file(self):
        path = os.path.join(
            os.path.dirname(__file__), "examples", "UBL-Order-2.0-Example.xml",
        )
        with open(path, "rb") as file:
            data = file.read()
        ctrl = ImportController()
        existing_jobs = self.env["queue.job"].search([])
        search_files = self.file_model.with_context(active_test=False).search
        existing_files = search_files([])
        with self._get_mocked_request(data=data):
            res = ctrl.import_sale_order()
            self.assertEqual(
                res.data, b"Thank you. Your order will be processed, shortly"
            )
            new_job = self.env["queue.job"].search([]) - existing_jobs
            new_job.ensure_one()
            self.assertRecordValues(
                new_job,
                [
                    {
                        "name": "Import UBL order from http",
                        "channel_method_name": "<sale.order>.import_ubl_from_http",
                        "channel": "root.ubl_import",
                    }
                ],
            )
            new_file = search_files([]) - existing_files
            new_file.ensure_one()
            self.assertRecordValues(
                new_file,
                [
                    {
                        "method_name": "import_ubl_from_http",
                        "mimetype": "application/xml",
                        "res_model": "sale.order",
                        "job_id": new_job.id,
                    }
                ],
            )
            self.assertTrue(new_file.name.startswith("UBL-SO-"))
            self.assertTrue(new_file.name.endswith(".xml"))
