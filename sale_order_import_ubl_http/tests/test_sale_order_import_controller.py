# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from werkzeug.exceptions import BadRequest, Unauthorized

from odoo.addons.queue_job.job import Job
from odoo.addons.sale_order_import_ubl_http.controllers.main import ImportController

from .common import TestSaleOrderImportCommon


class TestSaleOrderImportController(TestSaleOrderImportCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.controller = ImportController()

    def test_invalid_data(self):
        data = "<xml>"
        with self.assertRaises(BadRequest):
            self.controller.check_data_to_import(self.env, data)

    def test_api_key_validity(self):
        """ Check auth key validity."""
        self.controller.check_api_key(self.env, self.api_key.id)
        # Check non existing key
        with self.assertRaises(Unauthorized):
            self.controller.check_api_key(self.env, self.api_key.id + 1)
        # Check key with incorrect user
        self.api_key.user_id = self.env.user.id
        with self.assertRaises(Unauthorized):
            self.controller.check_api_key(self.env, self.api_key.id)

    def test_controller_process_file(self):
        existing_jobs = self.env["queue.job"].search([])
        search_files = self.file_model.with_context(active_test=False).search
        existing_files = search_files([])
        with self._get_mocked_request(data=self.test_file_data):
            res = self.controller.import_sale_order()
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
            self.assertEqual(new_job.state, "pending")
            self.assertTrue(new_file.active)
            Job.load(self.env, new_job.uuid).perform()
            self.assertFalse(new_file.active)
