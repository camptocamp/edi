# Copyright 2021 Camptcamp SA
# @author: Simone Orsi <simone.orsi@camptocamp.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import _, api
from odoo.exceptions import UserError

from odoo.addons.component.core import Component

# TODO: add tests


class EDIExchangeSOInput(Component):
    """Process sale orders."""

    _name = "edi.input.sale.order.process"
    _inherit = "edi.component.input.mixin"
    _usage = "input.process.sale.order"

    def process(self):
        wiz = self._setup_wizard()
        res = wiz.import_order_button()
        action_xmlid = res["xml_id"]
        # TODO: I don't really like that we have to check for the action.
        # `sale.order.import` should be refactored w/ proper methods that are reusable.
        if action_xmlid == "sale_order_import.sale_order_import_action":
            raise UserError(_("Sales order has already been imported before"))
        elif action_xmlid == "sale.action_quotations":
            order_id = res["res_id"]
            order = self.env["sale.order"].browse(order_id)
            if self._order_should_be_confirmed():
                order.action_confirm()
            self.exchange_record.sudo()._set_related_record(order)
            return _("Sales order {} created").format(order.name)
        else:
            raise UserError(_("Something went wrong with the importing wizard."))

    def _setup_wizard(self):
        """Init a `sale.order.import` instance for current record."""
        wiz = self.env["sale.order.import"].sudo().create({})
        wiz.order_file = self.exchange_record._get_file_content(binary=False)
        wiz.order_filename = self.exchange_record.exchange_filename
        wiz.order_file_change()
        wiz.price_source = self._get_default_price_source()
        return wiz

    @api.model
    def _get_default_price_source(self):
        return "pricelist"

    def _order_should_be_confirmed(self):
        settings = self.exchange_record.type_id.get_settings()
        return settings.get("sale_order", {}).get("confirm_order")
