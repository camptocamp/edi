# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from odoo import tools

from .common import TestSaleOrderImportCommon


class TestSaleOrderImportEndpoint(TestSaleOrderImportCommon):
    def test_import_so_ubl(self):
        with tools.mute_logger("odoo.addons.queue_job.models.base"):
            res = (
                self.env["sale.order"]
                .with_user(self.api_user)
                .with_context(test_queue_job_no_delay=True)
                .import_ubl_from_http(self.test_file)
            )
        order_ref = res.split(" ")[2]
        new_order = self.env["sale.order"].search([("name", "=", order_ref)], limit=1)
        self.assertEqual(new_order.state, "draft")
