# © 2016-2017 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64

from odoo.tests.common import TransactionCase
from odoo.tools import file_open


class TestUblOrderImport(TransactionCase):
    def test_ubl_order_import(self):
        # Modify partner of used purchase order
        self.env.ref("purchase.purchase_order_4").write(
            {"partner_id": self.env.ref("purchase_order_import_ubl.deltapc").id}
        )
        tests = {
            "quote-PO00004.pdf": {
                "po_to_update": self.env.ref("purchase.purchase_order_4"),
                "incoterm": self.env.ref("purchase_order_import_ubl.incoterm_DDU"),
            },
        }
        poio = self.env["purchase.order.import"]
        for filename, res in tests.items():
            po = res["po_to_update"]

            f = file_open("purchase_order_import_ubl/tests/files/" + filename, "rb")
            quote_file = f.read()
            wiz = poio.with_context(
                active_model="purchase.order", active_id=po.id
            ).create(
                {
                    "quote_file": base64.b64encode(quote_file),
                    "quote_filename": filename,
                }
            )
            f.close()
            self.assertEqual(wiz.purchase_id, po)
            wiz.update_rfq_button()
            self.assertEqual(po.incoterm_id, res["incoterm"])
