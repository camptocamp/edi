# © 2016-2017 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from io import BytesIO

from odoo.tools.pdf import OdooPdfFileReader

from .common import PurchaseOrderUblCommon


class TestUblOrder(PurchaseOrderUblCommon):
    def test_ubl_generate(self):
        ro = self.env["ir.actions.report"]
        rfq_states = self.env["purchase.order"].get_rfq_states()
        for order in self.purchase_orders:
            for version in ["2.0", "2.1"]:
                pdf_file = ro.with_context(
                    ubl_version=version, force_report_rendering=True
                )._render_qweb_pdf("purchase.report_purchase_quotation", order.ids)[0]
                pdf_reader = OdooPdfFileReader(BytesIO(pdf_file), strict=False)
                res = dict(pdf_reader.getAttachments())
                if order.state == "purchase":
                    filename = order.get_ubl_filename("order", version=version)
                    self.assertTrue(filename in res)
                elif order.state in rfq_states:
                    filename = order.get_ubl_filename("rfq", version=version)
                    self.assertTrue(filename in res)
