# Copyright 2022 Camptocamp SA
# @author: Simone Orsi <simahaw@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = [
        "sale.order",
        "edi.state.consumer.mixin",
    ]

    # See data/edi_state.xml
    # order
    EDI_STATE_ORDER_ACCEPTED = "AP"
    EDI_STATE_ORDER_CONDITIONALLY_ACCEPTED = "CA"
    EDI_STATE_ORDER_MSG_ACK = "AB"
    EDI_STATE_ORDER_REJECTED = "RE"
    EDI_STATE_ORDER_LINE_ADDED = "1"
    EDI_STATE_ORDER_LINE_ACCEPTED = "3"
    EDI_STATE_ORDER_LINE_CHANGED = "5"
    EDI_STATE_ORDER_LINE_NOT_ACCEPTED = "7"
    EDI_STATE_ORDER_LINE_ALREADY_DELIVERED = "32"

    # TODO: hook somewhere and call `_edi_set_state`
    def _edi_determine_state(self):
        metadata = self._edi_get_metadata()
        orig_vals = metadata.get("orig_vals", {})
        if not orig_vals.get("lines"):
            return False
        state_code = self._edi_determine_state_code(orig_vals)
        state = self.edi_find_state(code=state_code)
        return state

    def _edi_determine_state_code(self, orig_vals):
        state_code = self._edi_state_code_by_order_state()
        if state_code:
            return state_code
        satisfied = self._edi_compare_orig_values(orig_vals)
        state_code = self.EDI_STATE_ORDER_ACCEPTED
        if not satisfied:
            state_code = self.EDI_STATE_ORDER_CONDITIONALLY_ACCEPTED
        return state_code

    @property
    def _edi_state_code_by_order_state(self):
        return {
            "cancel": self.EDI_STATE_ORDER_REJECTED,
        }

    def _edi_compare_orig_values(self, orig_vals):
        # ATM check only if lines have changes
        for rec in self.order_line:
            if rec.edi_state_id.code == self.EDI_STATE_ORDER_LINE_CHANGED:
                return False
        return True


class SaleOrderLine(models.Model):
    _name = "sale.order.line"
    _inherit = [
        "sale.order.line",
        "edi.auto.exchange.consumer.mixin",
        "edi.id.mixin",
        "edi.state.consumer.mixin",
    ]

    def _edi_determine_state(self):
        metadata = self._edi_get_metadata()
        orig_vals = metadata.get("orig_vals", {})
        line_vals = orig_vals.get("lines", [])
        if not line_vals:
            return False
        state_code = self.order_id.EDI_STATE_ORDER_LINE_ACCEPTED
        satisfied = self._edi_compare_orig_values(line_vals)
        if not satisfied:
            state_code = self.order_id.EDI_STATE_ORDER_LINE_CHANGED
        state = self.order_id.edi_find_state(code=state_code)
        return state

    def _edi_compare_orig_values(self, orig_vals):
        vals_by_edi_id = orig_vals["lines"]
        qty_ok = True
        prod_ok = True
        for line in self.order_line:
            vals = vals_by_edi_id.get(line.edi_id)
            if not vals:
                # TODO: a new line? What do we do?
                continue
            if line.product_uom_qty < vals["product_uom_qty"]:
                qty_ok = False
                break
            if line.product_id.id != vals["product_id"]:
                prod_ok = False
                break
        return qty_ok and prod_ok
