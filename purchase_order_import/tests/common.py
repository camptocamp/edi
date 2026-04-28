# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command, fields
from odoo.tests.common import TransactionCase


class TestOrderResponseImportCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.OrderResponseImport = cls.env["order.response.import.wizard"]
        cls.env.user.company_id.partner_id.vat = "BE0421801233"
        cls.currency_euro = cls.env.ref("base.EUR")
        cls.currency_usd = cls.env.ref("base.USD")
        (cls.currency_euro | cls.currency_usd).action_unarchive()
        cls.product_uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.supplier = cls._create_supplier()
        cls.product_1 = cls._create_product("Product 1", "P1")
        cls.product_2 = cls._create_product("Product 2", "P2")
        cls.purchase_order = cls._create_purchase_order()
        cls.line1 = cls._create_purchase_order_line(
            cls.purchase_order,
            cls.product_1,
            qty=10,
            price_unit=15,
        )
        cls.line2 = cls._create_purchase_order_line(
            cls.purchase_order,
            cls.product_2,
            qty=5,
            price_unit=25,
        )

    @classmethod
    def _create_supplier(cls):
        return cls.env["res.partner"].create(
            {
                "name": "Order Response Supplier",
                "supplier_rank": 1,
                "vat": "BE0477472701",
            }
        )

    @classmethod
    def _create_product(cls, name, product_code):
        return cls.env["product.product"].create(
            {
                "name": name,
                "is_storable": True,
                "seller_ids": [
                    Command.create(
                        {
                            "partner_id": cls.supplier.id,
                            "product_code": product_code,
                        },
                    )
                ],
            }
        )

    @classmethod
    def _create_purchase_order(cls):
        return cls.env["purchase.order"].create(
            {
                "partner_id": cls.supplier.id,
                "date_order": fields.Datetime.now(),
                "date_planned": fields.Datetime.now(),
                "currency_id": cls.currency_euro.id,
            }
        )

    @classmethod
    def _create_purchase_order_line(
        cls,
        order,
        product,
        qty,
        price_unit,
    ):
        return cls.env["purchase.order.line"].create(
            {
                "order_id": order.id,
                "product_id": product.id,
                "name": product.name,
                "date_planned": fields.Datetime.now(),
                "product_qty": qty,
                "product_uom_id": cls.product_uom_unit.id,
                "price_unit": price_unit,
            }
        )

    def _get_base_data(self, **values):
        """Return a normalized parsed order response payload."""
        data = {
            "status": "acknowledgement",
            "company": {"vat": "BE0421801233"},
            "currency": {"iso": "EUR"},
            "date": "2020-02-04",
            "chatter_msg": [],
            "lines": [],
            "note": "Note1\nNote2",
            "time": "22:10:30",
            "supplier": {"vat": "BE0477472701"},
            "ref": str(self.purchase_order.name),
        }
        data.update(values)
        return data

    def _order_line_to_data(
        self,
        order_line,
        qty=None,
        status="accepted",
        backorder_qty=None,
        note=None,
    ):
        """Return parsed order response data for a purchase order line."""
        return {
            "status": status,
            "backorder_qty": backorder_qty,
            "qty": qty if qty is not None else order_line.product_qty,
            "note": note,
            "line_id": str(order_line.id),
            "uom": {"unece_code": order_line.product_uom_id.unece_code},
        }

    def _line_response_data(self, *lines):
        """Return conditional acceptance payload with the provided lines."""
        return self._get_base_data(
            status="conditionally_accepted",
            lines=list(lines),
        )

    def _assert_user_error_message(self, error, expected):
        self.assertEqual(str(error.exception), expected)
