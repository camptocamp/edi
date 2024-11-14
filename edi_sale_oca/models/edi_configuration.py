# Copyright 2024 Camptocamp SA
# @author: Simone Orsi <simahaw@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class EdiConfiguration(models.Model):
    _inherit = "edi.configuration"

    trigger = fields.Selection(
        selection_add=[
            ("on_edi_sale_order_state_sale", "On SO Confirm"),
            ("on_edi_sale_order_state_quotation_sent", "On SO Quotation Sent"),
            ("on_edi_sale_order_state_cancel", "On SO Cancel"),
            ("on_edi_sale_order_state_done", "On SO Done"),
            ("on_edi_sale_order_state_unlock", "On SO Unlock"),
            ("on_edi_sale_order_state_draft", "On SO reset to draft"),
        ],
        ondelete={
            "on_edi_sale_order_state_sale": "set default",
            "on_edi_sale_order_state_quotation_sent": "set default",
            "on_edi_sale_order_state_cancel": "set default",
            "on_edi_sale_order_state_done": "set default",
            "on_edi_sale_order_state_unlock": "set default",
            "on_edi_sale_order_state_draft": "set default",
        },
    )
