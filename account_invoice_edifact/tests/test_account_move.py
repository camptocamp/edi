# Copyright 2023 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestEdifactInvoice(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.base_edifact_model = cls.env["base.edifact"]
        cls.company = cls.env.ref("base.main_company")
        cls.product1 = cls.env.ref("product.product_product_4")
        cls.product2 = cls.env.ref("product.product_product_1")
        cls.invoice = cls.env["account.move"].create(
            {
                "company_id": cls.company.id,
                "move_type": "out_invoice",
                "partner_id": cls.env.ref(
                    "account_invoice_edifact.partner_edifact_invoiceto_dm"
                ).id,
                "partner_shipping_id": cls.env.ref(
                    "account_invoice_edifact.partner_edifact_shipto_dm"
                ).id,
                "invoice_user_id": cls.env.ref(
                    "account_invoice_edifact.user_edifact_sender_dm"
                ).id,
                "currency_id": cls.company.currency_id.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product1.id,
                            "product_uom_id": cls.product1.uom_id.id,
                            "quantity": 12,
                            "price_unit": 42.42,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product2.id,
                            "product_uom_id": cls.product2.uom_id.id,
                            "quantity": 2,
                            "price_unit": 12.34,
                        },
                    ),
                ],
            }
        )
        cls.invoice.action_post()

    def test_edifact_export_invoice(self):
        edifact_data = self.invoice.edifact_export_invoice()
        self.assertTrue(edifact_data)
        self.assertEqual(isinstance(edifact_data, str), True)

    def test_edifact_export_invoice_interchange(self):
        interchange = self.invoice._edifact_export_invoice_interchange()
        self.assertEqual(interchange.sender, ["9780201379624", "14"])
        self.assertEqual(interchange.recipient, ["9780201379174", "14"])
        self.assertEqual(interchange.syntax_identifier, ["UNOC", "3"])

    def test_edifact_export_invoice_header(self):
        segments = self.invoice._edifact_export_invoice_header()
        seg = ("UNH", "1", ["INVOIC", "D", "96A", "UN", "EAN008"])
        self.assertEqual(segments[0], seg)
        self.assertEqual(len(segments), 30)

    def test_edifact_export_invoice_product(self):
        segments, vals = self.invoice._edifact_export_invoice_product()
        self.assertEqual(len(vals), 2)
        self.assertEqual(len(segments), 24)

    def test_edifact_export_invoice_summary(self):
        vals = {"tax": {0: 533.72}, "total_line_item": 2}
        segments = self.invoice._edifact_export_invoice_summary(vals)
        self.assertEqual(len(segments), 9)
