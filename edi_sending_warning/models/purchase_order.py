# Copyright 2024 Camptocamp
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    sending_warning = fields.Selection(
        selection_add=[("edi_message_not_sent", "EDI Message not sent")]
    )

    @api.depends("sending_warning")
    def _compute_error_in_sending(self):
        super()._compute_error_in_sending()
        for rec in self:
            if not rec.sending_warning and rec.edi_exchange_record_id.state == "output_error_on_send":
                rec.error_in_sending = rec.sending_warning == "edi_message_not_sent"
