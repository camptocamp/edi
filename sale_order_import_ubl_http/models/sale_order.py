# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import _, api, models
from odoo.exceptions import UserError

from odoo.addons.queue_job.job import job


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    @job(default_channel="root.invoice_import")
    def import_ubl_from_http(self, data):
        """Job called by the endpoint to import received data."""
        wiz = self.env["sale.order.import"].create({})
        wiz.order_file = str.encode(data)
        wiz.order_filename = "imported_invoice.xml"
        wiz.order_file_change()
        wiz.price_source = self._get_default_price_source()
        res = wiz.sudo().import_order_button()
        action_xmlid = res["xml_id"]
        if action_xmlid == "sale_order_import.sale_order_import_action":
            # TODO: Order has already been imported
            #   there could be more than one to update ?
            return _("Sale order has already been imported before, nothing done.")
        elif action_xmlid == "sale.action_quotations":
            order_id = res["res_id"]
            order = self.env["sale.order"].browse(order_id)
            order.action_confirm()
            return _("Sale order created with id {}").format(order_id)
        else:
            raise UserError(_("Someting went wrong with the importing wizard."))

    @api.model
    def _get_default_price_source(self):
        return "pricelist"
