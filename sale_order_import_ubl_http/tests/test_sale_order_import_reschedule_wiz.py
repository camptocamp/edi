# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
import os

import mock

from odoo import exceptions
from odoo.tests.common import SavepointCase


class TestSaleOrderImportController(SavepointCase):
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

    def _search_files(self, domain=None):
        return self.file_model.with_context(active_test=False).search(domain or [])

    def _get_wiz(self, afile):
        return self.env["sale.order.import.http.reschedule.wiz"].create(
            {"file_id": afile.id}
        )

    def _get_job(self, afile):
        job = (
            self.env["sale.order"]
            .with_delay(description="Import UBL order from http")
            .import_ubl_from_http(afile)
        )
        afile.job_id = job.db_record()
        return afile.job_id

    def test_reschedule_file_bad_state(self):
        wiz = self._get_wiz(self.test_file)
        # Has no job, cannot determine state
        with self.assertRaisesRegex(
            exceptions.UserError, "Only failed files can be re-schedule"
        ):
            wiz.action_execute()

        self._get_job(self.test_file)
        wiz.file_id.job_id.ensure_one()
        # Has a job but in not valid state
        with self.assertRaisesRegex(
            exceptions.UserError, "Only failed files can be re-schedule"
        ):
            wiz.action_execute()

    def test_reschedule_file(self):
        self._get_job(self.test_file)
        wiz = self._get_wiz(self.test_file)
        self.assertEqual(wiz.job_channel, "root.ubl_import")
        self.assertEqual(wiz.xml_data, self.test_file_data.decode("utf-8"))
        existing_jobs = self.env["queue.job"].search([])
        existing_files = self._search_files()
        with mock.patch.object(
            type(wiz.file_id), "job_state", new_callable=mock.PropertyMock,
        ) as mocked:
            mocked.return_value = "failed"
            res = wiz.action_execute()

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
        new_file = self._search_files() - existing_files
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
        self.assertNotEqual(new_file.name, self.test_file.name)

        self.assertEqual(
            res,
            {
                "name": "Re-scheduled import job",
                "domain": [("id", "=", new_job.id)],
                "res_model": "queue.job",
                "type": "ir.actions.act_window",
                "view_id": False,
                "view_mode": "tree,form",
                "context": {"tracking_disable": True},
            },
        )
        # TODO: test _mark_done_for_order
