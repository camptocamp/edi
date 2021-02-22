# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    _client_order_ref_separator = " - "

    client_order_ref = fields.Char(
        compute="_compute_client_order_ref",
        string="Customer Reference",
        store=True,
        copy=False,
        readonly=False,
    )
    customer_order_number = fields.Char(string="Customer Order Number", copy=False)
    customer_order_free_ref = fields.Char(string="Customer Free Reference", copy=False)

    @api.depends("customer_order_number", "customer_order_free_ref")
    def _compute_client_order_ref(self):
        for order in self:
            refs = [order.customer_order_number, order.customer_order_free_ref]
            refs = [ref for ref in refs if ref and ref.strip()]
            order.client_order_ref = self._client_order_ref_separator.join(refs)

    def _prepare_invoice(self):
        res = super()._prepare_invoice()
        res["customer_order_number"] = self.customer_order_number
        res["customer_order_free_ref"] = self.customer_order_free_ref
        return res
