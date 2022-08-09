# Copyright 2022 Camptocamp SA
# @author: Simone Orsi <simahaw@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = ["sale.order", "edi.exchange.consumer.mixin"]

    # TODO: this field should be moved to the consumer mixin
    # Each extending module should then override `states` as needed.
    disable_edi_auto = fields.Boolean(
        help="When marked, EDI automatic processing will be avoided",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    # Receiver may send or not the response on create
    # then for each update IF required.
    # https://docs.oasis-open.org/ubl/os-UBL-2.3/UBL-2.3.html#S-ORDERING-POST-AWARD
    # https://docs.peppol.eu/poacc/upgrade-3/profiles/28-ordering
    # /#_response_code_on_header_level

    # TBD: implementing OrdResp for all modifications
    # can be complex to manage (also for the 3rd party).
    # Hence, we could block further modifications w/ sale exceptions
    # and ask the sender to issue a new order request.
    # This approach seems suitable only for orders that do not get processed immediately.
